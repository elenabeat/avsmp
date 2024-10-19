from datetime import datetime
from pathlib import Path
from typing import Tuple, List

from pydantic.dataclasses import dataclass


@dataclass
class VideoInfo:
    """
    Dataclass for storing video metadata
    """

    fps: float
    duration: float
    frameCount: int
    frameTime: float
    aspect_ratio: float
    crop_args: Tuple[str, str]

    def __repr__(self):
        return f"VideoInfo(fps={self.fps}, duration={self.duration}, frameCount={self.frameCount}, frameTime={self.frameTime}, aspect_ratio={self.aspect_ratio})"


@dataclass
class PlayerStart:
    """
    Dataclass for transimitting start parameters to the player
    from the frontend.
    """
    file_path: str
    dither_alg: str
    step: int
    start: float
    end: float


@dataclass
class PlayerInfo:
    """
    Dataclass for storing player settings and current status.
    """

    file_path: Path
    dither_alg: str
    step: int
    start: float
    end: float
    start_frame: int
    end_frame: int
    current_frame: int
    playback_start: datetime
    playback_end: datetime


@dataclass
class PlayerState:
    """
    Dataclass for communicating player state to the frontend.
    """

    video_info: VideoInfo
    player_info: PlayerInfo


@dataclass
class VideoList:
    """
    Dataclass for storing video list
    """

    videos: List[Path]


