#!/usr/bin/env python3
"""玄日 - 原生弹窗"""

import sys
import os
import subprocess
import time
import socket

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


def main():
    import webview

    if not is_running():
        start_server()

    # 桌面端加 ?desktop=1 让网页知道要自动播报
    window = webview.create_window(
        "玄日",
        URL + "?desktop=1",
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
