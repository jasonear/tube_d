import sys
import os
import re
import time
import math
import json
import shutil
import argparse
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import timedelta

import yt_dlp


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_FFMPEG_DIR = os.path.join(SCRIPT_DIR, "ffmpeg", "bin")

# 全局锁用于线程安全的打印
_print_lock = threading.Lock()


def sanitize_filename(filename, max_length=200):
    """清理文件名中的非法字符"""
    illegal_chars = r'[\\/:*?"<>|\x00-\x1f\r\n]'
    safe_name = re.sub(illegal_chars, '_', filename)
    safe_name = safe_name.strip(' .')
    if len(safe_name) > max_length:
        safe_name = safe_name[:max_length]
    return safe_name if safe_name else "untitled"


def safe_print(text):
    """线程安全的打印函数"""
    with _print_lock:
        print(text, flush=True)


def format_bytes(size_bytes):
    """格式化字节数为人类可读格式"""
    if size_bytes is None or size_bytes < 0:
        return "未知"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"


def format_duration(seconds):
    """格式化秒数为 HH:MM:SS"""
    if seconds is None:
        return "未知"
    return str(timedelta(seconds=int(seconds)))


def check_disk_space(path, required_bytes):
    """检查磁盘空间是否足够"""
    try:
        disk_usage = shutil.disk_usage(path)
        free_bytes = disk_usage.free
        if free_bytes < required_bytes:
            return False, free_bytes
        return True, free_bytes
    except Exception as e:
        print(f"警告: 无法检查磁盘空间 - {e}")
        return True, None


def estimate_file_size(info, format_selector="best"):
    """预估文件大小（字节）"""
    size = info.get('filesize') or info.get('filesize_approx')
    if size:
        return int(size)

    fps = info.get('f', {})
    if isinstance(fps, list):
        for f in fps:
            if f.get('format_id', '').startswith(format_selector):
                return int(f.get('filesize') or f.get('filesize_approx') or 0)
        for f in fps:
            size = f.get('filesize') or f.get('filesize_approx')
            if size:
                return int(size)

    duration = info.get('duration')
    filesize_approx = info.get('filesize_approx')
    if filesize_approx:
        return int(filesize_approx)

    return None


def preview_video_info(ydl, url):
    """下载前预览视频信息"""
    try:
        with ydl:
            info = ydl.extract_info(url, download=False)

            title = info.get('title', '未知')
            duration = info.get('duration', 0)
            uploader = info.get('uploader', '未知')
            view_count = info.get('view_count', 0)
            upload_date = info.get('upload_date', '')
            thumbnail = info.get('thumbnail', '')

            # 获取分辨率信息
            height = info.get('height') or info.get('width')
            resolution = f"{info.get('width', '?')}x{height}" if height else "未知"

            # 预估大小
            estimated_size = estimate_file_size(info)

            print("=" * 60)
            print("📹 视频信息预览")
            print("=" * 60)
            print(f"  标题:       {title}")
            print(f"  上传者:     {uploader}")
            print(f"  时长:       {format_duration(duration)}")
            print(f"  分辨率:     {resolution}")
            print(f"  观看次数:   {view_count:,}" if view_count else "  观看次数:   未知")
            if upload_date and len(upload_date) == 8:
                upload_date_formatted = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
                print(f"  上传日期:   {upload_date_formatted}")
            if estimated_size:
                print(f"  预估大小:   {format_bytes(estimated_size)}")
            print("=" * 60)

            return info
    except Exception as e:
        print(f"警告: 无法获取视频信息 - {e}")
        return None


