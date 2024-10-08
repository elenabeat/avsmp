import subprocess
from contextlib import asynccontextmanager
from pathlib import Path

import psutil
from fastapi import FastAPI

# Global variable to store the process
PROCESS = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI()

@app.post("/start-process")
def start_process():
    # Start the long-running process asynchronously
    global PROCESS
    PROCESS = subprocess.Popen(["python", "src/test.py"])
    return {"message": "Process started"}


@app.get("/check-process")
def check_process():
    if PROCESS is None:
        return {"message": "No process started"}
    elif PROCESS.poll() is None:
        return {"message": "Process is still running"}
    else:
        return {"message": "Process has finished"}


@app.get("/list-videos")
def list_videos():    
    video_files = [file.name for file in Path("./videos/").glob("**/*.mp4")]

    print(video_files)
    
    return {"videos": video_files}