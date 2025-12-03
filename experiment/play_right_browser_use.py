from playwright.sync_api import sync_playwright
import time

# SETTINGS
# Replace this with the path you found in step 2
# Note: Usually you point to the folder *above* the specific Profile folder
# e.g., if path is ".../Chrome/Profile 2", use ".../Chrome"
USER_DATA_DIR = "/Users/xiaofanlu/Library/Application Support/Google/Chrome"# Then specify which profile folder to use inside the args
PROFILE_DIR_NAME = "Default" 

def ask_gemini(prompt):
    with sync_playwright() as p:
        # Launch Chrome with your logged-in profile
        # headless=False means you will SEE the browser open (easier for debugging)
        context = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False, 
            channel="chrome", # Use your actual installed Chrome
            args=[f"--profile-directory={PROFILE_DIR_NAME}"] 
        )
        
        page = context.pages[0]
        page.goto("https://gemini.google.com/app")

        # 1. FIND THE INPUT BOX
        # Gemini's input box often has a specific role or class. 
        # Using a specialized selector is best.
        input_area = page.get_by_role("textbox") 
        input_area.click()
        input_area.fill(prompt)
        input_area.press("Enter")

        print("Thinking...")

        # 2. WAIT FOR RESPONSE
        # We wait for the "Stop responding" button to disappear, 
        # or for the "Copy" icon to appear at the bottom of the new response.
        # This is a simple wait; production code needs dynamic waiting.
        page.wait_for_timeout(5000) # Initial wait
        
        # Wait until the 'logo-spinning' or loading animation stops
        # A simple trick: wait for the text to stop changing or a specific unique UI element of a finished message.
        # Here we hard wait for demo purposes (adjust based on complexity)
        time.sleep(10) 

        # 3. EXTRACT TEXT
        # Get all response containers, take the last one
        responses = page.locator("app-message-content")
        last_response = responses.last
        text_content = last_response.inner_text()
        
        print("--- GEMINI RESPONSE ---")
        print(text_content)

        # 4. EXTRACT IMAGES (If Gemini generated one)
        images = last_response.locator("img").all()
        if images:
            print(f"--- FOUND {len(images)} IMAGES ---")
            for i, img in enumerate(images):
                src = img.get_attribute("src")
                print(f"Image {i}: {src}")
                # You can perform a download here using standard python requests
                # or page.download logic
        
        # Keep open for a moment to verify
        time.sleep(2)
        context.close()

# Run it
ask_gemini("Generate a python function to calculate fibonacci sequence and draw a diagram of a cat.")