import sys
import os
import subprocess
import yt_dlp


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_FFMPEG_DIR = os.path.join(SCRIPT_DIR, "ffmpeg", "bin")


def find_ffmpeg():
    local_ffmpeg = os.path.join(LOCAL_FFMPEG_DIR, "ffmpeg.exe")
    if os.path.exists(local_ffmpeg):
        print(f"检测到本地 ffmpeg: {local_ffmpeg}")
        return LOCAL_FFMPEG_DIR

    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True, text=True)
        print(f"检测到系统 ffmpeg: {result.stdout.splitlines()[0]}")
        return None
    except subprocess.CalledProcessError:
        return None
    except FileNotFoundError:
        return None


def install_ffmpeg():
    print("正在安装 ffmpeg...")
    install_script = os.path.join(SCRIPT_DIR, "install_ffmpeg.py")
    if os.path.exists(install_script):
        subprocess.check_call([sys.executable, install_script])
    else:
        print("错误: 找不到 install_ffmpeg.py")
        sys.exit(1)


def ensure_ffmpeg():
    ffmpeg_path = find_ffmpeg()
    if ffmpeg_path is not None:
        return ffmpeg_path

    print()
    print("未找到 ffmpeg，正在尝试自动安装...")
    print("(如果自动安装失败，请手动安装: winget install Gyan.FFmpeg)")
    print()
    try:
        install_ffmpeg()
        ffmpeg_path = find_ffmpeg()
        if ffmpeg_path is not None:
            return ffmpeg_path
    except Exception as e:
        print(f"自动安装失败: {e}")
        print()
        print("请手动安装 ffmpeg: winget install Gyan.FFmpeg")
    sys.exit(1)


def install_dependencies():
    try:
        import yt_dlp
    except ImportError:
        print("正在安装依赖...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        import yt_dlp


def download_video(url, output_folder="downloads"):
    os.makedirs(output_folder, exist_ok=True)

    ffmpeg_location = ensure_ffmpeg()

    ydl_opts = {
        "format": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": f"{output_folder}/%(title)s.%(ext)s",
        "noplaylist": True,
        "writethumbnail": True,
        "writesubtitles": True,
        "subtitleslangs": ["zh-Hans", "zh-Hant", "en"],
        "merge_output_format": "mp4",
        "quiet": False,
        "no_warnings": False,
    }

    if ffmpeg_location:
        ydl_opts["ffmpeg_location"] = ffmpeg_location

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title", "Unknown")
            print(f"\n下载完成: {title}")
            print(f"保存位置: {output_folder}/")
    except Exception as e:
        print(f"\n下载失败: {e}")
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("YouTube 高清视频下载器")
        print("=" * 40)
        print()
        print("用法: python download_youtube.py <YouTube视频URL>")
        print()
        print("示例:")
        print('  python download_youtube.py https://www.youtube.com/watch?v=xxxxx')
        print()
        print("功能:")
        print("  - 下载最高 1080p 高清视频")
        print("  - 自动下载中/英文字幕")
        print("  - 自动保存视频封面")
        print("  - 输出目录: downloads/")
        sys.exit(1)

    url = sys.argv[1]
    install_dependencies()
    download_video(url)


if __name__ == "__main__":
    main()