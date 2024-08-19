import os
import yaml
import json
import requests
from bs4 import BeautifulSoup

# OpenAI의 Azure API를 임포트
from openai import AzureOpenAI, AsyncAzureOpenAI

# FastAPI 관련 모듈을 임포트
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

# 데이터 검증을 위한 Pydantic 모델을 임포트
from pydantic import BaseModel
from typing import List,Dict

# config file 파일에서 api key 가져오기
current_direc = os.getcwd()
# GPT API 버전, 엔드포인트 및 API 키를 설정
key_path = "utils/chat_key.yaml"
config_path = os.path.join(current_direc, key_path)

with open(config_path) as f:
    config = yaml.safe_load(f)

api_version = config["config"]["api_version"]
azure_endpoint = config["config"]["azure_endpoint"]
api_key = config["config"]["api_key"]
default_model = config["config"]["model"]

# bing search api key 가져오기
key_path = "utils/search_key.yaml"
config_path = os.path.join(current_direc, key_path)


with open(config_path) as f:
    config = yaml.safe_load(f)

search_key = config["config"]["BING_SUBSCRIPTION_KEY"]
search_endpoint = config["config"]["BING_SEARCH_ENDPOINT"]

web_header = {'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
              'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3'}

# 비동기 OpenAI 클라이언트를 생성
client = AsyncAzureOpenAI(
    api_version=api_version,
    azure_endpoint=azure_endpoint,
    api_key=api_key
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "bing_search_function",
            "description": "internet searching is required to answer the question",
            "parameters": {
                "type": "object",
                "properties": {
                    "search term": {
                        "type": "string",
                        "description": "The search term",},},
                "required": ["query"],},}}]

# FastAPI 애플리케이션을 생성하고 디버그 모드를 활성화
app = FastAPI(debug=True)

# CORS 미들웨어를 추가하여 모든 도메인에서의 요청을 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"]   # 모든 헤더 허용
)

# JSON 요청의 데이터 구조를 정의하는 Pydantic 모델
class ChatRequest(BaseModel):
    #message: str
    messages : List[Dict[str, str]]
    model: str = default_model

# 시스템 메시지를 반환하는 함수
def get_prompt_parsing_assistant():
    return "You are an assistant who explains everything that people are curious about as specifically as possible."


def get_search_content(term, mkt, key, endpoint):
    params = { 'q': term, 'mkt': mkt}
    headers = { 'Ocp-Apim-Subscription-Key': key }

    resp = requests.get(endpoint, headers = headers, params=params)
    res = resp.json()

    urls, contents = [], []
    res_urls = []
    
    for web_value in res["webPages"]["value"]:
        urls.append(web_value['url'])

    for url in urls[:3]:
        try:
            res = requests.get(url, headers = web_header)
            res.raise_for_status() # 웹페이지의 상태가 정상인지 확인
            soup = BeautifulSoup(res.text, "lxml")

            contents.append(soup.text.replace('\n', ' ').replace('  ', ' '))
            res_urls.append(url)
        except:
            pass
    
    result = {"search term" : term}
    if len(contents) >= 1:
        #result = {"search term" : term}
        cnt = 0

        for idx in range(len(contents)):
            if cnt == 0:
                result["contexts"] = [{"source": res_urls[idx], "context": contents[idx]}]
                cnt += 1
            else:
                result["contexts"].append({"source": res_urls[idx], "context": contents[idx]})

    return json.dumps(result)


# 비동기 스트림 처리 함수
async def stream_processor(response):
    async for chunk in response:
        if len(chunk.choices) > 0:             # 응답에서 선택된 결과가 있는지 확인
            delta = chunk.choices[0].delta     # 첫 번째 선택의 델타를 얻음
            if delta.content:
                yield delta.content            # 델타의 콘텐츠를 스트리밍으로 반환


# 채팅 엔드포인트를 정의하는 FastAPI POST 경로
@app.post("/search_chat")
async def chat(req: ChatRequest):
    # OpenAI API에 채팅 요청을 보냅니다.
    if req.model == "gpt-4":
        model = "hatcheryOpenaiCanadaGPT4"

    elif req.model == "gpt-4o":
        model = "hatcheryOpenaiCanadaGPT4o"

    messages = req.messages
    print(req.messages[-1]['content'])

    response = await client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools,
                tool_choice="auto",)
    

    response_message = response.choices[0].message
    #messages.append(response_message)

    if response_message.tool_calls:
        messages.append(response_message)
        for tool_call in response_message.tool_calls:
            if tool_call.function.name == "bing_search_function":
                function_args = json.loads(tool_call.function.arguments)

                #search_response = get_search_content(function_args.get('search_term'))
                search_result = get_search_content(function_args.get('search term'), 'ko-KR', search_key, search_endpoint)
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role" : "tool",
                    "name" : "bing_search_function",
                    "content" : search_result
                })

    res = await client.chat.completions.create(
        model=model,
        messages=messages,
            #{"role": "system", "content": get_prompt_parsing_assistant()},  # 시스템 메시지
            #{"role": "user", "content": req.message}  # 사용자 메시지
        #temperature=0.6,
        stream=True  # 스트림 모드 사용
    )

    # 스트리밍 응답을 반환합니다.
    return StreamingResponse(stream_processor(res), media_type='text/event-stream')

# 스크립트가 메인 모듈로 실행될 때, uvicorn을 사용하여 애플리케이션을 실행합니다.
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("search_chat_api:app", host="0.0.0.0", port=126, reload = True)