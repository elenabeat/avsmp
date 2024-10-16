import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from fractions import Fraction
from math import floor
from time import sleep

import ffmpeg

from utils import VideoInfo

global FILE_TYPES
FILE_TYPES = [".avi", ".mp4", ".m4v", ".mkv", ".mov"]

global WIDTH
WIDTH = int(os.environ["WIDTH"])
global HEIGHT
HEIGHT = int(os.environ["HEIGHT"])


class VideoPlayer:

    def __init__(
        self,
        video_file: Path,
        dither_alg: str,
        step: int,
        start: float,
        end: float,
    ) -> None:
        self.video_file = video_file
        self.dither_alg = dither_alg
        self.step = step

        # Check if video file exists and is of supported format
        self._validate_video()
        # Get video info
        self._get_video_info()
        # Check if start and end times are valid
        self._validate_start_end(start=start, end=end)

    def _validate_video(self) -> None:
        """
        Check if video file exists and is of supported format

        Raises:
            FileNotFoundError: if video file not found
            ValueError: if video file format is not supported
        """
        if not self.video_file.is_file():
            logger.error(f"Video file not found: {self.video_file}")
            raise FileNotFoundError(f"Video file not found: {self.video_file}")
        if not self.video_file.suffix in FILE_TYPES:
            logger.error(
                f"Unsupported video format: {self.video_file.suffix}, supported formats: {FILE_TYPES}"
            )
            raise ValueError(
                f"Unsupported video format: {self.video_file.suffix}, supported formats: {FILE_TYPES}"
            )

    def _get_video_info(self) -> None:
        """
        Get video info using ffmpeg and save to self.videoInfo, info includes:
        - fps: frames per second
        - duration: duration in seconds
        - frameCount: total number of frames
        - frameTime: time each frame is displayed in milliseconds
        - aspect_ratio: aspect ratio of video
        """

        probeInfo = ffmpeg.probe(self.video_file)
        stream = probeInfo["streams"][0]

        # Calculate framerate
        avg_fps = stream["avg_frame_rate"]
        fps = float(Fraction(avg_fps))

        # Calculate duration
        duration = float(probeInfo["format"]["duration"])

        # Either get frame count or calculate it
        try:
            # Get frame count for .mp4s
            frameCount = int(stream["nb_frames"])
        except KeyError:
            # Calculate frame count for .mkvs (and maybe other formats?)
            frameCount = int(duration * fps)

        # Calculate frametime (ms each frame is displayed)
        frameTime = 1000 / fps

        # Calculate aspect ratio
        aspect_ratio = int(stream["width"]) / int(stream["height"])

        # Calculate crop args, used if aspect ratio does not match screen
        if aspect_ratio > WIDTH / HEIGHT:
            crop_args = (f"ih*{WIDTH / HEIGHT}", "ih")
        else:
            crop_args = ("iw", f"iw*{HEIGHT / WIDTH}")

        self.video_info = VideoInfo(
            fps=fps,
            duration=duration,
            frameCount=frameCount,
            frameTime=frameTime,
            aspect_ratio=aspect_ratio,
            crop_args=crop_args,
        )

        logger.info(f"Video info: {self.video_info}")

    def _validate_start_end(self, start: float, end: float) -> None:
        """
        Check if start and end times are valid, start must be less than end
        and both must be less than total duration of video.

        Args:
            start (float): the start time in ms
            end (float): the end time in ms
        """

        start_frame = floor(start / self.video_info.frameTime)
        end_frame = floor(end / self.video_info.frameTime)

        assert start_frame < end_frame
        assert end_frame <= self.video_info.frameCount

        self.start_frame = start_frame
        self.end_frame = end_frame
        self.current_frame = start_frame

    def _generate_frame(self) -> None:
        """
        Generate frame at frame_idx

        Args:
            frame_idx (int): frame to generate. Must be less than total number of frames.
        """

        # Convert current frame idx to millisecond timecode
        msTimecode = f"{int(self.idx * self.video_info.frameTime)}ms"

        # Generate frame
        frame = (
            ffmpeg.input(self.video_file, ss=msTimecode)
            .filter("scale", "iw*sar", "ih")
            .filter("crop", self.video_info.crop_args[0], self.video_info.crop_args[1])
            .filter("scale", WIDTH, HEIGHT, force_original_aspect_ratio=1)
            .filter("pad", WIDTH, HEIGHT, -1, -1)
            .filter("format", "gray")
            .output("tmp/current_frame.bmp", vframes=1, copyts=None)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )

        logger.info(type(frame))

        return frame

    def play(self) -> None:

        self.playback_start = datetime.now()
        self.playback_end = self.playback_start + timedelta(
            milliseconds=self.video_info.frameTime
            * self.video_info.frameCount
            / self.step
        )

        while self.current_frame <= self.end_frame:
            self._generate_frame()
            self.current_frame += self.step
            sleep(30)


if __name__ == "__main__":
    # Setup logging
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        filename=f"logs/{os.environ['MOVIE_TITLE']}_{datetime.now().strftime('%Y-%m-%d-%H-%M')}.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filemode="w",
    )
    logger.info(f"Converting {os.environ['VIDEO_FILE']} to bmp images")

    # Initialize converter
    player = VideoPlayer(
        video_file=Path(f"videos/{os.environ['VIDEO_FILE']}"),
        dither_alg="Floyd-Steinberg",
        step=1,
        start=0,
        end=400,
    )

    player.play_video()
