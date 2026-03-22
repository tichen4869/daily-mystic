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
afplay_proc = None
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
    """用微软 edge-tts 语音播报"""
    import json
    import urllib.request
    import tempfile

    config_path = os.path.join(DIR, "..", "config.json")
    birth = ""
    if os.path.exists(config_path):
        with open(config_path) as f:
            birth = json.load(f).get("birth", "")
    if not birth:
        return

    try:
        # 下载 MP3
        url = f"{URL}/api/speak?birth={urllib.parse.quote(birth)}"
        tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        with urllib.request.urlopen(url, timeout=30) as r:
            tmp.write(r.read())
        tmp.close()
        # 用 afplay 播放（macOS 自带），记录进程以便停止
        global afplay_proc
        afplay_proc = subprocess.Popen(["afplay", tmp.name])
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
    def on_closed():
        global afplay_proc
        if afplay_proc:
            afplay_proc.terminate()

    window.events.closed += on_closed
    webview.start()


if __name__ == "__main__":
    main()
