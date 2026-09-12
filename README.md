# Tube Downloader

一个简单易用的 YouTube 高清视频下载工具，支持 1080p 画质、自动下载字幕和封面。

## 功能特性

- 🎬 **高清下载** - 支持最高 1080p 画质
- 🌐 **多语言字幕** - 自动下载中/英文字幕
- 🖼️ **封面保存** - 自动保存视频封面图片
- 🤖 **自动安装** - ffmpeg 依赖自动检测与安装
- 📁 **本地运行** - Python 虚拟环境，无需全局安装

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/jasonear/tube_d.git
cd tube_d
```

### 2. 创建虚拟环境

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 下载视频

```bash
python download_youtube.py "https://www.youtube.com/watch?v=视频ID"
```

视频将保存在 `downloads/` 目录中。

## 使用方法

### 命令行方式

```bash
# 激活虚拟环境后运行
python download_youtube.py <YouTube视频URL>
```

### Windows 快捷方式

双击 `run.bat` 即可在虚拟环境中运行下载程序。

### 查看帮助

```bash
python download_youtube.py
```

## 依赖说明

| 依赖 | 说明 |
|------|------|
| Python 3.8+ | 运行环境 |
| yt-dlp | YouTube 视频下载核心库 |
| ffmpeg | 音视频合并（程序会自动检测安装） |

## 项目结构

```
tube_d/
├── download_youtube.py   # 主程序
├── install_ffmpeg.py     # ffmpeg 自动安装脚本
├── requirements.txt      # Python 依赖
├── run.bat               # Windows 快捷启动
├── .gitignore            # Git 忽略规则
├── venv/                 # Python 虚拟环境（已忽略）
├── ffmpeg/               # 自动下载的 ffmpeg（已忽略）
└── downloads/            # 下载输出目录（已忽略）
```

## 注意事项

1. 请确保网络可以访问 YouTube 和 ffmpeg 下载源
2. 首次运行会自动下载 ffmpeg（约 80MB）
3. 请遵守 YouTube 使用条款和当地法律法规

## License

MIT