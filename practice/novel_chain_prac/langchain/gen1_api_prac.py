# 필요한 패키지를 임포트
import yaml
from pprint import pprint
from typing import Dict, List

# FastAPI 관련 모듈을 임포트
from fastapi import FastAPI

# LangChain 관련 모듈을 임포트
from langchain_openai import AzureChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate

# 데이터 검증을 위한 Pydantic 모델을 임포트
from pydantic import BaseModel


# API 버전, 엔드포인트 및 API 키를 설정
with open('/Users/kdh/Desktop/project/langchain-prac/key.yaml') as f:
    config = yaml.safe_load(f)

api_version = config["config"]["api_version"]
azure_endpoint = config["config"]["azure_endpoint"]
api_key = config["config"]["api_key"]
model = config["config"]["model"]

# FastAPI 애플리케이션을 생성하고 디버그 모드를 활성화
app = FastAPI(debug = True)

# 요청 데이터 구조를 정의하는 Pydantic 모델 정의
class UserRequest(BaseModel):
    genre: str
    characters: List[Dict[str, str]]
    news_text: str

# 프롬프트 템플릿을 반환하는 함수
def read_prompt_template(file_path: str) -> str:
    with open(file_path, "r") as f:
        prompt_template = f.read()

    return prompt_template

# 채팅 엔드포인트를 정의하는 FastAPI POST 경로
@app.post("/writer")
def generate_novel(req:UserRequest) -> Dict[str, str]:
    writer_llm = AzureChatOpenAI(
        azure_deployment = model,
        api_version = api_version,
        azure_endpoint = azure_endpoint,
        api_key = api_key
    )
    writer_prompt_template = ChatPromptTemplate.from_template(
        template=read_prompt_template("/Users/kdh/Desktop/project/langchain-prac/novel_chain_prac/langchain/prompt_template_v1.txt")
    )

    '''    
    writer_chain = LLMChain(
        llm=writer_llm, prompt = writer_prompt_template, output_key = "output"
    )
    '''

    writer_chain = writer_prompt_template | writer_llm
    result = writer_chain.invoke(req.dict())

    return {"results": result.content}

# 스크립트 메인 모듈로 실행될 때, uvicorn을 사용하여 애플리케이션을 실행
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port = 8000)