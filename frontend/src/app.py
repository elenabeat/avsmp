import logging
from datetime import datetime

import streamlit as st

from api_calls import play_video, stop_video, get_player_state, get_videos

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename="logs/frontend.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="w",
)


def header_metrics() -> (
    None
):  # TODO: update this function to use status from backend, saved as session state

    st.markdown(
        """
        <style>
            footer {display: none}
            [data-testid="stHeader"] {display: none}
        </style>
        """,
        unsafe_allow_html=True,
    )

    with open("./src/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    title_col, playing_col, progress_col, runtime_col, est_col = st.columns(
        [1, 1, 1, 1, 1.5]
    )

    with title_col:
        with st.container():
            st.markdown(
                '<p class="dashboard_title">AVSMP</p>',
                unsafe_allow_html=True,
            )

    with playing_col:
        with st.container():
            movie_title = "The Matrix"
            st.markdown(
                f'<p class="metric_text">Currently Playing<br></p><p class="value_text">{movie_title}</p>',
                unsafe_allow_html=True,
            )

    with progress_col:
        with st.container():
            progress = "5760/15000"
            st.markdown(
                f'<p class="metric_text">Current Frame<br></p><p class="value_text">{progress}</p>',
                unsafe_allow_html=True,
            )

    with runtime_col:
        with st.container():
            runtime = "240.0 hrs"
            st.markdown(
                f'<p class="metric_text">Current Runtime<br></p><p class="value_text">{runtime}</p>',
                unsafe_allow_html=True,
            )

    with est_col:
        with st.container():
            est_time = datetime.now().strftime("%c")
            st.markdown(
                f'<p class="metric_text">Fin Scheduled<br></p><p class="value_text">{est_time}</p>',
                unsafe_allow_html=True,
            )


def playback_sidebar() -> None:  # TODO : update values based on current player state

    st.markdown(
        '<p class="settings_title">Playback</p>',
        unsafe_allow_html=True,
    )

    file_path = st.selectbox(
        label="Select a video file",
        options=st.session_state["videos"],
        index=None,
    )

    dither_alg = st.selectbox(
        label="Select a dithering algorithm",
        options=["Floyd-Steinberg", "Atkinson", "Sierra", "Stucki"],
    )

    step = st.number_input(label="Frame Step", value=1, min_value=1, max_value=3600)

    start = st.number_input(
        label="Start Time (s)",
        value=0,
        min_value=0,
    )

    end = st.number_input(
        label="End Time (s)",
        value=0,
        min_value=0,
    )

    cols = st.columns(2)

    with cols[0]:
        st.session_state["play_button"] = st.button(
            label="▶️ Play", use_container_width=True
        )

        if st.session_state["play_button"]:
            resp = play_video(
                settings={
                    "file_path": file_path,
                    "dither_alg": dither_alg,
                    "step": step,
                    "start": start * 1000.0,
                    "end": end * 1000.0,
                }
            )

    with cols[1]:
        st.session_state["stop_button"] = st.button(
            label="🟥 Stop", use_container_width=True
        )


def metadata_sidebar() -> None:

    st.markdown(
        '<p class="settings_title">Now Playing</p>',
        unsafe_allow_html=True,
    )

    if st.session_state.video_info:
        st.write(st.session_state.video_info)
    else:
        st.write(
            "No video is currently playing. Once playback starts file metdata will appear here."
        )


def refresh_state() -> None:

    # Update video list
    resp = get_videos()
    if resp.status_code == 200:
        logger.info(resp.json())
        st.session_state["videos"] = resp.json()["videos"]
    else:
        logger.error(f"An error occurred when fetching available videos: {resp}")
        st.session_state["videos"] = []

    # Update player state
    resp = get_player_state()
    if resp.status_code == 200:
        logger.info(resp.json())
        st.session_state["video_info"] = resp.json()["video_info"]
        st.session_state["player_info"] = resp.json()["player_info"]
    else:
        if resp.status_code == 204:
            logger.info("No video is currently playing")
        else:
            logger.error(f"An error occurred when fetching player state: {resp}")
        st.session_state["video_info"] = None
        st.session_state["player_info"] = {
            "file_path": None,
            "dither_alg": None,
            "step": 1,
            "start": 0,
            "end": 2,
        }


def main() -> None:

    refresh_state()

    header_metrics()

    settings_col, img_col, meta_col = st.columns([1, 2.5, 1])

    with settings_col:
        with st.container(border=True):
            playback_sidebar()

    with img_col:
        with st.container():
            st.image(
                "./41ms.jpg",
                use_column_width="always",
                caption="Current Frame",
            )

    with meta_col:
        with st.container(border=True):
            metadata_sidebar()


if __name__ == "__main__":
    st.set_page_config(
        page_title="AVSMP",
        page_icon="🎥",
        layout="wide",
        initial_sidebar_state="auto",
    )
    main()
