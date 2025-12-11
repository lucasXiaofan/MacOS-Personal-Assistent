
import os
import time
import base64
import json
import pyautogui
from openai import OpenAI
from PIL import ImageGrab
import io
import dotenv

# Load environment variables
dotenv.load_dotenv()

# --- CONFIGURATION ---
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Choose a model that supports tool use. 
# Use a capable model for computer use
MODEL_ID = "anthropic/claude-haiku-4.5" # can do the task
# MODEL_ID="x-ai/grok-4.1-fast"
# MODEL_ID="qwen/qwen3-vl-235b-a22b-instruct"

# Safety Failsafe
pyautogui.FAILSAFE = True 

# --- SCREEN SCALER ---
# We need to map the AI's coordinate space (resized image) to the User's screen space (pyautogui points).
# 1. Get actual screen points
SCREEN_W, SCREEN_H = pyautogui.size()
# 2. Get screenshot pixels (on Retina, this is often 2x the points)
_test_img = ImageGrab.grab()
IMG_W, IMG_H = _test_img.size
# 3. Calculate the dimensions the AI sees (thumbnail 1280x1280)
_test_img.thumbnail((1280, 1280))
AI_W, AI_H = _test_img.size

print(f"🔧 Screen Config: PyAutoGUI=({SCREEN_W}x{SCREEN_H}), RawShot=({IMG_W}x{IMG_H}), AI_View=({AI_W}x{AI_H})")
print(f"🔧 Scaling: X_Factor={SCREEN_W/AI_W:.3f}, Y_Factor={SCREEN_H/AI_H:.3f}")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    default_headers={
        "HTTP-Referer": "https://localhost",
        "X-Title": "LocalComputerAgent",
    },
)

def get_screenshot_b64():
    """Captures the screen and returns a base64 encoded JPEG."""
    screenshot = ImageGrab.grab()
    screenshot = screenshot.convert("RGB")
    # Must match the logic used in calculations
    screenshot.thumbnail((1280, 1280)) 
    
    buffer = io.BytesIO()
    screenshot.save(buffer, format="JPEG", quality=70)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

import subprocess
import time
import pyautogui

# --- HELPER ---
def run_applescript(script):
    """Runs a dedicated AppleScript command."""
    try:
        result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
        if result.returncode != 0:
            return False, result.stderr
        return True, result.stdout.strip()
    except Exception as e:
        return False, str(e)

# --- TOOLS ---

def move_mouse(x, y):
    """Moves the mouse to the specified (x, y) coordinates."""
    try:
        x_ai = int(x)
        y_ai = int(y)
        
        # Scale to screen points
        x_real = x_ai * (SCREEN_W / AI_W)
        y_real = y_ai * (SCREEN_H / AI_H)
        
        pyautogui.moveTo(x_real, y_real, duration=0.5)
        return f"Moved mouse to ({x_ai}, {y_ai}) [Screen: {int(x_real)}, {int(y_real)}]"
    except Exception as e:
        return f"Failed to move mouse: {e}"

def click_mouse(button="left"):
    """Clicks the mouse button (left, right, or middle)."""
    try:
        pyautogui.click(button=button)
        return f"Clicked {button} mouse button"
    except Exception as e:
        return f"Failed to click: {e}"

def type_text(text):
    """Types text using macOS System Events (more reliable focus handling)."""
    try:
        # Escape backslashes and double quotes for AppleScript
        safe_text = text.replace("\\", "\\\\").replace('"', '\\"')
        
        script = f'''
        tell application "System Events"
            keystroke "{safe_text}"
        end tell
        '''
        success, output = run_applescript(script)
        if not success:
            return f"Failed to type: {output}"
        return f"Typed: {text}"
    except Exception as e:
        return f"Failed to type: {e}"

