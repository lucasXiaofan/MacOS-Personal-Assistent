# macOS Launch Agents & Screen Capture Guide

This report details how to create and manage macOS Launch Agents (`.plist` files) and explains why background scripts often fail to capture screen content (resulting in only the desktop wallpaper being visible).

## 1. Creating a Launch Agent (`.plist`)

A **Launch Agent** is a background process that runs on behalf of the logged-in user. It is defined by a Property List (XML) file located in `~/Library/LaunchAgents/`.

### Basic Structure
Here is a standard template for a Launch Agent that runs a Python script:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <!-- Unique Label for the job -->
    <key>Label</key>
    <string>com.username.myscript</string>

    <!-- Command to execute -->
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/username/path/to/script.py</string>
    </array>

    <!-- Run immediately when loaded (login) -->
    <key>RunAtLoad</key>
    <true/>

    <!-- Keep running? (Daemon-like behavior) -->
    <key>KeepAlive</key>
    <true/>

    <!-- Logging -->
    <key>StandardOutPath</key>
    <string>/Users/username/path/to/logs/output.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/username/path/to/logs/error.log</string>
    
    <!-- Environment Variables (Optional) -->
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
</dict>
</plist>
```

### Setup Steps
1.  **Create the file**: Save the XML above as `~/Library/LaunchAgents/com.username.myscript.plist`.
2.  **Set Permissions**: Ensure the file is owned by you and has correct permissions:
    ```bash
    chmod 644 ~/Library/LaunchAgents/com.username.myscript.plist
    ```

## 2. Essential Commands

Once your `.plist` file is created, you manage it using `launchctl`.

| Action | Command |
| :--- | :--- |
| **Load (Start)** | `launchctl load ~/Library/LaunchAgents/com.username.myscript.plist` |
| **Unload (Stop)** | `launchctl unload ~/Library/LaunchAgents/com.username.myscript.plist` |
| **Reload (Restart)** | Unload then Load (see above) |
| **Check Status** | `launchctl list | grep com.username.myscript` |
| **Validate Syntax** | `plutil -lint ~/Library/LaunchAgents/com.username.myscript.plist` |

**Note**: If you change the `.plist` file, you **must** unload and reload it for changes to take effect.

## 3. The "Desktop Background Only" Screenshot Issue

### The Problem
When your script runs via `launchctl`, screenshots taken using `screencapture` or Python libraries (like `PIL.ImageGrab` or `pyautogui`) often show **only the desktop wallpaper**, ignoring all open windows.

### The Cause: macOS Privacy (TCC)
This is a security feature of macOS (Transparency, Consent, and Control - TCC).
1.  **Context**: Launch Agents run in a background context that is separate from your interactive terminal session.
2.  **Permissions**: "Screen Recording" permission is granted to **applications** (like Terminal.app, VS Code, or Python.app).
3.  **The Disconnect**: When `launchd` starts your script, it spawns a process (e.g., `/usr/bin/python3` or `/bin/sh`). If *that specific binary* does not have Screen Recording permission, macOS blocks it from seeing window contents to prevent spyware.

### The Solution

You must grant "Screen Recording" permission to the **specific executable** running your script.

#### Method 1: Add the Interpreter to Permissions (Harder)
You need to add the exact binary running your script to **System Settings > Privacy & Security > Screen Recording**.
1.  Find the path: `which python3` (or your specific venv python).
2.  Open System Settings.
3.  Click `+` and press `Cmd+Shift+G` to paste the path to the python binary.
4.  **Restart** the Launch Agent.

*Note: This often fails because `launchd` might spawn `sh` or `bash` first, or the permission doesn't propagate correctly to child processes in background mode.*

#### Method 2: The "App Wrapper" (Recommended)
The most reliable way is to wrap your script in a simple macOS Application (`.app`). macOS handles permissions for `.app` bundles much better than raw binaries.

1.  **Open Automator** (built-in macOS app).
2.  Choose **"Application"** as the document type.
3.  Add the action **"Run Shell Script"**.
4.  Paste your command:
    ```bash
    /path/to/your/venv/bin/python /path/to/your/script.py
    ```
5.  Save it as `MyBackgroundHandler.app` in your Applications folder.
6.  **Run the App manually once**. macOS will prompt: *"MyBackgroundHandler would like to record this computer's screen."*
7.  Click **"Open System Settings"** and grant permission.
8.  Update your `.plist` to launch the **App** instead of the script:
    ```xml
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/open</string>
        <string>-W</string>
        <string>/Applications/MyBackgroundHandler.app</string>
    </array>
    ```

This ensures the process has a proper bundle ID and persistent permissions.
