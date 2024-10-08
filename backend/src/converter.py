import logging
import os
from datetime import datetime
from pathlib import Path
from fractions import Fraction

import ffmpeg

from utils import VideoInfo

global FILE_TYPES
FILE_TYPES = [".avi", ".mp4", ".m4v", ".mkv", ".mov"]

global WIDTH
WIDTH = int(os.environ["WIDTH"])
global HEIGHT
HEIGHT = int(os.environ["HEIGHT"])


class Converter:

    def __init__(self, video_file: Path, output_dir: Path):
        self.video_file = video_file
        self.output_dir = output_dir
        self.idx = 0

        # Check if video file exists and is of supported format
        self._validate_video()
        # Check if output directory exists
        self._validate_output_dir()
        # Get video info
        self._get_video_info()

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

    def _validate_output_dir(self) -> None:
        """
        Check if output directory exists

        Raises:
            FileExistsError: if output directory already exists and OVERWRITE is not true
        """
        if not self.output_dir.is_dir():
            self.output_dir.mkdir(parents=True)
        else:
            if os.environ.get("OVERWRITE", False).lower() == "true":
                logger.warning(
                    f"Output directory already exists: {self.output_dir}, overwriting"
                )
                for file in self.output_dir.glob("*"):
                    file.unlink()
            else:
                logger.error(f"Output directory already exists: {self.output_dir}")
                raise FileExistsError(
                    f"Output directory already exists: {self.output_dir}, if you want to overwrite set OVERWRITE=true"
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

    def _generate_frame(self, frame_idx: int) -> None:
        """
        Generate frame at frame_idx

        Args:
            frame_idx (int): frame to generate. Must be less than total number of frames.
        """

        assert frame_idx < self.video_info.frameCount

        # Convert current frame idx to millisecond timecode
        msTimecode = f"{int(self.idx * self.video_info.frameTime)}ms"

        # Generate frame
        (
            ffmpeg.input(self.video_file, ss=msTimecode)
            .filter("scale", "iw*sar", "ih")
            .filter("crop", self.video_info.crop_args[0], self.video_info.crop_args[1])
            .filter("scale", WIDTH, HEIGHT, force_original_aspect_ratio=1)
            .filter("pad", WIDTH, HEIGHT, -1, -1)
            .filter("format", "gray")
            .output(str(self.output_dir / f"{msTimecode}.bmp"), vframes=1, copyts=None)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )

    def convert_video(self) -> None:
        """
        Convert entire video to bmp images
        """

        while self.idx < self.video_info.frameCount:
            self._generate_frame(self.idx)
            self.idx += 1


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
    converter = Converter(
        video_file=Path(f"videos/{os.environ['VIDEO_FILE']}"),
        output_dir=Path(f"frames/{os.environ['MOVIE_TITLE']}"),
    )

    converter.convert_video()
