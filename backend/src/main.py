import logging
import multiprocessing
from datetime import datetime
from typing import Union
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import Response

from src.player import VideoPlayer
from src.api_data_classes import PlayerStart, PlayerState, PlayerInfo, VideoList

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename=f"logs/{datetime.now().strftime('%Y-%m-%d-%H-%M')}.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="w",
)

# Global variable to store the process
PLAYER = None
PROCESS = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI()


@app.post("/play-video")
def play_video(data: PlayerStart) -> Response:
    """
    Start playing a video using the provided parameters.

    Args:
        data (PlayerStart): The video file path and player settings.

    Returns:
        Response: A response object with status code 201.
    """
    global PLAYER
    if PLAYER is not None:
        return Response(status_code=409, content="A video is already playing.")
    else:
        PLAYER = VideoPlayer(
            file_path=Path(data.file_path),
            dither_alg=data.dither_alg,
            step=data.step,
            start=data.start,
            end=data.end,
        )

        def play_video():
            global PLAYER
            PLAYER.play()
            PLAYER = None

        global PROCESS
        PROCESS = multiprocessing.Process(target=play_video)
        PROCESS.start()

        return Response(status_code=201, content="Video playback started.")


@app.post("/stop-video")
def stop_video() -> Response:
    """
    Stop the currently playing video.

    Returns:
        Response: A response object with status code 200 if a video is playing,
            else a response object with status code 204.
    """
    global PROCESS, PLAYER
    if PROCESS is not None:
        PROCESS.terminate()
        PROCESS = None
        PLAYER = None
        return Response(status_code=200, content="Video playback stopped.")
    else:
        return Response(status_code=204, content="No video is currently playing.")


@app.get("/player-state")
def check_process() -> Union[PlayerState, Response]:
    """
    Check if a video is currently playing.

    Returns:
        Union[PlayerState, Response]: A PlayerState object if a video is playing,
            else a response object with status code 204.
    """
    if PLAYER is None:
        return Response(status_code=204, content="No video is currently playing.")
    else:
        return PlayerState(
            video_info=PLAYER.video_info,
            player_info=PlayerInfo(
                file_path=PLAYER.file_path,
                dither_alg=PLAYER.dither_alg,
                step=PLAYER.step,
                start=PLAYER.start,
                end=PLAYER.end,
                start_frame=PLAYER.start_frame,
                end_frame=PLAYER.end_frame,
                current_frame=PLAYER.current_frame,
                playback_start=PLAYER.playback_start,
                playback_end=PLAYER.playback_end,
            ),
        )


@app.get("/list-videos")
def list_videos() -> VideoList:
    """
    List all mp4 files in the videos directory.

    Returns:
        VideoList: A list of video file paths.
    """
    return VideoList(videos=list(Path("./videos/").glob("**/*.mp4"))) 
