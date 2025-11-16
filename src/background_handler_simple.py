"""
Simple Background Handler with Two Shortcuts

Shortcut 1 (Cmd+Shift+T): Text input → Classify → Append
Shortcut 2 (Cmd+Shift+4): Screenshot → Text input → Classify → Append with image
"""

import os
import base64
import threading
import queue
import subprocess
import logging
from pynput import keyboard
from pync import Notifier
import rumps
from simple_classifier import shortcut_text, shortcut_screenshot

# Suppress pynput keyboard errors (F11/F12 volume keys cause KeyError)
logging.getLogger('pynput').setLevel(logging.CRITICAL)
logging.getLogger('pynput.keyboard').setLevel(logging.CRITICAL)


class SimpleBackgroundHandler(rumps.App):
    """Background handler with two shortcuts"""

    def __init__(self):
        super().__init__("📝")
        self.avatar_path = os.path.abspath(
            "/Users/xiaofanlu/Documents/github_repos/hackathon-umass/avatars/melina 2/melina-cute-256.png"
        )

        # Queues for both shortcuts
        self.text_queue = queue.Queue()
        self.screenshot_queue = queue.Queue()

        # Start hotkey listeners
        self.start_hotkeys()

        # Timer to check queues
        self.timer = rumps.Timer(self.check_queues, 0.1)
        self.timer.start()

        self.notify("Ready", "Cmd+Shift+E: Note | Cmd+Shift+4: Screenshot")
        print("✅ Shortcuts ready:")
        print("   Cmd+Shift+E: Quick text note (type 'C' for 40min timer)")
        print("   Cmd+Shift+4: Regional screenshot + comment")

    def start_hotkeys(self):
        """Start both hotkey listeners with error suppression for volume keys"""

        def on_text_shortcut():
            """Shortcut 1: Text input"""
            try:
                print("\n🔤 TEXT SHORTCUT PRESSED!")
                self.text_queue.put(True)
            except Exception as e:
                print(f"⚠️  Text shortcut error: {e}")

        def on_screenshot_shortcut():
            """Shortcut 2: Screenshot (Cmd+Shift+4)"""
            try:
                print("\n📸 SCREENSHOT SHORTCUT PRESSED!")
                screenshot = self.capture_screenshot()
                if screenshot:  # Only queue if user didn't cancel
                    self.screenshot_queue.put(screenshot)
                else:
                    print("Screenshot cancelled by user")
            except Exception as e:
                print(f"⚠️  Screenshot error: {e}")

        # Create hotkey listener with custom error suppression
        hotkey = keyboard.GlobalHotKeys({
            '<cmd>+<shift>+e': on_text_shortcut,
            '<cmd>+<shift>+4': on_screenshot_shortcut
        })

        # Monkey-patch the _on_press to suppress KeyError from volume keys
        original_on_press = hotkey._on_press

        def safe_on_press(key):
            """Wrapper that suppresses KeyError from unhandled keys"""
            try:
                return original_on_press(key)
            except KeyError:
                # Silently ignore keys not in our hotkey map (F11/F12/etc)
                pass
            except Exception as e:
                print(f"⚠️  Key handler error: {e}")

        hotkey._on_press = safe_on_press

        # Start listener in background thread
        threading.Thread(target=hotkey.start, daemon=True).start()

    def check_queues(self, _):
        """Check both queues on main thread"""

        # Check text queue
        try:
            self.text_queue.get_nowait()
            print("💬 Showing text input dialog...")
            text = self.show_input_dialog("Enter your notes:")
            if text and text.strip():
                self.process_text(text)
        except queue.Empty:
            pass

        # Check screenshot queue
        try:
            screenshot = self.screenshot_queue.get_nowait()
            print("💬 Showing screenshot comment dialog...")
            comment = self.show_input_dialog("Add comment for screenshot (optional):")
            self.process_screenshot(screenshot, comment)
        except queue.Empty:
            pass

    def show_input_dialog(self, prompt_text):
        """Show AppleScript input dialog"""
        applescript = f'''
        set userInput to text returned of (display dialog "{prompt_text}" default answer "" buttons {{"Cancel", "OK"}} default button "OK")
        return userInput
        '''

        try:
            result = subprocess.run(
                ['osascript', '-e', applescript],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes
            )

            if result.returncode == 0:
                return result.stdout.strip()
            return None

        except Exception as e:
            print(f"❌ Dialog error: {e}")
            return None

    def capture_screenshot(self):
        """Capture regional screenshot (like Cmd+Shift+4) and return base64"""
        import tempfile
        import time

        # Create temp file
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        temp_path = temp_file.name
        temp_file.close()

        try:
            # Use macOS screencapture with interactive selection (-i)
            subprocess.run(['screencapture', '-i', temp_path], check=True)

            # Small delay to ensure file is written
            time.sleep(0.1)

            # Check if user cancelled (file will be empty or very small)
            if os.path.getsize(temp_path) < 100:
                return None

            # Read and encode
            with open(temp_path, 'rb') as f:
                img_bytes = f.read()

            # Copy to clipboard using pbcopy
            try:
                proc = subprocess.Popen(
                    ['osascript', '-e', f'set the clipboard to (read (POSIX file "{temp_path}") as «class PNGf»)'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                proc.wait()
                print("📋 Screenshot copied to clipboard")
            except Exception as e:
                print(f"⚠️  Clipboard copy failed: {e}")

            img_base64 = base64.b64encode(img_bytes).decode('utf-8')
            return img_base64

        except subprocess.CalledProcessError:
            # User cancelled
            return None
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def process_text(self, text):
        """Process text shortcut"""
        threading.Thread(
            target=self._process_text_async,
            args=(text,),
            daemon=True
        ).start()

    def _process_text_async(self, text):
        """Async text processing with timer shortcuts"""
        try:
            # Check for timer shortcuts (C = 40min countdown)
            if text.strip().upper() == 'C':
                print("⏱️  Starting 40-minute countdown...")
                self.start_countdown_timer(40, "Focus Session")
                self.notify("⏱️ 40-min countdown started", "Check menu bar")
                return

            # Check for S shortcut (25min Pomodoro)
            if text.strip().upper() == 'S':
                print("⏱️  Starting 25-minute Pomodoro...")
                self.start_countdown_timer(25, "Pomodoro")
                self.notify("⏱️ 25-min countdown started", "Check menu bar")
                return

            # Normal text processing
            self.notify("Processing...", text[:50])
            result = shortcut_text(text)
            self.notify("✅ Saved", f"{result['target']}")

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            self.notify("Error", str(e))

    def process_screenshot(self, screenshot_base64, comment):
        """Process screenshot shortcut"""
        threading.Thread(
            target=self._process_screenshot_async,
            args=(screenshot_base64, comment),
            daemon=True
        ).start()

    def _process_screenshot_async(self, screenshot_base64, comment):
        """Async screenshot processing"""
        try:
            self.notify("Processing screenshot...", comment[:50] if comment else "")
            result = shortcut_screenshot(screenshot_base64, comment or "")
            self.notify("✅ Saved", f"{result['target']}: {result['file']}")

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            self.notify("Error", str(e))

    def start_countdown_timer(self, duration_minutes, session_name):
        """Start countdown timer in menu bar"""
        timer_script = os.path.join(os.path.dirname(__file__), "menubar_timer.py")
        motivation = "Stay focused!"

        try:
            subprocess.Popen([
                "python3",
                timer_script,
                str(duration_minutes),
                session_name,
                motivation
            ], start_new_session=True)
            print(f"✅ Timer started: {duration_minutes} minutes")
        except Exception as e:
            print(f"❌ Timer error: {e}")

    def notify(self, message, title="Classifier"):
        """Send notification with subtle sound"""
        try:
            Notifier.notify(
                message,
                title=title,
                contentImage=self.avatar_path if os.path.exists(self.avatar_path) else None,
                sound="Tink"  # Subtle, natural sound
            )
        except Exception as e:
            print(f"⚠️  Notification failed: {e}")


def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║         📝 SIMPLE CLASSIFIER SHORTCUTS                   ║
╚══════════════════════════════════════════════════════════╝

Shortcuts:
1. Cmd+Shift+E  → Quick text note
                  (type 'C' for 40min timer, 'S' for 25min timer)
2. Cmd+Shift+4  → Regional screenshot + comment

Starting...
""")
    SimpleBackgroundHandler().run()


if __name__ == "__main__":
    main()
