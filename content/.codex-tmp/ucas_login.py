#!/usr/bin/env python3
import fcntl
import os
import shutil
import signal
import subprocess
import tempfile
import tkinter as tk
from tkinter import messagebox


PORTAL_URL = "https://portal.ucas.ac.cn/index_11.html"
UCAS_CONNECTION = "UCAS"
LOCK_PATH = "/tmp/ucas-login.lock"


class UcasLogin:
    def __init__(self) -> None:
        self.lock_handle = open(LOCK_PATH, "w", encoding="utf-8")
        try:
            fcntl.flock(self.lock_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise SystemExit(0)

        self.profile_dir = tempfile.mkdtemp(prefix="ucas-chromium-")
        self.keyboard: subprocess.Popen | None = None
        self.browser: subprocess.Popen | None = None

        self.root = tk.Tk()
        self.root.title("UCAS 网络认证控制")
        self.root.configure(bg="#10151c")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.geometry("210x68-12+12")
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        self.status = tk.Label(
            self.root,
            text="正在连接 UCAS…",
            font=("Noto Sans CJK SC", 12, "bold"),
            fg="#f4f7fa",
            bg="#10151c",
        )
        self.status.pack(fill="x", padx=8, pady=(5, 2))
        tk.Button(
            self.root,
            text="返回服务器面板",
            command=self.close,
            font=("Noto Sans CJK SC", 12, "bold"),
            fg="#ffffff",
            bg="#9f3d46",
            activeforeground="#ffffff",
            activebackground="#b14953",
            bd=0,
        ).pack(fill="x", padx=8, pady=(0, 6))

        self.root.after(100, self.start)
        self.root.after(1000, self.keep_visible)

    def start(self) -> None:
        result = subprocess.run(
            ["/usr/bin/sudo", "/usr/bin/nmcli", "connection", "up", UCAS_CONNECTION],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=30,
        )
        if result.returncode != 0:
            messagebox.showerror("UCAS 连接失败", "无法连接 UCAS Wi-Fi，请检查信号后重试。")
            self.close()
            return

        self.status.config(text="UCAS 已连接 · 临时会话")
        env = os.environ.copy()
        env.setdefault("DISPLAY", ":0")
        env.setdefault("XAUTHORITY", "/home/conrad/.Xauthority")

        self.keyboard = subprocess.Popen(
            ["/usr/bin/matchbox-keyboard"],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self.browser = subprocess.Popen(
            [
                "/usr/bin/chromium",
                f"--app={PORTAL_URL}",
                f"--user-data-dir={self.profile_dir}",
                "--incognito",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-sync",
                "--disable-save-password-bubble",
                "--disable-session-crashed-bubble",
                "--password-store=basic",
                "--start-maximized",
            ],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self.root.after(1000, self.check_browser)

    def keep_visible(self) -> None:
        if self.root.winfo_exists():
            self.root.lift()
            self.root.attributes("-topmost", True)
            self.root.after(1000, self.keep_visible)

    def check_browser(self) -> None:
        if self.browser is not None and self.browser.poll() is not None:
            self.close()
            return
        self.root.after(1000, self.check_browser)

    @staticmethod
    def stop_process(process: subprocess.Popen | None) -> None:
        if process is None or process.poll() is not None:
            return
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)

    def close(self) -> None:
        self.stop_process(self.browser)
        self.stop_process(self.keyboard)
        shutil.rmtree(self.profile_dir, ignore_errors=True)
        try:
            self.root.destroy()
        except tk.TclError:
            pass

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    def terminate(_signum, _frame) -> None:
        raise SystemExit(0)

    signal.signal(signal.SIGTERM, terminate)
    app = UcasLogin()
    try:
        app.run()
    finally:
        app.stop_process(app.browser)
        app.stop_process(app.keyboard)
        shutil.rmtree(app.profile_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
