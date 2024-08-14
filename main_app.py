import streamlit as st  # Streamlit을 이용하여 웹 애플리케이션을 구축
from streamlit_option_menu import option_menu

import asyncio  # 비동기 작업을 위한 asyncio 모듈
import httpx  # 비동기 HTTP 요청을 위한 httpx 모듈
from io import BytesIO
import os, requests


###################
# API 요청 함수 정의 #
###################
API_BASE_URL = "http://localhost:123/chat"  # 챗봇 API의 기본 URL
API_IMAGE_URL = "http://localhost:124/image" # 이미지 생성 URL
API_SEARCH_URL = "http://localhost:125/search" # 검색 API의 기본 URL
API_SEARCH_CHAT_URL = "http://localhost:126/search_chat"

# 챗봇 API에 요청을 보내기 위한 비동기 함수
async def request_chat_api(messages, model):
    async with httpx.AsyncClient() as client:  # 비동기 HTTP 클라이언트를 생성
        async with client.stream("POST",
                                 API_BASE_URL,
                                 json={"messages": messages, "model": model},
                                 timeout=None) as response:
            # API 응답을 스트리밍 방식으로 받음
            async for chunk in response.aiter_text():
                yield chunk  # 응답 데이터를 청크 단위로 반환

# 이미지 생성 API에 요청을 보내기 위한 함수
def request_image_api(
    message: str) -> str:

    resp = requests.post(API_IMAGE_URL, json = {"message" : message})
    resp = resp.json()

    return resp["message"]

# 검색 엔진 API에 요청을 보내기 위한 함수
def request_search_api(query, search_type, mkt):
    resp = requests.post(API_SEARCH_URL, json = {"query": query,
                                                 "search_type": search_type,
                                                 "mkt": mkt})

    resp = resp.json()
    return resp["content"]


###################
# 채팅 주요 함수 정의 #
###################
# 세션 상태를 초기화하는 함수
def init_session_state():
    #st.set_page_config(layout = "wide") # 기본 세팅을 와이드 뷰 버전으로 세팅
    st.title("🥑 Chat with GPT")  # 애플리케이션의 제목을 설정
    st.subheader(":blue[For Cho]")  # 정보글을 출력
    #st.write(":red[hi :)]")
    st.divider()

    # 모델 선택을 위한 selectbox 추가
    if "model" not in st.session_state:
        st.session_state.model = "gpt-4o"

    st.sidebar.selectbox(
        "Select Model",
        ["gpt-4", "gpt-4o"],
        key = "model")
    
    # 채팅 히스토리를 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = []  # 세션 상태에 "messages" 키를 추가하고 빈 리스트로 초기화

    # 애플리케이션 재실행 시, 기존 채팅 메시지를 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])  # 기존 메시지를 마크다운 형식으로 출력

# 챗 메시지를 처리하는 비동기 함수
async def handle_chat(message: str):
    st.session_state.messages.append({"role": "user", "content": message})  # 사용자가 보낸 메시지를 세션 상태에 추가
    with st.chat_message("user"):  # 사용자 메시지 영역을 생성
        st.markdown(message)  # 사용자의 메시지를 마크다운 형식으로 출력
    #print(message)  # 디버깅을 위해 메시지를 출력

    full_response = ""
    message_placeholder = st.empty()  # 응답 메시지를 위한 빈 공간 생성
    #async for chunk in request_chat_api(message):  # 챗봇 API로부터 응답을 청크 단위로 받음
    async for chunk in request_chat_api(st.session_state.messages, st.session_state.model):
        full_response += chunk  # 응답 청크를 누적
        message_placeholder.markdown(full_response)  # 누적된 응답을 마크다운 형식으로 출력
        await asyncio.sleep(0.01)  # 약간의 지연을 두어 비동기 처리를 원활하게 함

    st.session_state.messages.append({"role": "assistant", "content": full_response})  # 어시스턴트의 응답을 세션 상태에 추가

