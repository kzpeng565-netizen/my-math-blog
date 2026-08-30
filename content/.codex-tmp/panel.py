#!/usr/bin/env python3
import socket
import subprocess
import time
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox

import psutil


BG = "#10151c"
CARD = "#18212b"
FG = "#f4f7fa"
MUTED = "#a8b3bf"
ACCENT = "#4da3ff"
GOOD = "#43c781"
WARN = "#ffb454"
FONT = "Noto Sans CJK SC"
WORKSPACE_PATH = Path("/home/conrad/workspace")


def local_ip() -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("1.1.1.1", 80))
        return sock.getsockname()[0]
    except OSError:
        return "未联网"
    finally:
        sock.close()


def temperature() -> float | None:
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", encoding="utf-8") as handle:
            return int(handle.read().strip()) / 1000
    except (OSError, ValueError):
        return None


def uptime_text() -> str:
    seconds = int(time.time() - psutil.boot_time())
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes = seconds // 60
    if days:
        return f"{days}天 {hours}小时 {minutes}分"
    return f"{hours}小时 {minutes}分"


def service_active(name: str) -> bool:
    result = subprocess.run(
        ["/usr/bin/systemctl", "is-active", "--quiet", name],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def recent_files(limit: int = 6) -> list[tuple[Path, float]]:
    files: list[tuple[Path, float]] = []
    try:
        candidates = WORKSPACE_PATH.rglob("*")
        for path in candidates:
            try:
                if path.is_file() and not path.is_symlink():
                    files.append((path, path.stat().st_mtime))
            except OSError:
                continue
    except OSError:
        return []
    return sorted(files, key=lambda item: item[1], reverse=True)[:limit]


def confirm_action(title: str, message: str, command: str) -> None:
    if messagebox.askyesno(title, message):
        subprocess.Popen(
            ["/usr/bin/sudo", "/usr/bin/systemctl", command],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def turn_off_display() -> None:
    root.after(
        250,
        lambda: subprocess.Popen(
            ["/usr/bin/xset", "dpms", "force", "off"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ),
    )


def launch_terminal() -> None:
    confirmed = messagebox.askokcancel(
        "打开本地终端",
        "请先连接 USB 键盘。\n\n"
        "需要管理员权限时运行：sudo -i\n"
        "当前系统会直接进入 root。\n\n"
        "输入 exit 可逐级退出并返回面板。",
    )
    if not confirmed:
        return
    subprocess.Popen(
        [
            "/usr/bin/xterm",
            "-fa",
            "Noto Sans Mono CJK SC",
            "-fs",
            str(max(12, int(16 * scale))),
            "-title",
            "Pi 本地终端 - sudo -i 获取 root",
            "-e",
            "/bin/bash",
            "--login",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def launch_ucas_login() -> None:
    confirmed = messagebox.askokcancel(
        "打开 UCAS 网络认证",
        "将切换到学校 UCAS Wi-Fi，并打开官方网络准入认证页。\n\n"
        "请在页面内输入 SEP 账号和密码。浏览器使用临时会话，关闭后不会保留账号、密码或 Cookie。\n\n"
        "右上角的“返回面板”可关闭认证浏览器。",
    )
    if not confirmed:
        return
    subprocess.Popen(
        ["/usr/bin/python3", "/home/conrad/touchpanel/ucas_login.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def connect_backup_wifi() -> None:
    confirmed = messagebox.askyesno(
        "连接备用热点",
        "确定要离开 UCAS，并连接备用热点 XYH 0563 吗？",
    )
    if not confirmed:
        return
    subprocess.Popen(
        [
            "/usr/bin/sudo",
            "/usr/bin/nmcli",
            "connection",
            "up",
            "netplan-wlan0-XYH 0563",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


root = tk.Tk()
root.title("Pi Server Panel")
root.configure(bg=BG)
root.attributes("-fullscreen", True)
root.bind("<Escape>", lambda _event: root.destroy())

screen_w = max(root.winfo_screenwidth(), 640)
screen_h = max(root.winfo_screenheight(), 480)
scale = min(screen_w / 1024, screen_h / 600)
clock_size = max(28, int(54 * scale))
title_size = max(13, int(20 * scale))
body_size = max(12, int(18 * scale))
button_size = max(12, int(17 * scale))
pad = max(8, int(14 * scale))

root.grid_columnconfigure(0, weight=3)
root.grid_columnconfigure(1, weight=4)
root.grid_rowconfigure(1, weight=1)

header = tk.Frame(root, bg=BG)
header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=pad, pady=(pad, 0))
header.grid_columnconfigure(1, weight=1)

clock_label = tk.Label(header, text="--:--", font=(FONT, clock_size, "bold"), fg=FG, bg=BG)
clock_label.grid(row=0, column=0, rowspan=2, sticky="w")
date_label = tk.Label(header, text="", font=(FONT, title_size), fg=MUTED, bg=BG)
date_label.grid(row=0, column=1, sticky="e")
host_label = tk.Label(header, text="Pi 服务器", font=(FONT, title_size, "bold"), fg=ACCENT, bg=BG)
host_label.grid(row=1, column=1, sticky="e")

status_card = tk.Frame(root, bg=CARD, padx=pad, pady=pad)
status_card.grid(row=1, column=0, sticky="nsew", padx=(pad, pad // 2), pady=pad)
status_card.grid_columnconfigure(1, weight=1)

metrics: dict[str, tk.Label] = {}
for row, (key, label) in enumerate(
    [
        ("cpu", "CPU"),
        ("temp", "温度"),
        ("memory", "内存"),
        ("disk", "磁盘"),
        ("uptime", "运行时间"),
    ]
):
    tk.Label(status_card, text=label, font=(FONT, body_size), fg=MUTED, bg=CARD).grid(
        row=row, column=0, sticky="w", pady=max(2, pad // 3)
    )
    value = tk.Label(status_card, text="--", font=(FONT, body_size, "bold"), fg=FG, bg=CARD)
    value.grid(row=row, column=1, sticky="e", pady=max(2, pad // 3))
    metrics[key] = value

right = tk.Frame(root, bg=BG)
right.grid(row=1, column=1, sticky="nsew", padx=(pad // 2, pad), pady=pad)
right.grid_columnconfigure(0, weight=1)
right.grid_columnconfigure(1, weight=1)
right.grid_rowconfigure(1, weight=1)
right.grid_rowconfigure(2, weight=1)
right.grid_rowconfigure(3, weight=1)
right.grid_rowconfigure(4, weight=1)

network_card = tk.Frame(right, bg=CARD, padx=pad, pady=pad)
network_card.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, pad))
network_card.grid_columnconfigure(0, weight=1)
ip_label = tk.Label(network_card, text="IP：--", font=(FONT, body_size, "bold"), fg=FG, bg=CARD)
ip_label.grid(row=0, column=0, sticky="w")
cockpit_label = tk.Label(network_card, text="Cockpit：检查中", font=(FONT, body_size), fg=MUTED, bg=CARD)
cockpit_label.grid(row=1, column=0, sticky="w", pady=(pad // 2, 0))
url_label = tk.Label(network_card, text="", font=(FONT, max(10, body_size - 2)), fg=ACCENT, bg=CARD)
url_label.grid(row=2, column=0, sticky="w")

button_options = {
    "font": (FONT, button_size, "bold"),
    "bd": 0,
    "relief": "flat",
    "activeforeground": FG,
    "height": 2,
}


def add_button(row: int, column: int, text: str, command, color: str) -> tk.Button:
    button = tk.Button(
        right,
        text=text,
        command=command,
        fg=FG,
        bg=color,
        activebackground=color,
        **button_options,
    )
    button.grid(row=row, column=column, sticky="nsew", padx=pad // 3, pady=pad // 3)
    return button


add_button(1, 0, "最近修改的文件", lambda: show_recent_files(), "#276fae")
add_button(1, 1, "本地终端", launch_terminal, "#35616f")
add_button(2, 0, "UCAS 网络认证", launch_ucas_login, "#287c63")
add_button(2, 1, "连接备用热点", connect_backup_wifi, "#6b5b35")
add_button(3, 0, "立即刷新", lambda: update_status(), "#276fae")
add_button(3, 1, "关闭屏幕", turn_off_display, "#48596b")
add_button(4, 0, "重启系统", lambda: confirm_action("确认重启", "确定要重启树莓派吗？", "reboot"), "#a86424")
add_button(4, 1, "安全关机", lambda: confirm_action("确认关机", "确定要安全关闭树莓派吗？", "poweroff"), "#9f3d46")

weekdays = "一二三四五六日"


recent_files_page = tk.Frame(root, bg=BG)


def hide_recent_files() -> None:
    recent_files_page.place_forget()


def show_recent_files() -> None:
    for child in recent_files_page.winfo_children():
        child.destroy()
    recent_files_page.place(x=0, y=0, relwidth=1, relheight=1)
    recent_files_page.lift()
    recent_files_page.grid_columnconfigure(0, weight=1)
    recent_files_page.grid_rowconfigure(1, weight=1)

    top = tk.Frame(recent_files_page, bg=BG)
    top.grid(row=0, column=0, sticky="ew", padx=pad, pady=pad)
    top.grid_columnconfigure(0, weight=1)
    tk.Label(top, text="最近修改的文件", font=(FONT, clock_size, "bold"), fg=FG, bg=BG).grid(
        row=0, column=0, sticky="w"
    )
    tk.Button(
        top,
        text="返回首页",
        command=hide_recent_files,
        font=(FONT, button_size, "bold"),
        fg=FG,
        bg="#48596b",
        activebackground="#48596b",
        activeforeground=FG,
        bd=0,
        padx=pad,
        pady=pad // 2,
    ).grid(row=0, column=1, sticky="e")

    list_frame = tk.Frame(recent_files_page, bg=BG)
    list_frame.grid(row=1, column=0, sticky="nsew", padx=pad, pady=(0, pad))
    list_frame.grid_columnconfigure(0, weight=1)
    files = recent_files()
    if not files:
        tk.Label(
            list_frame,
            text="工作区内暂无文件",
            font=(FONT, title_size),
            fg=MUTED,
            bg=BG,
            justify="center",
        ).grid(row=0, column=0, sticky="nsew", pady=pad * 3)
        return

    for row, (path, modified) in enumerate(files):
        relative_path = path.relative_to(WORKSPACE_PATH)
        modified_text = datetime.fromtimestamp(modified).strftime("%m-%d %H:%M")
        tk.Label(
            list_frame,
            text=f"{relative_path}\n修改于 {modified_text}",
            font=(FONT, body_size, "bold"),
            anchor="w",
            justify="left",
            fg=FG,
            bg=CARD,
            padx=pad,
            pady=max(5, pad // 2),
        ).grid(row=row, column=0, sticky="ew", pady=max(2, pad // 4))


def update_status() -> None:
    now = datetime.now()
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    temp = temperature()
    ip = local_ip()
    cockpit_ok = service_active("cockpit.socket")

    clock_label.config(text=now.strftime("%H:%M:%S"))
    date_label.config(text=f"{now:%Y年%m月%d日} 星期{weekdays[now.weekday()]}")
    metrics["cpu"].config(text=f"{psutil.cpu_percent():.0f}%")
    metrics["temp"].config(text="未知" if temp is None else f"{temp:.1f} °C", fg=WARN if temp and temp >= 70 else FG)
    metrics["memory"].config(text=f"{memory.percent:.0f}%")
    metrics["disk"].config(text=f"{disk.percent:.0f}%")
    metrics["uptime"].config(text=uptime_text())
    ip_label.config(text=f"IP：{ip}")
    cockpit_label.config(text=f"Cockpit：{'运行中' if cockpit_ok else '未运行'}", fg=GOOD if cockpit_ok else WARN)
    url_label.config(text="" if ip == "未联网" else f"https://{ip}:9090")
    root.after(1000, update_status)


update_status()
root.mainloop()
