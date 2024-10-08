from datetime import datetime

import streamlit as st
import requests


def check_process() -> None:

    button = st.button("Check Process")
    if button:
        resp = requests.get("http://localhost:5050/check-process")
        st.write(resp.json())


def start_process() -> None:

    button = st.button("Start Process")
    if button:
        resp = requests.post("http://localhost:5050/start-process")
        st.write(resp.json())


def make_header_metrics() -> None:

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

    title_col, playing_col, progress_col, runtime_col, est_col, terminate_col = (
        st.columns([1, 1, 1, 1, 1.5, 1])
    )

    with title_col:
        with st.container():
            st.markdown(
                '<p class="dashboard_title">AVSMP<br>Dashboard</p>',
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

    with terminate_col:
        with st.container():
            st.markdown(
                f'<p class="terminate_text">⚠️ Terminate Current Movie<br></p>',
                unsafe_allow_html=True,
            )
            button = st.button("Terminate", use_container_width=True)


def main() -> None:

    make_header_metrics()

    settings_col, img_col, meta_col = st.columns([1, 2.5, 1])

    with settings_col:
        with st.container(border=True):
            st.markdown(
                '<p class="settings_title">Settings</p>',
                unsafe_allow_html=True,
            )
            st.write("Some settings will go here")

    with img_col:
        with st.container():
            st.image(
                "./41ms.jpg",
                use_column_width="always",
                caption="Current Frame",
            )

    with meta_col:
        with st.container(border=True):
            st.markdown(
                '<p class="settings_title">File Metadata</p>',
                unsafe_allow_html=True,
            )
            st.write("File metadata will go here")


    # st.title("Another Very Slow Movie Player")

    # st.write("## Select a video file to play")

    # video_list = get_videos()

    # if video_list:
    #     st.selectbox(label="Select a video file", options=video_list)
    # else:
    #     st.write("No videos found")

    # start_process()
    # check_process()


def get_videos() -> None:

    resp = requests.get("http://localhost:5050/list-videos")
    return resp.json()["videos"]


if __name__ == "__main__":
    st.set_page_config(
        page_title="AVSMP",
        page_icon="🎥",
        layout="wide",
        initial_sidebar_state="auto",
    )
    main()
