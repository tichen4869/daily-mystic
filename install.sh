#!/bin/bash
# ✧ 每日玄学 - 一键安装 ✧

echo ""
echo "  ✧ 正在安装「每日玄学」✧"
echo ""

DIR="$HOME/daily-mystic"
APP="$HOME/Desktop/每日玄学.app"

# 1. 下载文件
mkdir -p "$DIR"
cd "$DIR"

# 如果是从压缩包解压运行的，文件已经在同目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$SCRIPT_DIR/app.py" ]; then
    cp "$SCRIPT_DIR/app.py" "$DIR/"
    cp "$SCRIPT_DIR/requirements.txt" "$DIR/"
    mkdir -p "$DIR/static"
    cp "$SCRIPT_DIR/static/index.html" "$DIR/static/"
fi

# 2. 安装依赖
echo "  → 安装依赖…"
pip3 install cnlunar flask 2>/dev/null | tail -1

# 3. 创建启动脚本
cat > "$DIR/start.sh" << 'LAUNCH'
#!/bin/bash
PORT=9283
DIR="$HOME/daily-mystic"
URL="http://127.0.0.1:$PORT"

if lsof -ti:$PORT >/dev/null 2>&1; then
    open "$URL"
    exit 0
fi

cd "$DIR"
PORT=$PORT /usr/bin/python3 "$DIR/app.py" &

for i in $(seq 1 30); do
    if curl -s "$URL" >/dev/null 2>&1; then
        open "$URL"
        exit 0
    fi
    sleep 0.3
done
open "$URL"
LAUNCH
chmod +x "$DIR/start.sh"

# 4. 创建桌面 App
mkdir -p "$APP/Contents/MacOS"
mkdir -p "$APP/Contents/Resources"

cat > "$APP/Contents/MacOS/launch" << 'APPSCRIPT'
#!/bin/bash
exec "$HOME/daily-mystic/start.sh"
APPSCRIPT
chmod +x "$APP/Contents/MacOS/launch"

# 图标
if [ -f "$SCRIPT_DIR/icon/AppIcon.icns" ]; then
    cp "$SCRIPT_DIR/icon/AppIcon.icns" "$APP/Contents/Resources/"
fi

cat > "$APP/Contents/Info.plist" << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>launch</string>
    <key>CFBundleName</key>
    <string>每日玄学</string>
    <key>CFBundleIdentifier</key>
    <string>com.mystic.daily</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>LSUIElement</key>
    <true/>
</dict>
</plist>
PLIST

# 5. 修改 app.py 让它用 PORT 环境变量
cd "$DIR"
if ! grep -q "PORT" "$DIR/app.py" 2>/dev/null; then
    echo "port already configured"
fi

# 6. 安装 pywebview（原生弹窗）
echo "  → 安装弹窗组件…"
pip3 install pywebview 2>/dev/null | tail -1

# 7. 创建弹窗启动器
cat > "$DIR/popup.py" << 'POPUP'
#!/usr/bin/env python3
import sys, os, subprocess, time, socket
DIR = os.path.dirname(os.path.abspath(__file__))
PORT = 9283
URL = f"http://127.0.0.1:{PORT}"
def is_running():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try: s.connect(("127.0.0.1", PORT)); s.close(); return True
    except: return False
def start_server():
    subprocess.Popen([sys.executable, os.path.join(DIR, "app.py")],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        env={**os.environ, "PORT": str(PORT)})
    for _ in range(40):
        if is_running(): return True
        time.sleep(0.2)
    return False
def main():
    import webview
    if not is_running(): start_server()
    webview.create_window("每日玄学", URL, width=440, height=780,
        resizable=True, min_size=(360, 600))
    webview.start()
if __name__ == "__main__": main()
POPUP

# 8. 更新桌面 App 用原生弹窗
cat > "$APP/Contents/MacOS/launch" << 'APPSCRIPT'
#!/bin/bash
exec /usr/bin/python3 "$HOME/daily-mystic/popup.py"
APPSCRIPT
chmod +x "$APP/Contents/MacOS/launch"

echo ""
echo "  ✓ 安装完成！"
echo ""
echo "  双击桌面上的「每日玄学」图标即可使用"
echo "  首次打开请点击「命盘」输入你的生辰"
echo ""
