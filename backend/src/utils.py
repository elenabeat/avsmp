from typing import Tuple
from datetime import datetime

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
class VideoSettings:
    """
    Dataclass for storing video settings
    """

    file_path: str
    dither_alg: str
    frame_step: int
    start_time: float
    end_time: float

    def __repr__(self):
        return f"VideoSettings(file_path={self.file_path}, dither_alg={self.dither_alg}, frame_step={self.frame_step}, start_time={self.start_time}, end_time={self.end_time})"


@dataclass
class VideoStatus(VideoSettings):
    """
    Dataclass for storing video status
    """

    current_frame: str
    playback_start: datetime
    playback_end: datetime


    def __repr__(self):
        return f"VideoStatus(message={self.message})"
