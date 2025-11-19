"""
Single-Thread TTS Pipeline System
==================================

This module implements a simple single-threaded TTS system:
1. TTS Worker Thread: Converts text to audio AND plays it sequentially

This prevents race conditions and memory issues from multi-threading.

Architecture:
    text_queue → [TTS Worker Thread: Generate → Play → Cleanup] → Speaker
"""

import queue
import threading
import numpy as np
import sounddevice as sd
import warnings
import logging
import re
import sys
import gc
import time
from mlx_audio.tts.models.kokoro import KokoroPipeline
from mlx_audio.tts.utils import load_model

# Suppress phonemizer and TTS warnings
warnings.filterwarnings('ignore', category=UserWarning, module='phonemizer')
warnings.filterwarnings('ignore', module='mlx_audio')
logging.getLogger('phonemizer').setLevel(logging.ERROR)

# Configure sounddevice for low latency
sd.default.latency = 'low'
sd.default.blocksize = 2048
sd.default.prime_output_buffers_using_stream_callback = True


class TTSPipeline:
    """Single-threaded TTS pipeline - generates and plays audio sequentially"""

    def __init__(self, model_id='prince-canuma/Kokoro-82M', default_voice='af_heart', idle_timeout=300):
        """
        Initialize the TTS pipeline

        Args:
            model_id: HuggingFace model ID for TTS
            default_voice: Default voice to use for TTS
            idle_timeout: Seconds of inactivity before unloading model (default: 300 = 5 min)
        """
        print("🎤 Loading TTS model (INITIAL)...")
        self.model_id = model_id
        self.model = load_model(model_id)
        self.pipeline = KokoroPipeline(lang_code='a', model=self.model, repo_id=model_id)
        self.default_voice = default_voice
        self.idle_timeout = idle_timeout
        self.last_activity_time = time.time()

        # CRITICAL: Thread lock to prevent multiple model loads
        self.model_lock = threading.Lock()

        # Debug counter to track model loads
        self.model_load_count = 1

        print("✓ TTS model loaded successfully (load count: 1)")

        # Single queue for text to process
        self.text_queue = queue.Queue()

        # Stop event for graceful shutdown
        self.stop_event = threading.Event()

        # Worker threads
        self.tts_worker_thread = None  # Single worker thread
        self.idle_monitor_thread = None

    def unload_model(self):
        """Unload TTS model to free memory (thread-safe)"""
        with self.model_lock:
            if self.model is None:
                return  # Already unloaded
            print("🗑️  Unloading TTS model to free memory...")
            self.model = None
            self.pipeline = None
            gc.collect()  # Force garbage collection
            print("✓ TTS model unloaded, memory freed")

    def _idle_monitor_worker(self):
        """Monitor inactivity and unload model after timeout"""
        print(f"⏱️  Idle monitor started (timeout: {self.idle_timeout}s)")

        while not self.stop_event.is_set():
            time.sleep(30)  # Check every 30 seconds

            if self.model is None:
                continue  # Model already unloaded

            idle_time = time.time() - self.last_activity_time

            if idle_time >= self.idle_timeout:
                # Check if queue is empty
                if self.text_queue.empty():
                    print(f"💤 TTS idle for {int(idle_time)}s, unloading model...")
                    self.unload_model()

        print("⏱️  Idle monitor stopped")

    def sanitize_text(self, text):
        """Clean text for TTS to avoid phonemizer errors"""
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)

        # Remove markdown code blocks and inline code
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        text = re.sub(r'`[^`]+`', '', text)

        # Remove emojis and special unicode characters
        text = re.sub(r'[^\w\s.,!?;:\'-]', '', text)

        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)

        # Remove very short words (likely artifacts)
        text = ' '.join(word for word in text.split() if len(word) > 1 or word in ['I', 'a', 'A'])

        return text.strip()

    def _tts_worker(self):
        """Single worker thread: Generate AND play audio sequentially"""
        print("🎤 TTS worker thread started (single-threaded mode)")

        # Set thread priority on macOS
        try:
            import ctypes
            if sys.platform == 'darwin':
                libc = ctypes.CDLL('/usr/lib/libc.dylib')
                libc.pthread_setname_np(b'TTS_Worker')
        except:
            pass

        while not self.stop_event.is_set():
            audio_chunks = None
            full_audio = None

            try:
                # Get text from queue with timeout
                item = self.text_queue.get(timeout=0.05)

                if item is None:  # Poison pill
                    break

                text, voice, speed = item

                # Skip empty text
                if not text or len(text) < 5:
                    self.text_queue.task_done()
                    continue

                # Reload model if it was unloaded (with thread safety)
                with self.model_lock:
                    if self.model is None or self.pipeline is None:
                        self.model_load_count += 1
                        print(f"🔄 Reloading TTS model (load #{self.model_load_count})...")
                        self.model = load_model(self.model_id)
                        self.pipeline = KokoroPipeline(lang_code='a', model=self.model, repo_id=self.model_id)
                        print(f"✓ TTS model reloaded (total loads: {self.model_load_count})")

                # Update activity time
                self.last_activity_time = time.time()

                # STEP 1: Generate audio
                audio_chunks = []
                for _, _, audio in self.pipeline(text, voice=voice, speed=speed):
                    if self.stop_event.is_set():
                        break
                    audio_chunks.append(audio[0])

                if not audio_chunks or self.stop_event.is_set():
                    self.text_queue.task_done()
                    continue

                # STEP 2: Concatenate
                full_audio = np.concatenate(audio_chunks, axis=0)

                # STEP 3: Delete chunks immediately
                del audio_chunks
                audio_chunks = None
                gc.collect()

                # STEP 4: Play audio (blocking - wait until done)
                sd.play(
                    full_audio,
                    samplerate=24000,
                    blocksize=2048,
                    blocking=True
                )
                sd.wait()  # Wait for playback to complete
                sd.stop()  # Explicitly stop and release buffers

                # STEP 5: Delete audio array immediately after playback
                del full_audio
                full_audio = None

                # STEP 6: Force garbage collection
                gc.collect()

                self.text_queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                print(f"⚠️ TTS worker error: {e}")
                import traceback
                traceback.print_exc()
                try:
                    # Clean up on error
                    if audio_chunks is not None:
                        del audio_chunks
                    if full_audio is not None:
                        del full_audio
                    gc.collect()
                    self.text_queue.task_done()
                except:
                    pass

        print("🎤 TTS worker thread stopped")

    def start(self):
        """Start TTS worker thread and idle monitor"""
        # Start single TTS worker thread
        if self.tts_worker_thread is None or not self.tts_worker_thread.is_alive():
            self.tts_worker_thread = threading.Thread(
                target=self._tts_worker,
                daemon=True,
                name='TTS-Worker'
            )
            self.tts_worker_thread.start()

        # Start idle monitor thread
        if self.idle_monitor_thread is None or not self.idle_monitor_thread.is_alive():
            self.idle_monitor_thread = threading.Thread(
                target=self._idle_monitor_worker,
                daemon=True,
                name='TTS-IdleMonitor'
            )
            self.idle_monitor_thread.start()

        print("✓ TTS pipeline started (single-threaded mode)")

    def queue_text(self, text, voice=None, speed=1.1):
        """
        Public API: Add text to generation queue

        Args:
            text: Text to convert to speech
            voice: Voice to use (defaults to default_voice)
            speed: Speed multiplier (default 1.1)
        """
        cleaned_text = self.sanitize_text(text)

        # Only queue if text is substantial enough (at least 10 characters)
        if cleaned_text and len(cleaned_text) >= 10:
            v = voice if voice else self.default_voice
            self.text_queue.put((cleaned_text, v, speed))
            # Update activity time when new text is queued
            self.last_activity_time = time.time()

    def stop(self):
        """Stop TTS worker thread gracefully"""
        print("🛑 Stopping TTS pipeline...")
        self.stop_event.set()

        # Send poison pill
        self.text_queue.put(None)

        # Wait for threads to finish
        if self.tts_worker_thread:
            self.tts_worker_thread.join(timeout=2)
        if self.idle_monitor_thread:
            self.idle_monitor_thread.join(timeout=2)

        print("✓ TTS pipeline stopped")

    def wait_until_done(self):
        """Wait until all queued text has been spoken"""
        self.text_queue.join()


# Global instance (singleton pattern)
_tts_pipeline = None
_tts_pipeline_lock = threading.Lock()


def get_tts_pipeline():
    """Get or create the global TTS pipeline instance (thread-safe singleton)"""
    global _tts_pipeline

    # Double-checked locking for thread safety
    if _tts_pipeline is None:
        with _tts_pipeline_lock:
            # Check again inside lock
            if _tts_pipeline is None:
                print("🎤 Creating TTS pipeline singleton...")
                _tts_pipeline = TTSPipeline()
                _tts_pipeline.start()

    return _tts_pipeline


def queue_tts(text, voice=None, speed=1.1):
    """Convenience function to queue text for TTS"""
    pipeline = get_tts_pipeline()
    pipeline.queue_text(text, voice, speed)


def stop_tts():
    """Stop the TTS pipeline"""
    global _tts_pipeline
    if _tts_pipeline:
        _tts_pipeline.stop()
        _tts_pipeline = None


def wait_tts_done():
    """Wait until all TTS playback is complete"""
    global _tts_pipeline
    if _tts_pipeline:
        _tts_pipeline.wait_until_done()


# Auto-start DISABLED to save memory
# TTS pipeline will only load when actually used
# if __name__ != "__main__":
#     get_tts_pipeline()
