from typing import Dict, Union
import logging

import requests
from requests import Response

logger = logging.getLogger(__name__)


def play_video(settings: Dict[str, Union[str, int, float]]) -> Response:
    """
    Sends a POST request to play a video with the given settings.

    Args:
        settings (Dict[str, Union[str, int, float]]): A dictionary containing the following key-value pairs:
            - 'file_path' (str): path to video file to play
            - 'dither_alg' (str): dithering algorithm to use
            - 'step' (int): the number of frames to advance with each refresh
            - 'start' (float): start time in ms
            - 'end' (float): end time in ms

    Returns:
        Response: response from the backend. Will have status code 201 if playback started successfully.
            Will instead have status code 409 if playback failed because a video is already playing.
    """
    resp = requests.post("http://localhost:5050/play-video", json=settings)
    return resp


def stop_video() -> Response:
    """
    Sends a POST request to stop the currently playing video.

    Returns:
        Response: response from the backend. Will have status code 200 if video
            is stopped successfully. Will instead have status code 204 if no video
            is currently playing.
    """

    resp = requests.post("http://localhost:5050/stop-video")
    return resp


def get_player_state() -> Response:
    """
    Sends a GET request to get the state of the current player.

    Returns:
        Response: response from the backend. Will have status code 200 and a json
            response if a video is currently playing. Will instead have status code
            204 if no video is currently playing.
    """

    resp = requests.get("http://localhost:5050/player-state")
    return resp


def get_videos() -> Response:
    """
    Sends a GET request to get the list of videos available for playback.

    Returns:
        Response: response from the backend. Will have status code 200 and a json
            response containing a list of video file paths.
    """

    resp = requests.get("http://localhost:5050/list-videos")
    return resp
