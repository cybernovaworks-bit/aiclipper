import os
import asyncio
import subprocess
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp
import whisper

app = FastAPI(title="AI Clipper API", description="Backend for processing YouTube videos into shorts")

# Configure CORS so the frontend can communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    url: str
    subtitle_style: str = "none"

# 10 Viral Subtitle Styles (FFmpeg force_style formats)
SUBTITLE_STYLES = {
    "viral_yellow": "FontName=Arial,FontSize=24,PrimaryColour=&H0000FFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=3,Shadow=0",
    "classic_white": "FontName=Arial,FontSize=22,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=1",
    "neon_green": "FontName=Arial,FontSize=24,PrimaryColour=&H0000FF00,OutlineColour=&H00000000,BorderStyle=1,Outline=3,Shadow=0",
    "cinematic_box": "FontName=Arial,FontSize=20,PrimaryColour=&H00FFFFFF,BorderStyle=3,Outline=1,BackColour=&H80000000",
    "bold_red": "FontName=Arial,FontSize=26,PrimaryColour=&H000000FF,OutlineColour=&H00000000,BorderStyle=1,Outline=3,Shadow=1",
    "pop_art_pink": "FontName=Arial,FontSize=26,PrimaryColour=&H00FF00FF,OutlineColour=&H00FFFFFF,BorderStyle=1,Outline=3,Shadow=2",
    "hacker_terminal": "FontName=Consolas,FontSize=20,PrimaryColour=&H0000FF00,BorderStyle=1,Outline=1,Shadow=0",
    "minimalist": "FontName=Arial,FontSize=20,PrimaryColour=&H00FFFFFF,BorderStyle=1,Outline=0,Shadow=1",
    "blue_glow": "FontName=Arial,FontSize=24,PrimaryColour=&H00FFFF00,OutlineColour=&H00FF0000,BorderStyle=1,Outline=3,Shadow=2",
    "high_contrast": "FontName=Arial,FontSize=22,PrimaryColour=&H00000000,BorderStyle=3,Outline=1,BackColour=&H00FFFFFF"
}

os.makedirs("temp", exist_ok=True)
os.makedirs("static/clips", exist_ok=True)

# Load Whisper model globally to avoid reloading (using 'tiny' or 'base' for speed)
try:
    print("Loading Whisper model...")
    whisper_model = whisper.load_model("tiny")
    print("Whisper model loaded!")
except Exception as e:
    print(f"Error loading whisper model: {e}")
    whisper_model = None

def download_youtube_video(url: str, output_path: str):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def transcribe_audio_to_srt(video_path: str, srt_path: str):
    if not whisper_model:
        return
    result = whisper_model.transcribe(video_path)

    # Simple SRT generation
    with open(srt_path, "w", encoding="utf-8") as srt_file:
        for i, segment in enumerate(result["segments"]):
            start = segment["start"]
            end = segment["end"]
            text = segment["text"].strip()

            # Format time for SRT: HH:MM:SS,mmm
            def format_time(seconds):
                h = int(seconds // 3600)
                m = int((seconds % 3600) // 60)
                s = int(seconds % 60)
                ms = int((seconds - int(seconds)) * 1000)
                return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

            srt_file.write(f"{i+1}\n")
            srt_file.write(f"{format_time(start)} --> {format_time(end)}\n")
            srt_file.write(f"{text}\n\n")

def process_clip(input_video: str, output_video: str, srt_path: str, style_key: str):
    # Cut first 59 seconds and crop to 9:16

    # Avoid path backslash issues in FFmpeg filter by replacing them
    safe_srt_path = srt_path.replace('\\', '/')

    vf_filters = "crop=ih*(9/16):ih"

    if style_key != "none" and style_key in SUBTITLE_STYLES:
        style_string = SUBTITLE_STYLES[style_key]
        vf_filters += f",subtitles={safe_srt_path}:force_style='{style_string}'"

    cmd = [
        "ffmpeg", "-y",
        "-i", input_video,
        "-t", "59",
        "-vf", vf_filters,
        "-c:a", "copy",
        output_video
    ]

    print(f"Running FFmpeg: {' '.join(cmd)}")
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

@app.get("/")
def read_root():
    return {"message": "AI Clipper Backend is running!"}

@app.post("/process-video")
async def process_video(request: VideoRequest):
    url = request.url
    style = request.subtitle_style

    if "youtube.com" not in url and "youtu.be" not in url:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    print(f"Received request to process: {url} with style {style}")

    video_id = "clip_test"  # In a real app, generate a UUID or use YouTube ID
    temp_video = f"temp/{video_id}.mp4"
    temp_srt = f"temp/{video_id}.srt"
    final_clip = f"static/clips/{video_id}_final.mp4"

    try:
        print("1. Downloading video...")
        # For actual use, download the real video.
        # Uncomment the line below to actually download (might take a long time in testing)
        # await asyncio.to_thread(download_youtube_video, url, temp_video)

        # To avoid making this test take 10 minutes to download and process a real video,
        # we'll simulate the downloaded video by generating a small blank video with FFmpeg.
        if not os.path.exists(temp_video):
            print("Generating a test video (to simulate download)...")
            subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "testsrc=duration=60:size=1280x720:rate=30", "-f", "lavfi", "-i", "sine=frequency=1000:duration=60", "-c:v", "libx264", "-c:a", "aac", temp_video], check=True)

        print("2. Transcribing with Whisper...")
        # In a real scenario, this processes the audio.
        # await asyncio.to_thread(transcribe_audio_to_srt, temp_video, temp_srt)

        # Simulating SRT creation for the dummy video
        if not os.path.exists(temp_srt):
            with open(temp_srt, "w", encoding="utf-8") as f:
                f.write("1\n00:00:01,000 --> 00:00:05,000\nThis is a viral hook!\n\n")
                f.write("2\n00:00:05,500 --> 00:00:10,000\nNotice the amazing subtitle style.\n\n")

        print("3. Cropping and Burning Subtitles...")
        await asyncio.to_thread(process_clip, temp_video, final_clip, temp_srt, style)

        # Simulating a slightly longer wait for the UI demo
        await asyncio.sleep(2)

        return {
            "status": "success",
            "original_url": url,
            "clips": [
                {
                    "id": "clip_1",
                    "title": "Viral Hook Generated",
                    "score": "99/100 Viral Score",
                    "videoUrl": "https://www.w3schools.com/html/mov_bbb.mp4" # Kept as placeholder so UI still plays something without hosting setup
                }
            ]
        }
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    import os
    # Default to 8000 for Koyeb, otherwise use the PORT environment variable
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)