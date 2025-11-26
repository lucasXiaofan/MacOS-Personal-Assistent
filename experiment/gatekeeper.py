import sys, os, time, subprocess
import tkinter as tk

# --- 配置 ---
SAFE_APPS = [
    "Code", "Visual Studio Code", "Electron", "Antigravity", 
    "Obsidian", "iTerm2", "Terminal", "Warp", "Cursor",
    "zoom.us", "Zoom", "Slack", "Claude",
    "python3", "Python"
]
MAX_SECONDS = 10 

def get_app():
    try:
        return os.popen("osascript -e 'tell application \"System Events\" to name of first application process whose frontmost is true'").read().strip()
    except: return ""

# [模式 B]：拦截器模式
def run_blocker_process(trigger_app):
    root = tk.Tk()
    
    # --- 关键修改开始 ---
    # 1. 取消原生全屏（防止创建新桌面）
    # root.attributes("-fullscreen", True) <--- 删掉这行
    
    # 2. 使用“无边框”模式 (像贴纸一样覆盖)
    root.overrideredirect(True) 
    
    # 3. 手动设置大小为屏幕尺寸
    w = root.winfo_screenwidth()
    h = root.winfo_screenheight()
    root.geometry(f"{w}x{h}+0+0")
    
    # 4. 强制置顶
    root.lift()
    root.attributes("-topmost", True)
    # --- 关键修改结束 ---

    root.configure(bg="black")
    
    # 修复 MacOS 上无边框窗口可能无法获取键盘焦点的问题
    # 强制让 AppleScript 把焦点给 Python
    def force_macos_focus():
        os.system("osascript -e 'tell application \"System Events\" to set frontmost of first process whose name contains \"Python\" to true'")
        root.focus_force()
        entry.focus_set()
    
    # 延迟 100ms 执行焦点抢夺，确保窗口已经创建
    root.after(100, force_macos_focus)

    # 界面内容
    tk.Label(root, text=f"🛑 专注中断 🛑\n\n来源: {trigger_app}", font=("Arial", 30), fg="red", bg="black").pack(pady=100)
    tk.Label(root, text="输入计划以继续 (按 Enter):", font=("Arial", 20), fg="white", bg="black").pack()
    
    entry = tk.Entry(root, font=("Arial", 24), width=30)
    entry.pack(pady=20)
    
    # 绑定鼠标点击，以防万一焦点丢了，点一下窗口能找回来
    root.bind("<Button-1>", lambda e: force_macos_focus())

    def commit_suicide(event):
        if entry.get().strip():
            root.destroy()
            sys.exit(0)

    entry.bind("<Return>", commit_suicide)
    
    # 持续置顶
    def keep_top():
        root.lift()
        root.attributes("-topmost", True)
        root.after(500, keep_top)
    
    keep_top()
    root.mainloop()

# [模式 A]：监控模式
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--block":
        run_blocker_process(sys.argv[2])
    else:
        print(f"🛡️ Gatekeeper V6 (贴纸版) 启动...")
        idle_count = 0
        while True:
            try:
                app = get_app()
                if app in SAFE_APPS:
                    idle_count = 0
                    print(f"✅ Flow: {app}".ljust(40), end="\r")
                else:
                    idle_count += 2
                    left = MAX_SECONDS - idle_count
                    print(f"⚠️ 警告: {app} | 剩 {left}s".ljust(40), end="\r")
                
                if idle_count >= MAX_SECONDS:
                    print(f"\n🛑 启动拦截进程...")
                    subprocess.run([sys.executable, __file__, "--block", app])
                    idle_count = 0 
                    print("🛡️ 恢复监控...                    ")
                
                time.sleep(2)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"\nError: {e}")