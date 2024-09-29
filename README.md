# Another Very Slow Movie Player (AVSMP)

This time with Docker!

## Quickstart

So far I've only implemented the python code to convert a video to `.bmp` files for the epaper display. To run that code:

1. Install docker
    - On Windows or Mac you can use [Docker Desktop](https://www.docker.com/products/docker-desktop/)
    - On Linux, see installation instructions for your distribution: https://docs.docker.com/desktop/install/linux/
2. From a terminal at `converter/` run `docker compose run --build converter`
    - Frames from `videos/test.mp4` will be written to `frames/Test Movie`

## Customize

You can change settings throught the environment variables in the `converter/docker-compose.yaml` file:
  ```yaml
  environment:
  - VIDEO_FILE=test.mp4
  - MOVIE_TITLE=Test Movie
  - WIDTH=800
  - HEIGHT=480
  - OVERWRITE=true
  ```

- `VIDEO_FILE`: name of the video file in `videos/`
- `MOVIE_TITLE`: title of the movie, used to name the directory in `frames/` where outputs will be written
- `WIDTH`: width of the display you will be using, in pixels. If video is in a different aspect ratio, then the frames will be padded appropriately
- `HEIGHT`: height of the display you will be using, in pixels. If video is in a different aspect ratio, then the frames will be padded appropriately
- `OVERWRITE`: whether to overwrite existing frames if a directory with `MOVIE_TITLE` already exists.

>[!NOTE] The code is not optimized so video files longer than ~30 seconds are not recommended at this time.
