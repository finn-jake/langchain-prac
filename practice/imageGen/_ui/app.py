import requests
import streamlit as st
import os
from io import BytesIO

API_BASE_URL = "http://localhost:124/image"

def request_image_api(
    message: str) -> str:

    resp = requests.post(API_BASE_URL, json = {"message" : message})
    resp = resp.json()

    return resp["message"]


def init_session_state():
    if "generated_image_url" not in st.session_state:
        st.session_state.generated_image_url = None
    #st.write("This is the Image Generation Page.")

def download_image(image_url: str) -> BytesIO:
    response = requests.get(image_url)
    return BytesIO(response.content)

def imagegen_main():
    init_session_state()
    st.subheader("🪄 Whatever you imagine will come :blue[TRUE] \n")
    prompt = st.text_input("Enter a prompt for image generation:")

    if st.button("Generate Image") and prompt:
        st.write(f"Generating image for prompt: {prompt}")
        generated_image_url = request_image_api(prompt)
        st.session_state.generated_image_url = generated_image_url

    if st.session_state.generated_image_url:
        st.image(st.session_state.generated_image_url, caption="Generated Image")
        
        img_bytes = download_image(st.session_state.generated_image_url)
        st.download_button(
            label="Download Image",
            data=img_bytes,
            file_name="your_imagination_is_beautiful.png",
            mime="image/png"
        )

if __name__ == "__main__":
    imagegen_main()
