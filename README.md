# Tube Downloader

一个功能强大的 YouTube 高清视频下载工具，支持批量下载、实时进度显示、视频预览、自定义路径等高级特性。

## 在线文档

📖 [完整文档站点](docs/index.html) - 交互式文档页面（点击直接打开）

---

## 功能特性

### 核心功能

- 🎬 **高清下载** - 支持最高 1080p 画质
- 🎞️ **多格式支持** - 自动选择 MP4/WebM 最佳格式，输出统一为 MP4
- 🌐 **多语言字幕** - 自动下载简体/繁体/英文字幕（SRT 格式）
- 🖼️ **封面保存** - 自动保存视频封面图片（WebP 格式）

### 新增特性 v2.0

- 📊 **实时进度显示** - 进度条 + 下载速度 + 预计剩余时间
- 💾 **文件大小限制** - 支持设置最大文件大小，自动检查磁盘空间
- ⚡ **批量并发下载** - 多线程并发下载多个视频，可自定义并发数
- 📁 **自定义输出路径** - 灵活指定下载保存目录
- 👁️ **视频信息预览** - 下载前显示标题、时长、分辨率、预估大小

### 系统特性

- 🔍 **智能检测** - 自动检测 ffmpeg/ffprobe（支持本地和系统路径）
- 🤖 **自动安装** - 依赖缺失时自动下载安装
- 🔄 **断点续传** - 支持下载中断后继续
- 🔁 **自动重试** - 网络波动时自动重试（默认 3 次）
- 🛡️ **安全处理** - 自动清理文件名中的特殊字符
- 📁 **本地运行** - Python 虚拟环境，无需全局安装

---

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

---

## 使用方法

### 基础用法

```bash
# 下载单个视频（默认参数）
python download_youtube.py <URL>

# 查看帮助信息
python download_youtube.py --help
```

### 命令行参数

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `urls` | - | YouTube 视频 URL（支持多个） | 必填 |
| `--output` | `-o` | 输出目录路径 | `downloads` |
| `--concurrent` | `-c` | 并发下载数 | `1` |
| `--retries` | `-r` | 最大重试次数 | `3` |
| `--max-size` | - | 最大文件大小限制 (如 1GB) | 不限制 |
| `--preview-only` | - | 仅预览视频信息，不下载 | False |
| `--no-preview` | - | 下载前不显示视频信息 | False |

### 使用示例

#### 下载单个视频

```bash
python download_youtube.py https://www.youtube.com/watch?v=xxxxx
```

#### 自定义输出目录

```bash
python download_youtube.py -o my_videos https://www.youtube.com/watch?v=xxxxx
```

#### 批量下载

```bash
# 批量下载多个视频（顺序执行）
python download_youtube.py url1 url2 url3

# 批量下载并设置并发数（并行执行）
python download_youtube.py -c 5 url1 url2 url3 url4 url5
```

#### 设置文件大小限制

```bash
# 限制单个视频最大 1GB
python download_youtube.py --max-size 1GB url1 url2

# 支持格式: B, KB, MB, GB, TB
python download_youtube.py --max-size 500MB url
python download_youtube.py --max-size 2GB url
```

#### 仅预览视频信息

```bash
# 查看视频信息但不下载
python download_youtube.py --preview-only https://www.youtube.com/watch?v=xxxxx
```

#### 跳过预览直接下载

```bash
# 不显示视频信息预览，直接开始下载
python download_youtube.py --no-preview https://www.youtube.com/watch?v=xxxxx
```

---

## 输出示例

### 视频信息预览

```
============================================================
📹 视频信息预览
============================================================
  标题:       How to Build a REST API with Python
  上传者:     Programming with Mosh
  时长:       0:32:15
  分辨率:     1920x1080
  观看次数:   2,456,789
  上传日期:   2024-03-15
  预估大小:   856.42 MB
============================================================
  磁盘空间: 可用 256.78 GB ✓
```

### 下载进度显示

```
📥 开始下载 (第 1 次尝试)...

  下载: How to Build a REST API with Python
  [████████████████░░░░░░░░░░░░░░]  45.2%  387.56 MB/856.42 MB  12.5 MB/s  ETA: 0:00:37
```

### 批量下载总结

