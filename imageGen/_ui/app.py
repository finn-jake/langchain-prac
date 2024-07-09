import requests
import streamlit as st
from openai import AzureOpenAI

API_BASE_URL = "http://lacalhost:124/image"

def request_image_api(
    message: str) -> str:

    resp = requests.post(
        API_BASE_URL,
        json = {
            "message" : message
        }
    )

    resp = resp.json()


def init_session_state():
    st.title("Whatever you imagine will come true")

