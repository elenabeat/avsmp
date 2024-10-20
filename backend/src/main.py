import logging
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Union

from fastapi import FastAPI, Request, status
from fastapi.responses import Response, JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi_utils.tasks import repeat_every

from src.player import VideoPlayer
from src.api_data_classes import PlayerStart, PlayerState, PlayerInfo, VideoList

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename="logs/backend.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="w",
)

# Global variable to track of currently playing video
PLAYER = None


app = FastAPI()


@app.on_event("startup")
@repeat_every(seconds=30, logger=logger)
def advance_video() -> None:
    global PLAYER
    if PLAYER:
        if PLAYER.playing:
            if PLAYER.current_frame <= PLAYER.end_frame:
                PLAYER.generate_frame()
                PLAYER.current_frame += 1
                logger.info(PLAYER)
            else:
                PLAYER = None
    else:
        logger.info("Nothing is currently playing")


@app.exception_handler(RequestValidationError)
async def custom_form_validation_error(request: Request, exc: RequestValidationError):
    reformatted_message = defaultdict(list)
    for pydantic_error in exc.errors():
        loc, msg = pydantic_error["loc"], pydantic_error["msg"]
        filtered_loc = loc[1:] if loc[0] in ("body", "query", "path") else loc
        field_string = ".".join(filtered_loc)  # nested fields with dot-notation
        reformatted_message[field_string].append(msg)

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder(
            {"detail": "Invalid request", "errors": reformatted_message}
        ),
    )


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

        PLAYER.play()

        return Response(status_code=201)


@app.post("/stop-video")
def stop_video() -> Response:
    """
    Stop the currently playing video.

    Returns:
        Response: A response object with status code 200 if a video is playing,
            else a response object with status code 204.
    """
    global PLAYER
    if PLAYER is not None:
        PLAYER = None
        return Response(status_code=200, content="Video playback stopped.")
    else:
        return Response(status_code=204)


@app.get("/player-state", response_model=None)
def player_state() -> Union[PlayerState, Response]:
    """
    Check if a video is currently playing.

    Returns:
        Union[PlayerState, Response]: A PlayerState object if a video is playing,
            else a response object with status code 204.
    """
    global PLAYER
    if PLAYER:
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
    else:
        return Response(status_code=204)


@app.get("/list-videos")
def list_videos() -> VideoList:
    """
    List all mp4 files in the videos directory.

    Returns:
        VideoList: A list of video file paths.
    """
    return VideoList(videos=list(Path("./videos/").glob("**/*.mp4")))