def press_hotkey(keys):
    """Presses hotkeys using macOS System Events."""
    try:
        # Map common keys to AppleScript syntax if needed, strictly simpler for now
        # keys is list like ['command', 't']
        
        # Build the modifiers string
        modifiers = []
        key_to_press = ""
        
        for k in keys:
            k = k.lower()
            if k == 'command' or k == 'cmd':
                modifiers.append('command down')
            elif k == 'shift':
                modifiers.append('shift down')
            elif k == 'option' or k == 'alt':
                modifiers.append('option down')
            elif k == 'control' or k == 'ctrl':
                modifiers.append('control down')
            elif k == 'enter' or k == 'return':
                key_to_press = "return"
            elif k == 'space':
                key_to_press = "space"
            else:
                key_to_press = k
        
        if not key_to_press:
            return "Error: No valid key found to press."

        if modifiers:
            mod_string = ", ".join(modifiers)
            script = f'''
            tell application "System Events"
                keystroke "{key_to_press}" using {{{mod_string}}}
            end tell
            '''
        else:
            # Special handling for special keys if needed, but keystroke works for chars
            if key_to_press in ["return", "space", "tab"]:
                script = f'''
                tell application "System Events"
                    key code {{
                        "return": 36,
                        "space": 49,
                        "tab": 48
                    }}'s {key_to_press}
                end tell
                '''
                # Actually simpler: 'keystroke return' works usually, or use code
                if key_to_press == "return": script = 'tell application "System Events" to key code 36'
                if key_to_press == "space": script = 'tell application "System Events" to key code 49'
                if key_to_press == "tab": script = 'tell application "System Events" to key code 48'
            else:
                script = f'''
                tell application "System Events"
                    keystroke "{key_to_press}"
                end tell
                '''

        success, output = run_applescript(script)
        if not success:
            return f"Failed to press hotkey: {output}"
        
        time.sleep(0.5)
        return f"Pressed hotkey: {'+'.join(keys)}"
    except Exception as e:
        return f"Failed to press hotkey: {e}"

def open_app(app_name):
    """Opens/Activates an application using macOS 'activate'."""
    try:
        script = f'''
        tell application "{app_name}"
            activate
        end tell
        '''
        success, output = run_applescript(script)
        if not success:
            # Fallback to subprocess open which is also robust
            subprocess.run(["open", "-a", app_name])
            return f"Opened {app_name} (via fallback)"
            
        time.sleep(2.0) # Wait for window to appear
        return f"Activated application: {app_name}"
    except Exception as e:
        return f"Failed to open app: {e}"

def wait(seconds):
    """Waits for a specified number of seconds."""
    time.sleep(float(seconds))
    return f"Waited for {seconds} seconds"

def terminate(status, reason):
    """Terminates the task."""
    print(f"TERMINATING: [{status}] {reason}")
    return f"Terminated with {status}: {reason}"

tools = [
    {
        "type": "function",
        "function": {
            "name": "move_mouse",
            "description": "Moves the mouse to specific X,Y coordinates. The screen is 1280x1280 (scaled).",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {"type": "integer", "description": "X coordinate"},
                    "y": {"type": "integer", "description": "Y coordinate"}
                },
                "required": ["x", "y"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "click_mouse",
            "description": "Clicks the mouse at the current location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "button": {"type": "string", "enum": ["left", "right", "middle"], "default": "left"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "type_text",
            "description": "Types text at the current cursor location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "The text to type"}
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "press_hotkey",
            "description": "Presses a hotkey combination (e.g. ['command', 'space']). Use for system shortcuts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "keys": {
                        "type": "array", 
                        "items": {"type": "string"},
                        "description": "List of keys to press together, e.g. ['command', 'space']"
                    }
                },
                "required": ["keys"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_app",
            "description": "Opens a macOS application by name (e.g. 'Google Chrome', 'Calculator'). Use this INSTEAD of Spotlight.",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Name of the application"}
                },
                "required": ["app_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "wait",
            "description": "Waits for a period of time. Use this when a page is loading or an animation is playing.",
            "parameters": {
                "type": "object",
                "properties": {
                    "seconds": {"type": "number", "description": "Seconds to wait"}
                },
                "required": ["seconds"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "terminate",
            "description": "Ends the task. Use this when the objective is achieved OR if an unrecoverable error occurs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["success", "failure"]},
                    "reason": {"type": "string", "description": "Reason for termination"}
                },
                "required": ["status", "reason"]
            }
        }
    }
]

