from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

import requests
import os
import subprocess
import uuid

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Temp directory (Render-safe)
TEMP_DIR = "/tmp"
os.makedirs(TEMP_DIR, exist_ok=True)


# Request model
class RequestModel(BaseModel):
    url: str
    operation: str


# Generate unique filename
def generate_filename(extension):
    return os.path.join(TEMP_DIR, f"{uuid.uuid4()}.{extension}")


# Download media
def download_file(url):
    local_filename = generate_filename("mp4")

    with requests.get(url, stream=True) as r:
        if r.status_code != 200:
            raise Exception("Failed to download file")

        with open(local_filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

    print(f"Downloaded: {local_filename} Size: {os.path.getsize(local_filename)}")
    return local_filename


# Main API
@app.post("/process")
def process_media(req: RequestModel):
    try:
        input_file = download_file(req.url)

        # Choose operation
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

        elif req.operation == "compress":
            output_file = generate_filename("mp4")
            command = [
                "ffmpeg",
                "-y",
                "-i", input_file,
                "-vcodec", "libx264",
                "-crf", "28",
                "-preset", "fast",
                "-movflags", "+faststart",
                "-acodec", "aac",
                "-b:a", "128k",
                output_file
            ]

        elif req.operation == "extract_audio":
            output_file = generate_filename("mp3")
            command = [
                "ffmpeg",
                "-y",
                "-i", input_file,
                "-vn",
                "-acodec", "libmp3lame",
                "-ab", "192k",
                output_file
            ]

        else:
            return {"status": "error", "message": "Invalid operation"}

        print("Running:", " ".join(command))

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=120
        )

        if result.returncode != 0:
            error_msg = result.stderr.decode()
            print("FFmpeg Error:", error_msg)
            return {
                "status": "error",
                "message": error_msg
            }

        print(f"Output: {output_file} Size: {os.path.getsize(output_file)}")

        # RETURN FILE DIRECTLY (CRITICAL FIX)
        return FileResponse(
            path=output_file,
            media_type="application/octet-stream",
            filename=os.path.basename(output_file)
        )

    except Exception as e:
        print("Error:", str(e))
        return {
            "status": "error",
            "message": str(e)
        }


# Root check
@app.get("/")
def home():
    return {"message": "Media Processor API is running"}
