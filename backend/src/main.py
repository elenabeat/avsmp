import subprocess
import threading
import multiprocessing
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from utils import VideoSettings, VideoStatus
from player import VideoPlayer

# Global variable to store the process
PLAYER = None
PROCESS = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI()


@app.post("/play-video")
def play_video(data: VideoSettings):

    global PLAYER
    PLAYER = VideoPlayer(
        video_file=Path(data.file_path),
        dither_alg=data.dither_alg,
        step=data.frame_step,
        start=data.start_time,
        end=data.end_time,
    )

    def play_video():
        global PLAYER
        PLAYER.play()
        PLAYER = None

    global PROCESS
    PROCESS = multiprocessing.Process(target=play_video)
    PROCESS.start()

    return {"message": "Video is playing"}


@app.post("/stop-video")
def stop_video():
    global PROCESS, PLAYER
    if PROCESS is not None:
        PROCESS.terminate()
        PROCESS = None
        PLAYER = None
        return {"message": "Video stopped"}
    else:
        return {"message": "No video playing"}


@app.get("/player-status")
def check_process() -> VideoStatus:
    if PLAYER is None:
        return {"message": "No video playing"}
    else:
        pass


@app.get("/list-videos")
def list_videos():
    video_files = [file.name for file in Path("./videos/").glob("**/*.mp4")]

    print(video_files)

    return {"videos": video_files}
