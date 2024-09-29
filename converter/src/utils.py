from typing import Tuple

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