class ProgressHook:
    """下载进度回调类"""

    def __init__(self, title=""):
        self.title = title
        self.last_percent = -1
        self.last_print_time = 0

    def progress_hook(self, d):
        """yt-dlp 进度回调函数"""
        if d['status'] == 'downloading':
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            speed = d.get('speed', 0)
            eta = d.get('eta', 0)

            if total:
                percent = (downloaded / total) * 100
            else:
                percent = -1

            # 每 2% 或每 1 秒更新一次，避免过于频繁的打印
            current_time = time.time()
            should_update = (
                percent >= 0 and
                (percent - self.last_percent >= 2 or current_time - self.last_print_time >= 1)
            )

            if should_update:
                progress_bar_len = 30
                if percent >= 0:
                    filled = int(progress_bar_len * percent / 100)
                    progress_bar = '█' * filled + '░' * (progress_bar_len - filled)
                    percent_str = f"{percent:5.1f}%"
                    total_str = format_bytes(total)
                else:
                    progress_bar = '░' * progress_bar_len
                    percent_str = "未知  "
                    total_str = "未知"

                downloaded_str = format_bytes(downloaded)
                speed_str = format_bytes(speed) + "/s" if speed else "计算中..."
                eta_str = format_duration(eta) if eta else "计算中..."

                # 使用 \r 实现单行更新
                with _print_lock:
                    if self.title:
                        title_display = self.title[:40]
                        print(f"\r  下载: {title_display}")
                        print(f"\r  [{''.join(progress_bar)}] {percent_str}", end='', flush=True)
                        print(f"  {downloaded_str}/{total_str}  {speed_str}  ETA: {eta_str}", end='', flush=True)
                    else:
                        print(f"\r  [{''.join(progress_bar)}] {percent_str}", end='', flush=True)
                        print(f"  {downloaded_str}/{total_str}  {speed_str}  ETA: {eta_str}", end='', flush=True)

                self.last_percent = percent
                self.last_print_time = current_time

        elif d['status'] == 'finished':
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes') or d.get('total_bytes_estimate')

            with _print_lock:
                if total:
                    print(f"\r  [{'█' * 30}] 100.0%  {format_bytes(downloaded)}/{format_bytes(total)}  ✓ 完成!")
                else:
                    print(f"\r  [{'█' * 30}] 完成!  已下载: {format_bytes(downloaded)}")
                print()

        elif d['status'] == 'error':
            with _print_lock:
                print(f"\r  [{'✗' * 30}] 下载出错!")
                print()


def find_ffmpeg():
    local_ffmpeg = os.path.join(LOCAL_FFMPEG_DIR, "ffmpeg.exe")
    local_ffprobe = os.path.join(LOCAL_FFMPEG_DIR, "ffprobe.exe")
    if os.path.exists(local_ffmpeg) and os.path.exists(local_ffprobe):
        return LOCAL_FFMPEG_DIR

    try:
        ffmpeg_result = subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True, text=True)
        ffprobe_result = subprocess.run(["ffprobe", "-version"], capture_output=True, check=True, text=True)
        return None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def install_ffmpeg():
    print("正在安装 ffmpeg...")
    install_script = os.path.join(SCRIPT_DIR, "install_ffmpeg.py")
    if os.path.exists(install_script):
        subprocess.check_call([sys.executable, install_script])
    else:
        print("错误: 找不到 install_ffmpeg.py")
        sys.exit(1)


def ensure_ffmpeg(quiet=False):
    ffmpeg_path = find_ffmpeg()
    if ffmpeg_path is not None:
        if not quiet:
            if ffmpeg_path == LOCAL_FFMPEG_DIR:
                print(f"✓ 检测到本地 ffmpeg")
            else:
                print(f"✓ 检测到系统 ffmpeg")
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


