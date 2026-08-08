# 玄日 · daily-mystic

每天早上花 10 秒，看看今天适合做什么、不适合做什么。

「玄日」是一个基于个人生辰八字与传统黄历的每日运势应用：结合你的出生时间和当天的干支五行，生成专属的宜忌事项、幸运颜色、财神方位、吉时和穿搭建议，还能语音播报、写运势日记。支持网页直接用、加到手机主屏幕当 App、也能装成 Mac / Windows 桌面小程序。

在线体验：https://daily-mystic.onrender.com

## 功能

- **个性化宜忌**：不是通用黄历，而是结合你的八字喜用神，对当天的「宜/忌」事项重新排序、消解冲突，告诉你哪些事今天做对你更有利。
- **命理速览**：日主强弱、命格、喜用神/忌神、当日干支与五行。
- **每日彩蛋**：幸运颜色、幸运数字、财神方位、宜穿搭配色、当日吉时（十二时辰）。
- **语音播报**：一句话总结今天的运势，可用 Edge TTS 生成语音，或配合 iOS 快捷指令做成每天早上自动播报。
- **运势日记**：记录当天的心情/事件，本地保存并可同步到 GitHub，换设备也能找回。
- **PWA / 多端安装**：手机浏览器「添加到主屏幕」即可当 App 用；也提供 Mac（`install.sh`）和 Windows（`win/安装玄日.bat`）一键安装脚本，装出原生弹窗小程序。

## 技术栈

- 后端：Python + [Flask](https://flask.palletsprojects.com/)
- 农历 / 干支排盘：[cnlunar](https://pypi.org/project/cnlunar/)
- 语音合成：[edge-tts](https://github.com/rany2/edge-tts)
- 部署：Render（见 `render.yaml` / `Procfile`），用 gunicorn 起服务
- 前端：原生 HTML/CSS/JS 单页应用（`static/index.html`），带 Service Worker 离线缓存

## 本地运行

```bash
git clone https://github.com/tichen4869/daily-mystic.git
cd daily-mystic
pip install -r requirements.txt
python app.py
```

默认监听 `PORT` 环境变量指定的端口（未设置时见 `app.py` 内默认值），启动后打开 `http://127.0.0.1:<端口>` 即可，首次使用点击「命盘」输入你的出生时间（格式：年/月/日/时:分）。

## 部署到 Render

仓库已包含 `render.yaml` 和 `Procfile`，直接在 Render 新建 Web Service 并关联本仓库即可，构建命令 `pip install -r requirements.txt`，启动命令 `gunicorn app:app`。

## 手机安装

用 Safari / Chrome 打开在线地址，选择「添加到主屏幕」，即可像 App 一样使用；也支持设置每日定时语音播报。详细图文步骤见 [手机安装教程.md](./手机安装教程.md)。

## 桌面安装

- **Mac**：双击 `安装玄日.command`（或运行 `./install.sh`），会在桌面生成「玄日.app」原生弹窗小程序。
- **Windows**：运行 `win/安装玄日.bat`，在桌面生成快捷方式。

## 主要 API

| 接口 | 说明 |
| --- | --- |
| `GET /api/fortune?birth=&date=` | 核心接口，返回当日黄历 + 个性化八字分析 |
| `GET /api/voice?birth=&date=` | 返回当日运势的播报文案 |
| `GET /api/speak?birth=&date=` | 生成运势播报语音（mp3） |
| `GET/POST /api/journal` | 读取 / 保存某天的运势日记 |
| `GET /api/journal/all?birth=` | 获取某用户全部日记（本地 + GitHub 合并） |

## 项目结构

```
app.py              后端主程序（排盘、八字分析、宜忌逻辑、API）
static/index.html   前端单页应用
static/sw.js        Service Worker，离线缓存
install.sh / 安装玄日.command   Mac 一键安装
win/                Windows 版本（app.py、启动脚本、安装脚本）
popup.py            桌面弹窗启动器（pywebview）
手机安装教程.md      手机端图文安装教程
render.yaml / Procfile   Render 部署配置
```
