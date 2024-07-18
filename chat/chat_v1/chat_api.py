# 필요한 패키지를 임포트
import os
import yaml

# OpenAI의 Azure API를 임포트
from openai import AzureOpenAI, AsyncAzureOpenAI

# FastAPI 관련 모듈을 임포트
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

# 데이터 검증을 위한 Pydantic 모델을 임포트
from pydantic import BaseModel
from typing import List,Dict


# API 버전, 엔드포인트 및 API 키를 설정
with open('/home/dongha/langchain-prac/chat/key.yaml') as f:
    config = yaml.safe_load(f)

api_version = config["config"]["api_version"]
azure_endpoint = config["config"]["azure_endpoint"]
api_key = config["config"]["api_key"]
default_model = config["config"]["model"]


# 비동기 OpenAI 클라이언트를 생성
client = AsyncAzureOpenAI(
    api_version=api_version,
    azure_endpoint=azure_endpoint,
    api_key=api_key
)

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

# 비동기 스트림 처리 함수
async def stream_processor(response):
    async for chunk in response:
        if len(chunk.choices) > 0:               # 응답에서 선택된 결과가 있는지 확인
            delta = chunk.choices[0].delta       # 첫 번째 선택의 델타를 얻음
            if delta.content:
                yield delta.content              # 델타의 콘텐츠를 스트리밍으로 반환

# 채팅 엔드포인트를 정의하는 FastAPI POST 경로
@app.post("/chat")
async def chat(req: ChatRequest):
    # OpenAI API에 채팅 요청을 보냅니다.
    if req.model == "gpt-4":
        model = "hatcheryOpenaiCanadaGPT4"

    elif req.model == "gpt-4o":
        model = "hatcheryOpenaiCanadaGPT4o"
    
    res = await client.chat.completions.create(
        model=model,
        messages=req.messages,
            #{"role": "system", "content": get_prompt_parsing_assistant()},  # 시스템 메시지
            #{"role": "user", "content": req.message}  # 사용자 메시지
        stream=True  # 스트림 모드 사용
    )

    print(req.messages[-1]['content'])  # 사용자 메시지를 콘솔에 출력합니다.
    #res_ = res.choices[0].message.model_dump()["content"]

    # 스트리밍 응답을 반환합니다.
    return StreamingResponse(stream_processor(res), media_type='text/event-stream')

# 스크립트가 메인 모듈로 실행될 때, uvicorn을 사용하여 애플리케이션을 실행합니다.
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=123)  # localhost와 포트 123에서 실행