# Tube Downloader

一个简单易用的 YouTube 高清视频下载工具，支持 1080p 画质、自动下载字幕和封面。

## 功能特性

- 🎬 **高清下载** - 支持最高 1080p 画质
- 🎞️ **多格式支持** - 自动选择 MP4/WebM 最佳格式，输出统一为 MP4
- 🌐 **多语言字幕** - 自动下载简体/繁体/英文字幕（SRT 格式）
- 🖼️ **封面保存** - 自动保存视频封面图片（WebP 格式）
- 🔍 **智能检测** - 自动检测 ffmpeg/ffprobe（支持本地和系统路径）
- 🤖 **自动安装** - 依赖缺失时自动下载安装
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

## 视频格式说明

程序按以下优先级自动选择最佳视频格式：

| 优先级 | 格式组合 | 说明 |
|--------|----------|------|
| 1️⃣ | MP4 视频 + M4A 音频 | 最佳兼容性，需要 ffmpeg 合并 |
| 2️⃣ | WebM 视频 + WebM 音频 | VP9/AV1 编码，更高压缩效率 |
| 3️⃣ | 单文件 MP4 | 低质量但无需合并 |
| 4️⃣ | 任意最佳格式 | 兜底方案 |

最终输出统一转换为 **MP4** 格式，确保最大兼容性。

## 字幕说明

- 自动下载 **简体中文**、**繁体中文**、**英文** 字幕
- 字幕格式：**SRT**（通用格式，兼容主流播放器）
- 当视频没有对应字幕时，程序会自动跳过，不会报错

## 依赖检测机制

程序启动时会按以下顺序检测依赖：

```
1. 检查本地 ffmpeg/ffprobe
   └── 存在 → 使用本地版本
   └── 不存在 → 继续步骤 2

2. 检查系统 ffmpeg/ffprobe
   └── 存在 → 使用系统版本
   └── 不存在 → 继续步骤 3

3. 自动安装 ffmpeg 套件
   └── 安装成功 → 使用本地版本
   └── 安装失败 → 提示手动安装
```

> **注意**：音视频合并功能需要同时具备 **ffmpeg** 和 **ffprobe** 两个组件。

## 依赖说明

| 依赖 | 说明 | 自动安装 |
|------|------|:--------:|
| Python 3.8+ | 运行环境 | ✗ |
| yt-dlp | YouTube 视频下载核心库 | ✓ |
| ffmpeg | 音视频合并与格式转换 | ✓ |
| ffprobe | 媒体文件分析工具 | ✓ |

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

## 下载结果示例

```
downloads/
├── 视频标题.mp4           # 合并后的高清视频
├── 视频标题.webp          # 视频封面
└── 视频标题.zh-Hans.srt   # 简体中文字幕
```

## 常见问题

### Q: 提示 "未找到 ffmpeg" 怎么办？

A: 程序会自动尝试安装。如果安装失败，可以手动安装：
- **Windows**: `winget install Gyan.FFmpeg`
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`

### Q: 下载的视频没有声音？

A: 请确保 **ffprobe** 已正确安装，程序需要它来分析音频流。

## 注意事项

1. 请确保网络可以访问 YouTube 和 ffmpeg 下载源
2. 首次运行会自动下载 ffmpeg（约 80MB）
3. 部分视频可能不支持 1080p，程序会自动选择最佳可用质量
4. 请遵守 YouTube 使用条款和当地法律法规

## License

MIT