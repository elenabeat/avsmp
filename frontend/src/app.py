from datetime import datetime

import streamlit as st
import requests


def check_process() -> None:  # TODO: update this function to use the new endpoint

    button = st.button("Check Process")
    if button:
        resp = requests.get("http://localhost:5050/check-process")
        st.write(resp.json())
    # TODO: update this function to save the status in session state


def start_process() -> None:  # TODO: update this function to use the new endpoint

    button = st.button("Start Process")
    if button:
        resp = requests.post("http://localhost:5050/start-process")
        st.write(resp.json())


def get_videos() -> None:

    resp = requests.get("http://localhost:5050/list-videos")

    return resp.json()["videos"]


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


def playback_sidebar() -> None:

    st.markdown(
        '<p class="settings_title">Playback</p>',
        unsafe_allow_html=True,
    )

    st.session_state["file_path"] = st.selectbox(
        label="Select a video file",
        options=["The Matrix.mp4", "The Matrix Reloaded.mp4"],
    )

    st.session_state["dither_alg"] = st.selectbox(
        label="Select a dithering algorithm",
        options=["Floyd-Steinberg", "Atkinson", "Sierra", "Stucki"],
    )

    st.session_state["frame_step"] = st.number_input(
        label="Frame Step", value=1, min_value=1, max_value=3600
    )

    st.session_state["start_time"] = st.number_input(
        label="Start Time (s)",
        value=0,
        min_value=0,
    )

    st.session_state["end_time"] = st.number_input(
        label="End Time (s)",
        value=0,
        min_value=0,
    )

    cols = st.columns(2)

    with cols[0]:
        st.session_state["play_button"] = st.button(
            label="▶️ Play", use_container_width=True
        )

    with cols[1]:
        st.session_state["stop_button"] = st.button(
            label="🟥 Stop", use_container_width=True
        )


def metadata_sidebar() -> None:

    st.markdown(
        '<p class="settings_title">File Metadata</p>',
        unsafe_allow_html=True,
    )

    metadata = {
        "File Name": "The Matrix.mp4",
        "File Size": "1.2 GB",
        "Resolution": "1920x1080",
        "Frame Rate": "24 fps",
        "Duration": "2:30:00",
        "Director": "The Wachowskis",
        "Year": "1999",
        "Genre": "Action",
    }

    st.write(metadata)


def main() -> None:

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