def download_video(url, output_folder="downloads", max_retries=3, max_file_size=None,
                   preview=True, quiet=False):
    """
    下载单个视频

    Args:
        url: YouTube 视频 URL
        output_folder: 输出目录
        max_retries: 最大重试次数
        max_file_size: 最大文件大小限制（字节），None 表示不限制
        preview: 是否在下载前显示视频信息
        quiet: 是否静默模式（减少输出）
    """
    os.makedirs(output_folder, exist_ok=True)

    # 确保 ffmpeg 存在
    ffmpeg_location = ensure_ffmpeg(quiet=True)

    # 创建 yt-dlp 选项
    ydl_opts = {
        "format": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080][ext=webm]+bestaudio[ext=webm]/best[ext=mp4]/best",
        "outtmpl": f"{output_folder}/%(title)s.%(ext)s",
        "noplaylist": True,
        "writethumbnail": True,
        "writesubtitles": True,
        "subtitleslangs": ["zh-Hans", "zh-Hant", "en"],
        "subtitlesformat": "srt",
        "skip_unavailable_fragments": True,
        "merge_output_format": "mp4",
        "quiet": quiet,
        "no_warnings": quiet,
        "continuedl": True,
        "fail_on_missing_subtitles": False,
        "restrictfilenames": True,
        "retries": max_retries,
    }

    if ffmpeg_location:
        ydl_opts["ffmpeg_location"] = ffmpeg_location

    # 预览视频信息
    video_title = ""
    if preview and not quiet:
        print(f"\n🔍 正在获取视频信息...")
        info = preview_video_info(yt_dlp.YoutubeDL({"quiet": True}), url)
        if info:
            video_title = info.get('title', '')

            # 检查文件大小限制
            estimated_size = estimate_file_size(info)
            if max_file_size and estimated_size and estimated_size > max_file_size:
                print(f"\n✗ 错误: 视频预估大小 {format_bytes(estimated_size)} 超过限制 {format_bytes(max_file_size)}")
                return False

            # 检查磁盘空间
            if estimated_size:
                has_space, free_space = check_disk_space(output_folder, estimated_size)
                if not has_space:
                    print(f"\n✗ 错误: 磁盘空间不足!")
                    print(f"  需要: {format_bytes(estimated_size)}")
                    print(f"  可用: {format_bytes(free_space)}")
                    return False
                else:
                    print(f"  磁盘空间: 可用 {format_bytes(free_space)} ✓")

    # 创建进度钩子
    progress = ProgressHook(title=video_title)
    ydl_opts["progress_hooks"] = [progress.progress_hook]

    # 执行下载
    for attempt in range(1, max_retries + 1):
        try:
            if not quiet:
                print(f"\n📥 开始下载 (第 {attempt} 次尝试)...")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get("title", "Unknown")

                if not quiet:
                    print(f"\n✓ 下载完成: {title}")
                    print(f"📁 保存位置: {output_folder}/")
                    print()
            return True

        except Exception as e:
            error_msg = str(e)
            if attempt < max_retries:
                wait_time = attempt * 5
                safe_print(f"\n✗ 下载失败: {error_msg}")
                safe_print(f"⏱ 将在 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            else:
                safe_print(f"\n✗ 下载失败 (已重试 {max_retries} 次): {error_msg}")
                return False


def download_video_batch(urls, output_folder="downloads", max_concurrent=3,
                         max_retries=3, max_file_size=None, preview=True):
    """
    批量下载多个视频

    Args:
        urls: YouTube 视频 URL 列表
        output_folder: 输出目录
        max_concurrent: 最大并发下载数
        max_retries: 每个视频的最大重试次数
        max_file_size: 最大文件大小限制（字节）
        preview: 是否在下载前显示视频信息
    """
    if not urls:
        print("错误: 没有提供下载 URL")
        return

    print(f"\n📋 批量下载任务")
    print(f"  视频数量: {len(urls)}")
    print(f"  并发数:   {max_concurrent}")
    print(f"  输出目录: {output_folder}")
    if max_file_size:
        print(f"  大小限制: {format_bytes(max_file_size)}")
    print("=" * 60)

    results = {"success": 0, "failed": 0, "errors": []}
    total = len(urls)

    def download_with_index(index, url):
        """带索引的下载函数，用于显示进度"""
        url_number = f"[{index + 1}/{total}]"
        print(f"\n{'=' * 60}")
        print(f"📥 {url_number} 开始下载")

        success = download_video(
            url, output_folder, max_retries,
            max_file_size, preview, quiet=False
        )

        if success:
            print(f"✓ {url_number} 下载完成")
            return index, True, None
        else:
            error = f"{url_number} 下载失败"
            print(f"✗ {error}")
            return index, False, error

    # 使用线程池并发下载
    with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
        futures = {
            executor.submit(download_with_index, i, url): i
            for i, url in enumerate(urls)
        }

        for future in as_completed(futures):
            index, success, error = future.result()
            if success:
                results["success"] += 1
            else:
                results["failed"] += 1
                if error:
                    results["errors"].append(error)

    # 打印总结
    print(f"\n{'=' * 60}")
    print("📊 下载完成总结")
    print(f"  总数:   {total}")
    print(f"  成功:   {results['success']} ✓")
    print(f"  失败:   {results['failed']}")
    if results["errors"]:
        print("\n失败列表:")
        for error in results["errors"]:
            print(f"  - {error}")
    print("=" * 60)

    return results


def parse_size(size_str):
    """解析大小字符串为字节数"""
    if not size_str:
        return None

    size_str = size_str.strip().upper()
    multipliers = {
        'B': 1,
        'K': 1024,
        'KB': 1024,
        'M': 1024 ** 2,
        'MB': 1024 ** 2,
        'G': 1024 ** 3,
        'GB': 1024 ** 3,
        'T': 1024 ** 4,
        'TB': 1024 ** 4,
    }

    for suffix, multiplier in sorted(multipliers.items(), key=lambda x: -len(x[0])):
        if size_str.endswith(suffix):
            try:
                number = float(size_str[:-len(suffix)].strip())
                return int(number * multiplier)
            except ValueError:
                return None

    # 尝试直接解析为数字（字节）
    try:
        return int(size_str)
    except ValueError:
        return None


def main():
    parser = argparse.ArgumentParser(
        description="YouTube 高清视频下载器 - 支持批量下载、进度显示、自定义路径",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 下载单个视频
  python download_youtube.py https://www.youtube.com/watch?v=xxxxx

  # 下载到自定义目录
  python download_youtube.py -o my_videos https://www.youtube.com/watch?v=xxxxx

  # 批量下载多个视频
  python download_youtube.py url1 url2 url3

  # 批量下载并设置并发数
  python download_youtube.py --concurrent 5 url1 url2 url3 url4 url5

  # 设置文件大小限制
  python download_youtube.py --max-size 1GB url1 url2

  # 仅预览视频信息，不下载
  python download_youtube.py --preview-only url1 url2
        """
    )

    parser.add_argument(
        "urls",
        nargs="+",
        help="YouTube 视频 URL（可指定多个）"
    )
    parser.add_argument(
        "-o", "--output",
        default="downloads",
        help="输出目录路径（默认: downloads）"
    )
    parser.add_argument(
        "-c", "--concurrent",
        type=int,
        default=1,
        help="并发下载数（默认: 1）"
    )
    parser.add_argument(
        "-r", "--retries",
        type=int,
        default=3,
        help="最大重试次数（默认: 3）"
    )
    parser.add_argument(
        "--max-size",
        default=None,
        help="最大文件大小限制，如 500MB, 1GB, 2GB（默认: 不限制）"
    )
    parser.add_argument(
        "--preview-only",
        action="store_true",
        help="仅预览视频信息，不下载"
    )
    parser.add_argument(
        "--no-preview",
        action="store_true",
        help="下载前不显示视频信息预览"
    )

    args = parser.parse_args()

    # 安装依赖
    install_dependencies()

    # 解析文件大小限制
    max_file_size = parse_size(args.max_size) if args.max_size else None

    # 预览模式
    if args.preview_only:
        print("👁 预览模式 - 仅显示视频信息")
        ydl_opts = {"quiet": True}
        for url in args.urls:
            info = preview_video_info(yt_dlp.YoutubeDL(ydl_opts), url)
            if info and len(args.urls) > 1:
                print()
        return

    # 检查磁盘空间（在所有下载之前）
    os.makedirs(args.output, exist_ok=True)
    has_space, free_space = check_disk_space(args.output, 0)
    if free_space:
        safe_print(f"📁 输出目录: {os.path.abspath(args.output)}")
        safe_print(f"💾 磁盘可用空间: {format_bytes(free_space)}")

    # 批量下载
    if len(args.urls) > 1 or args.concurrent > 1:
        results = download_video_batch(
            urls=args.urls,
            output_folder=args.output,
            max_concurrent=args.concurrent,
            max_retries=args.retries,
            max_file_size=max_file_size,
            preview=not args.no_preview
        )
    else:
        # 单个视频下载
        success = download_video(
            url=args.urls[0],
            output_folder=args.output,
            max_retries=args.retries,
            max_file_size=max_file_size,
            preview=not args.no_preview
        )
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()