def run_agent(objective):
    print(f"🎯 Objective: {objective}")
    print("⏳ Starting in 3s... (Move mouse to corner to abort)")
    time.sleep(3)

    messages = [
        {
            "role": "system",
            "content": """You are a computer control agent. 
            RULES:
            1. TO OPEN APPS: ALWAYS use the open_app("App Name") tool. DO NOT use Spotlight or keyboard shortcuts to open apps.
            2. To click, use move_mouse first, then click_mouse.
            3. The screen is 1280x1280. 
            4. If you need to search in a browser, open the browser first using open_app, wait, then press command+t or command+l."""
        },
        {
            "role": "user",
            "content": f"Objective: {objective}"
        }
    ]

    step_count = 0
    max_steps = 30

    while step_count < max_steps:
        step_count += 1
        print(f"\n--- Step {step_count} ---")

        # 1. Capture Vision
        try:
            # Get current mouse position and scale to AI view
            cur_x, cur_y = pyautogui.position()
            
            # Get actual screen dimensions
            SCREEN_W, SCREEN_H = pyautogui.size()
            AI_W = 1280
            AI_H = 1280

            ai_cur_x = int(cur_x * (AI_W / SCREEN_W))
            ai_cur_y = int(cur_y * (AI_H / SCREEN_H))
            
            # Capture for AI
            screenshot = ImageGrab.grab()
            screenshot = screenshot.convert("RGB")
            
            # Save debug screenshot for user
            screenshot.save(f"debug_step_{step_count}.jpg", "JPEG")
            print(f"   (Saved debug_step_{step_count}.jpg)")

            # Must match the logic used in calculations
            screenshot.thumbnail((1280, 1280)) 
            buffer = io.BytesIO()
            screenshot.save(buffer, format="JPEG", quality=70)
            b64_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
        except Exception as e:
            print(f"❌ Screenshot Error: {e}")
            break
        
        # Add screenshot to the message history as a new user message
        user_content = [
            {
                "type": "text",
                "text": f"Current screen state. Current Mouse Position: ({ai_cur_x}, {ai_cur_y})"
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{b64_image}"
                }
            }
        ]
        
        messages.append({"role": "user", "content": user_content})

        try:
            response = client.chat.completions.create(
                model=MODEL_ID,
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )
        except Exception as e:
            print(f"❌ API Error: {e}")
            break

        msg = response.choices[0].message
        print(f"🤖 AI: {msg.content or '(Tool Call)'}")
        
        messages.append(msg)

        if msg.tool_calls:
            for tool_call in msg.tool_calls:
                func_name = tool_call.function.name
                try:
                    args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    print(f"   -> Error parsing JSON arguments: {tool_call.function.arguments}")
                    args = {}

                print(f"   -> Call {func_name}({args})")
                
                result = None
                
                # Robust Argument Handling
                if func_name == "move_mouse":
                    x = args.get("x")
                    y = args.get("y")
                    # Handle case where model puts "x, y" in x
                    if isinstance(x, str) and "," in x and y is None:
                        try:
                            parts = x.split(",")
                            x = int(parts[0].strip())
                            y = int(parts[1].strip())
                        except:
                            pass
                    # Handle single string case if passed as "x,y"
                    if y is None and isinstance(x, str):
                         # Try to parse or just fail gracefully
                         pass
                         
                    if x is not None and y is not None:
                        result = move_mouse(x, y)
                    else:
                        result = "Error: Missing x or y coordinates"

                elif func_name == "click_mouse":
                    # Check if 'x' is here by mistake (some models do click(x,y))
                    if "x" in args and "y" in args:
                         move_mouse(args["x"], args["y"])
                    result = click_mouse(args.get("button", "left"))
                    
                elif func_name == "type_text":
                    result = type_text(args.get("text", ""))
                    
                elif func_name == "press_hotkey":
                    result = press_hotkey(args.get("keys", []))

                elif func_name == "open_app":
                    result = open_app(args.get("app_name"))
                    
                elif func_name == "wait":
                    result = wait(args.get("seconds", 1))
                    
                elif func_name == "terminate":
                    result = terminate(args.get("status", "unknown"), args.get("reason", ""))
                    if args.get("status") == "success":
                        print("✅ Task Completed!")
                    else:
                        print("❌ Task Failed.")
                    return # Exit the loop and function

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })
        else:
            # If no tool calls, just continue. 
            pass
            
        time.sleep(1) 

if __name__ == "__main__":
    run_agent("open app with open_app, open google chrome, if there is luffy image on gemini page move mouse on the image right click, click copy image, then open obsidian, and paste the image.")