# 챗봇 애플리케이션의 주요 함수
def chat_main():
    init_session_state()  # 세션 상태를 초기화

    if message := st.chat_input(""):  # 챗 입력란에 입력된 메시지를 읽어옴
        loop = asyncio.new_event_loop()  # 새로운 이벤트 루프를 생성
        asyncio.set_event_loop(loop)  # 생성한 이벤트 루프를 현재 루프로 설정
        loop.run_until_complete(handle_chat(message))  # handle_chat 함수를 실행하여 사용자의 메시지를 처리


###################
# 이미지 생성 주요 함수 정의 #
###################
# 이미지 생성 세션 초기화
def init_image_session_state():
    if "generated_image_url" not in st.session_state:
        st.session_state.generated_image_url = None

# 생성 이미지 다운로드 처리 함수
def download_image(image_url: str) -> BytesIO:
    response = requests.get(image_url)
    return BytesIO(response.content)

# 이미지 생성 애플리케이션의 주요 함수
def imagegen_main():
    init_image_session_state()
    st.subheader("🪄 Image Generation \n")
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

###################
# 검색엔진 주요 함수 정의 #
###################
# 검색엔진 세션 초기화
def init_search_session_state():

    if "search_keyword" not in st.session_state:
        st.session_state.search_keyword =""

    if "search_results" not in st.session_state:
        st.session_state.search_results = None

    if "type_" not in st.session_state:
        st.session_state.type_ = "General"

    if "lang" not in st.session_state:
        st.session_state.lang = "ko-KR"

    st.sidebar.selectbox(
        "Select Search Type",
        ["General", "News", "Image"],
        key = "type_",
        index=["General", "News", "Image"].index(st.session_state.type_)
        )

    st.sidebar.selectbox(
        "Select Region/Country(MKT)",
        ["ko-KR", "en-US"],
        key = "lang",
        index=["ko-KR", "en-US"].index(st.session_state.lang)
    )
    
def handle_search(search_keyword:str):
    if st.session_state.type_ == "News":
        contents = request_search_api(search_keyword, "news", st.session_state.lang)
        st.session_state.search_results = contents

    elif st.session_state.type_ == "General":
        contents = request_search_api(search_keyword, "search", st.session_state.lang)
        st.session_state.search_results = contents

    elif st.session_state.type_ == "Image":
        contents = request_search_api(search_keyword, "image", st.session_state.lang)
        st.session_state.search_results = contents

def search_main():
    init_search_session_state()

    st.subheader("🐋 Bing Search Engine")
    prompt = st.text_input("Search Keyword:", st.session_state.search_keyword)

    if prompt != st.session_state.search_keyword:
        st.session_state.search_keyword = prompt

    if prompt.strip():
        st.session_state.search_keyword = prompt
        handle_search(prompt)

    if st.session_state.search_results:
        # 뉴스 검색 결과
        if st.session_state.type_ == "News":
            contents = st.session_state.search_results
            for content in contents:
                st.markdown(f"[{content['name']}]({content['url']})")
                st.markdown(content['description'])
                st.divider()
        
        # 일반 검색 결과
        elif st.session_state.type_ == "General":
            contents = st.session_state.search_results
            try:
                for content in contents["webPages"]["value"]:
                    st.markdown(f"[{content['name']}]({content['url']})")
                    st.markdown(content['snippet'])
                    st.divider()
            except KeyError:
                pass

            try:
                for content in contents["relatedSearches"]["value"]:
                    st.markdown(content['text'])
                    st.markdown(f"[{content['webSearchUrl']}]({content['webSearchUrl']})")
            except KeyError:
                pass

        # 이미지 검색 결과
        elif st.session_state.type_ == "Image":
            contents = st.session_state.search_results
            try:
                for content in contents["value"]:
                    st.markdown(f"[{content['name']}]({content['thumbnailUrl']})")
                    st.markdown(content['datePublished'])
                    st.divider()
            except KeyError:
                pass

