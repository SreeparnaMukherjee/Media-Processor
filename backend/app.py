from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
import requests
import os
import subprocess
import uuid
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Temp directory
TEMP_DIR = "/tmp"
os.makedirs(TEMP_DIR, exist_ok=True)


class RequestModel(BaseModel):
    url: str
    operation: str


def generate_filename(ext):
    return os.path.join(TEMP_DIR, f"{uuid.uuid4()}.{ext}")


# ✅ STRONG DOWNLOAD FIX
def download_file(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, stream=True, timeout=30)

    if response.status_code != 200:
        raise Exception("Failed to download file")

    file_path = generate_filename("mp4")

    with open(file_path, "wb") as f:
        for chunk in response.iter_content(1024 * 1024):
            if chunk:
                f.write(chunk)

    size = os.path.getsize(file_path)
    print("Downloaded:", file_path, "Size:", size)

    if size < 100000:  # <100KB means broken download
        raise Exception("Downloaded file is too small / corrupted")

    return file_path


# ✅ SAFE FFMPEG RUN
def run_ffmpeg(command):
    print("Running:", " ".join(command))

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    stdout, stderr = process.communicate()

    if process.returncode != 0:
        print(stderr.decode())
        raise Exception("FFmpeg failed")

@app.get("/media/{filename}")
def get_media(filename: str):
    file_path = os.path.join(TEMP_DIR, filename)

    if not os.path.exists(file_path):
        return {"error": "File not found"}

    return FileResponse(
        path=file_path,
        media_type="application/octet-stream",
        filename=filename
    )

@app.post("/process")
def process_media(req: RequestModel):
    try:
        input_file = download_file(req.url)

        # ----------------------------
        # THUMBNAIL
        # ----------------------------
        if req.operation == "thumbnail":
            output_file = generate_filename("jpg")

            command = [
                "ffmpeg",
                "-y",
                "-ss", "00:00:02",
                "-i", input_file,
                "-frames:v", "1",
                output_file
            ]

        # ----------------------------
        # VIDEO COMPRESS (STRICT FIX)
        # ----------------------------
        elif req.operation == "compress":
            output_file = generate_filename("mp4")

            command = [
                "ffmpeg",
                "-y",
                "-i", input_file,
                "-c:v", "libx264",
                "-profile:v", "baseline",
                "-level", "3.0",
                "-pix_fmt", "yuv420p",
                "-preset", "medium",
                "-crf", "23",
                "-c:a", "aac",
                "-b:a", "128k",
                "-movflags", "+faststart",
                output_file
            ]

        # ----------------------------
        # AUDIO EXTRACT (STRICT FIX)
        # ----------------------------
        elif req.operation == "extract_audio":
            output_file = generate_filename("mp3")

            command = [
                "ffmpeg",
                "-y",
                "-i", input_file,
                "-vn",
                "-acodec", "libmp3lame",
                "-ab", "192k",
                "-ar", "44100",
                "-f", "mp3",
                output_file
            ]

        else:
            return {"status": "error", "message": "Invalid operation"}

        # Run FFmpeg
        run_ffmpeg(command)

        # Validate output
        size = os.path.getsize(output_file)
        print("Output:", output_file, "Size:", size)

        if size < 1000:
            raise Exception("Output file corrupted")

        return {
            "status": "success",
            "output": os.path.basename(output_file)
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
