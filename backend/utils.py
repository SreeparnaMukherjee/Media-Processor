import subprocess
import os
import uuid

TEMP_DIR = "temp"

def run_ffmpeg(command):
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30
        )
        if result.returncode != 0:
            raise Exception(result.stderr.decode())
    except subprocess.TimeoutExpired:
        raise Exception("FFmpeg process timed out")


def generate_filename(ext):
    return os.path.join(TEMP_DIR, f"{uuid.uuid4()}.{ext}")