```
============================================================
📊 下载完成总结
  总数:   5
  成功:   4 ✓
  失败:   1

失败列表:
  - [3/5] 下载失败
============================================================
```

---

## 视频格式说明

程序按以下优先级自动选择最佳视频格式：

| 优先级 | 格式组合 | 说明 |
|--------|----------|------|
| 1️⃣ | MP4 视频 + M4A 音频 | 最佳兼容性，需要 ffmpeg 合并 |
| 2️⃣ | WebM 视频 + WebM 音频 | VP9/AV1 编码，更高压缩效率 |
| 3️⃣ | 单文件 MP4 | 低质量但无需合并 |
| 4️⃣ | 任意最佳格式 | 兜底方案 |

最终输出统一转换为 **MP4** 格式，确保最大兼容性。

---

## 字幕说明

- 自动下载 **简体中文**、**繁体中文**、**英文** 字幕
- 字幕格式：**SRT**（通用格式，兼容主流播放器）
- 当视频没有对应字幕时，程序会自动跳过，不会报错

---

## 网络容错机制

程序内置多层容错机制，确保下载稳定性：

```
1. 断点续传
   └── 下载中断后可以从断点继续，无需重新开始

2. 自动重试（3 次）
   └── 第 1 次失败：等待 5 秒后重试
   └── 第 2 次失败：等待 10 秒后重试
   └── 第 3 次失败：等待 15 秒后重试
   └── 全部失败 → 显示错误信息

3. 字幕容错
   └── 缺少字幕时自动跳过，不影响视频下载
```

---

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

---

## 依赖说明

| 依赖 | 说明 | 自动安装 |
|------|------|:--------:|
| Python 3.8+ | 运行环境 | ✗ |
| yt-dlp | YouTube 视频下载核心库 | ✓ |
| ffmpeg | 音视频合并与格式转换 | ✓ |
| ffprobe | 媒体文件分析工具 | ✓ |

---

## 项目结构

```
tube_d/
├── download_youtube.py   # 主程序
├── install_ffmpeg.py     # ffmpeg 自动安装脚本
├── requirements.txt      # Python 依赖
├── run.bat               # Windows 快捷启动
├── .gitignore            # Git 忽略规则
├── docs/                 # 文档站点
│   └── index.html        # 交互式文档首页
├── venv/                 # Python 虚拟环境（已忽略）
├── ffmpeg/               # 自动下载的 ffmpeg（已忽略）
└── downloads/            # 下载输出目录（已忽略）
```

---

## 下载结果示例

```
downloads/
├── 视频标题.mp4           # 合并后的高清视频
├── 视频标题.webp          # 视频封面
└── 视频标题.zh-Hans.srt   # 简体中文字幕
```

---

## 常见问题

### Q: 提示 "未找到 ffmpeg" 怎么办？

A: 程序会自动尝试安装。如果安装失败，可以手动安装：
- **Windows**: `winget install Gyan.FFmpeg`
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`

### Q: 下载的视频没有声音？

A: 请确保 **ffprobe** 已正确安装，程序需要它来分析音频流。

### Q: 下载失败提示网络错误？

A: 程序会自动重试 3 次。如果仍然失败，请检查网络连接或稍后重试。

### Q: 视频标题有特殊字符怎么办？

A: 程序会自动清理文件名中的非法字符（如 `\ / : * ? " < > |`），替换为下划线 `_`。

### Q: 如何批量下载多个视频？

A: 直接在命令行传入多个 URL 即可：
```bash
python download_youtube.py url1 url2 url3
```
使用 `-c` 参数可设置并发数：
```bash
python download_youtube.py -c 3 url1 url2 url3 url4 url5
```

### Q: 如何限制下载文件大小？

A: 使用 `--max-size` 参数：
```bash
python download_youtube.py --max-size 1GB url
```
支持单位：B, KB, MB, GB, TB

---

## 注意事项

1. 请确保网络可以访问 YouTube 和 ffmpeg 下载源
2. 首次运行会自动下载 ffmpeg（约 80MB）
3. 部分视频可能不支持 1080p，程序会自动选择最佳可用质量
4. 批量下载时注意并发数不宜过高，建议 3-5 个
5. 请遵守 YouTube 使用条款和当地法律法规

---

## License

MIT