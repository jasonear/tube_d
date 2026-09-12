import os
import sys
import urllib.request
import zipfile
import shutil

FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
FFMPEG_ZIP = "ffmpeg-release-essentials.zip"
FFMPEG_DIR = "ffmpeg"


def download_ffmpeg():
    if os.path.exists(os.path.join(FFMPEG_DIR, "bin", "ffmpeg.exe")):
        print("ffmpeg 已存在，跳过下载。")
        return

    print(f"正在下载 ffmpeg... ({FFMPEG_URL})")
    urllib.request.urlretrieve(FFMPEG_URL, FFMPEG_ZIP)
    print("下载完成，正在解压...")

    with zipfile.ZipFile(FFMPEG_ZIP, "r") as zip_ref:
        zip_ref.extractall("ffmpeg-temp")

    extracted_dir = os.path.join("ffmpeg-temp", os.listdir("ffmpeg-temp")[0])
    if os.path.exists(FFMPEG_DIR):
        shutil.rmtree(FFMPEG_DIR)
    shutil.move(extracted_dir, FFMPEG_DIR)
    shutil.rmtree("ffmpeg-temp")
    os.remove(FFMPEG_ZIP)

    print(f"ffmpeg 已安装到 {os.path.abspath(FFMPEG_DIR)}/bin/")


if __name__ == "__main__":
    download_ffmpeg()