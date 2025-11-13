"""
Simple agent activity logger
Logs daily activities like task creation, paper tracking, etc.
"""

import os
from datetime import datetime, timedelta

LOG_FILE = "/Users/xiaofanlu/Documents/github_repos/hackathon-umass/memory/agent_activity.log"

def log_activity(summary, files_changed=None):
    """
    Log agent activity with timestamp

    Args:
        summary: One-line description of what was done
        files_changed: Optional list of file paths that were modified

    Example:
        log_activity("Tracked new paper: RARE agents", ["/memory/papers/RARE.md"])
        log_activity("Created task: Math 233 Exam 2 due 2025-11-15")
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Format the log entry
    log_entry = f"[{timestamp}] {summary}"

    if files_changed:
        if isinstance(files_changed, str):
            files_changed = [files_changed]
        files_str = ", ".join(files_changed)
        log_entry += f" | Files: {files_str}"

    # Append to log file
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, 'a') as f:
        f.write(log_entry + "\n")

    return log_entry

def get_recent_logs(days=7):
    """
    Get logs from the last X days

    Args:
        days: Number of days to look back (default 7)

    Returns:
        String with formatted recent logs
    """
    if not os.path.exists(LOG_FILE):
        return "No activity logs found."

    cutoff_date = datetime.now() - timedelta(days=days)

    with open(LOG_FILE, 'r') as f:
        lines = f.readlines()

    recent_logs = []
    for line in lines:
        # Extract timestamp from log entry [YYYY-MM-DD HH:MM:SS]
        if line.startswith("["):
            try:
                timestamp_str = line[1:20]  # Extract "YYYY-MM-DD HH:MM:SS"
                log_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")

                if log_time >= cutoff_date:
                    recent_logs.append(line.strip())
            except:
                continue

    if not recent_logs:
        return f"No activity logs in the last {days} days."

    header = f"ACTIVITY LOGS (Last {days} days)"
    separator = "=" * len(header)

    return f"{header}\n{separator}\n" + "\n".join(recent_logs)
