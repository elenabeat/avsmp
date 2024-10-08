import streamlit as st
import requests


def check_process()  -> None:

    button = st.button("Check Process")
    if button:
        resp = requests.get("http://localhost:5050/check-process")
        st.write(resp.json())


def start_process() -> None:

    button = st.button("Start Process")
    if button:
        resp = requests.post("http://localhost:5050/start-process")
        st.write(resp.json())


def main() -> None:

    st.title("Another Very Slow Movie Player")

    st.write("## Select a video file to play")

    video_list = get_videos()

    if video_list:
        st.selectbox(label="Select a video file", options=video_list)
    else:
        st.write("No videos found")

    start_process()
    check_process()


def get_videos() -> None:

    resp = requests.get("http://localhost:5050/list-videos")
    return resp.json()["videos"]

if __name__ == "__main__":
    st.set_page_config(
        page_title="AVSMP",
        page_icon="🎥",
        layout="centered",
        initial_sidebar_state="auto",
    )
    main()
