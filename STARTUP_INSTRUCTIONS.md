# How to Run Background Handler on Startup

## Quick Commands

### Stop the script:
```bash
launchctl unload ~/Library/LaunchAgents/com.classifier.background.plist
```

### Start/Restart the script:
```bash
launchctl unload ~/Library/LaunchAgents/com.classifier.background.plist
launchctl load ~/Library/LaunchAgents/com.classifier.background.plist
```

### Check if it's running:
```bash
launchctl list | grep classifier
# Output should show: PID 0 com.classifier.background (0 = success)
```

---

## First-Time Setup

### 1. Grant Accessibility Permissions (REQUIRED)

**The keyboard shortcuts won't work without this!**

1. Open **System Settings** → **Privacy & Security** → **Accessibility**
2. Click the **+** button (or lock icon to unlock)
3. Press **Cmd+Shift+G** and navigate to:
   ```
   /Users/xiaofanlu/Documents/github_repos/hackathon-umass/.venv/bin/python3
   ```
4. Add it and enable the checkbox

### 2. Start the LaunchAgent:

```bash
launchctl load ~/Library/LaunchAgents/com.classifier.background.plist
```

### 3. Verify it's running:

```bash
launchctl list | grep classifier
```

### 4. Check logs (if needed):

```bash
tail -f ~/Documents/github_repos/hackathon-umass/logs/background_handler.log
tail -f ~/Documents/github_repos/hackathon-umass/logs/background_handler.error.log
```

---

## Manual Startup (Alternative)

If you prefer to start manually (for debugging):

```bash
cd ~/Documents/github_repos/hackathon-umass
uv run src/background_handler_simple.py
```

---

## Shortcuts Available:

1. **Cmd+Shift+E** → Quick text note
   - Type 'C' for 40min timer
   - Type 'S' for 25min timer

2. **Cmd+Shift+4** → Regional screenshot + comment
   - Automatically copies to clipboard
   - You can paste with Cmd+V anywhere

---

## Troubleshooting:

### Shortcuts don't work:
**Most common issue:** Missing Accessibility permissions
1. Open **System Settings** → **Privacy & Security** → **Accessibility**
2. Make sure Python has accessibility permissions:
   ```
   /Users/xiaofanlu/Documents/github_repos/hackathon-umass/.venv/bin/python3
   ```
3. Restart the LaunchAgent after granting permission

### Script keeps crashing:
```bash
# Check error logs
tail -20 ~/Documents/github_repos/hackathon-umass/logs/background_handler.error.log

# Common errors:
# - "ModuleNotFoundError" → Run: uv sync
# - "Operation not permitted" → Grant Accessibility permissions
# - "This process is not trusted" → Grant Accessibility permissions
```

### Kill all running instances:
```bash
pkill -f background_handler_simple
```

### Start manually for debugging:
```bash
cd ~/Documents/github_repos/hackathon-umass
uv run src/background_handler_simple.py
# Watch for errors in real-time
```

### Check what's actually running:
```bash
ps aux | grep background_handler
```
