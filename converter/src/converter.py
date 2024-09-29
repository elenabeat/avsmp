import logging
import os
import glob
from datetime import datetime
from pathlib import Path

global FILE_TYPES
FILE_TYPES = [".avi", ".mp4", ".m4v", ".mkv", ".mov"]


class Converter:

    def __init__(self, video_file: Path, output_dir: Path):
        self.video_file = video_file
        self.output_dir = output_dir
        self.idx = 0

        # Check if video file exists and is of supported format
        self._validate_video()
        # Check if output directory exists
        self._validate_output_dir()

    def _validate_video(self):
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

    def _validate_output_dir(self):
        if not self.output_dir.is_dir():
            self.output_dir.mkdir(parents=True)
        else:
            if os.environ.get("OVERWRITE", False).lower() == "true":
                logger.warning(
                    f"Output directory already exists: {self.output_dir}, overwriting"
                )
                for file in self.output_dir.glob('*'):
                    file.unlink()
            else:
                logger.error(f"Output directory already exists: {self.output_dir}")
                raise FileExistsError(
                    f"Output directory already exists: {self.output_dir}, if you want to overwrite set OVERWRITE=true"
                )


if __name__ == "__main__":
    logger = logging.getLogger(__name__)

    logging.basicConfig(
        filename=f"logs/{os.environ['MOVIE_TITLE']}_{datetime.now().strftime('%Y-%m-%d-%H-%M')}.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filemode="w",
    )

    logger.info(f"Converting {os.environ['VIDEO_FILE']} to bmp images")

    video_file = Path(f"videos/{os.environ['VIDEO_FILE']}")
    output_dir = Path(f"frames/{os.environ['MOVIE_TITLE']}")

    converter = Converter(video_file, output_dir)

    logger.info(f"Converter started successfully")
