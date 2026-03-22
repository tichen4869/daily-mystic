#!/usr/bin/env python3
"""每日玄学 - 原生弹窗，不走浏览器"""

import sys
import os
import subprocess
import time
import socket
import urllib.parse

DIR = os.path.dirname(os.path.abspath(__file__))
PORT = 9283
URL = f"http://127.0.0.1:{PORT}"


def is_running():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(("127.0.0.1", PORT))
        s.close()
        return True
    except (ConnectionRefusedError, OSError):
        return False


def start_server():
    subprocess.Popen(
        [sys.executable, os.path.join(DIR, "app.py")],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env={**os.environ, "PORT": str(PORT)},
    )
    for _ in range(40):
        if is_running():
            return True
        time.sleep(0.2)
    return False


def speak_fortune():
    """用 macOS say 命令语音播报今日运势"""
    import json
    import urllib.request

    # 读取本地生辰
    config_path = os.path.join(DIR, "..", "config.json")
    birth = ""
    if os.path.exists(config_path):
        with open(config_path) as f:
            birth = json.load(f).get("birth", "")
    if not birth:
        return

    try:
        url = f"{URL}/api/voice?birth={urllib.parse.quote(birth)}"
        with urllib.request.urlopen(url, timeout=5) as r:
            data = json.loads(r.read())
            text = data.get("text", "")
            if text:
                # 用 macOS 中文语音播报
                # 去掉 emoji 再播报
                import re
                clean = re.sub(r'[\U00010000-\U0010ffff]', '', text)
                subprocess.Popen(["say", "-v", "Tingting", "-r", "220", clean])
    except Exception:
        pass


def main():
    import webview

    if not is_running():
        start_server()

    # 弹窗打开后自动语音播报
    import threading
    threading.Timer(2.0, speak_fortune).start()

    window = webview.create_window(
        "每日玄学",
        URL,
        width=440,
        height=780,
        resizable=True,
        min_size=(360, 600),
        x=0,
        y=0,
        on_top=True,
    )
    webview.start()


if __name__ == "__main__":
    main()