###################
# 채팅 주요 함수 정의 #
###################
# 세션 상태를 초기화하는 함수
def init_schat_session_state():
    #st.set_page_config(layout = "wide") # 기본 세팅을 와이드 뷰 버전으로 세팅
    st.title("🥑 Chat with GPT Version 2")  # 애플리케이션의 제목을 설정
    st.subheader(":blue[For Smart Cho]")  # 정보글을 출력
    st.write(":red[Query -> Websearch -> answer PipeLining]")
    st.write(":red[Under Test]")
    st.divider()

    # 모델 선택을 위한 selectbox 추가
    if "model" not in st.session_state:
        st.session_state.model = "gpt-4o"

    st.sidebar.selectbox(
        "Select Model",
        ["gpt-4", "gpt-4o"],
        key = "model")
    
    # 채팅 히스토리를 초기화
    if "messages" not in st.session_state:
        st.session_state.search_messages = []  # 세션 상태에 "messages" 키를 추가하고 빈 리스트로 초기화

    # 애플리케이션 재실행 시, 기존 채팅 메시지를 표시
    for message in st.session_state.search_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])  # 기존 메시지를 마크다운 형식으로 출력

# 챗 메시지를 처리하는 비동기 함수
async def handle_search_chat(message: str):
    st.session_state.search_messages.append({"role": "user", "content": message})  # 사용자가 보낸 메시지를 세션 상태에 추가
    with st.chat_message("user"):  # 사용자 메시지 영역을 생성
        st.markdown(message)  # 사용자의 메시지를 마크다운 형식으로 출력
    #print(message)  # 디버깅을 위해 메시지를 출력

    full_response = ""
    message_placeholder = st.empty()  # 응답 메시지를 위한 빈 공간 생성
    #async for chunk in request_chat_api(message):  # 챗봇 API로부터 응답을 청크 단위로 받음
    async for chunk in request_search_chat_api(st.session_state.search_messages, st.session_state.model):
        full_response += chunk  # 응답 청크를 누적
        message_placeholder.markdown(full_response)  # 누적된 응답을 마크다운 형식으로 출력
        await asyncio.sleep(0.01)  # 약간의 지연을 두어 비동기 처리를 원활하게 함

    st.session_state.messages.append({"role": "assistant", "content": full_response})  # 어시스턴트의 응답을 세션 상태에 추가

# 챗봇 애플리케이션의 주요 함수
def search_chat_main():
    init_schat_session_state()  # 세션 상태를 초기화

    if message := st.chat_input(""):  # 챗 입력란에 입력된 메시지를 읽어옴
        loop = asyncio.new_event_loop()  # 새로운 이벤트 루프를 생성
        asyncio.set_event_loop(loop)  # 생성한 이벤트 루프를 현재 루프로 설정
        loop.run_until_complete(handle_chat(message))  # handle_chat 함수를 실행하여 사용자의 메시지를 처리 
        
###################
# 서비스 메인 함수 정의 #
###################
def main():
    #st.sidebar.title("Navigation")
    #selection = st.sidebar.radio("Go to", ['Chat', "Search Engine", "Image Generation", "Chat_v2"])

    with st.sidebar:
        selection = option_menu("Go to", ["Chat", "Search Engine", "Image Generation", "Chat_V2"],
                            icons=['chat', 'file-earmark-play', 'brush', 'activity'],
                            menu_icon="app-indicator", default_index=0,
                            styles={
            "container": {"padding": "2!important",}, #"background-color": "#134f5c"
            "icon": {"color": "#76a5af", "font-size": "20px"},
            "nav-link": {"font-size": "14px", "text-align": "left", "margin":"0px", "--hover-color": "#b1d3da"},
            "nav-link-selected": {"background-color": "#08c7b4"},})

    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    st.sidebar.markdown("<br>", unsafe_allow_html=True)

    if selection == "Chat":
        chat_main()
    elif selection == "Image Generation":
        imagegen_main()
    elif selection == "Search Engine":
        search_main()
    elif selection == "Chat_v2":
        search_chat_main()

    st.sidebar.markdown("<br>", unsafe_allow_html=True)

if __name__ == "__main__":  # 메인 스크립트로 실행될 때 (import되지 않고 직접 실행될 때)
    #chat_main()
    main()  # 챗봇 애플리케이션 시작