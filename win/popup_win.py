#!/usr/bin/env python3
"""每日玄学 - Windows 原生弹窗"""

import sys
import os
import subprocess
import time
import socket
import urllib.parse
import re

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
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    for _ in range(40):
        if is_running():
            return True
        time.sleep(0.2)
    return False


def speak_fortune():
    import json
    import urllib.request

    config_path = os.path.join(DIR, "config.json")
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
                clean = re.sub(r'[\U00010000-\U0010ffff]', '', text)
                # Windows TTS
                subprocess.Popen([
                    "powershell", "-Command",
                    f'Add-Type -AssemblyName System.Speech; '
                    f'$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; '
                    f'$s.Rate = 2; '
                    f'$s.Speak("{clean}")'
                ], creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    except Exception:
        pass


def main():
    import webview

    if not is_running():
        start_server()

    import threading
    threading.Timer(2.0, speak_fortune).start()

    webview.create_window(
        "每日玄学",
        URL,
        width=440,
        height=780,
        resizable=True,
        min_size=(360, 600),
    )
    webview.start()


if __name__ == "__main__":
    main()
