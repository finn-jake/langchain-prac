from pprint import pprint
from typing import Dict, List

from fastapi import FastAPI
from langchain import LLMChain
from langchain.chat.models import AzureChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate
from pydantic import BaseModel

app = FastAPI()

class UserRequest(BaseModel):
    genre: str
    chracters: List[Dict[str, str]]
    news_text: str

def read_prompt_template(file_path: str) -> str:
    with open(file_path, "r") as f:
        prompt_template = f.read()

    return prompt_template


@app.post("/writer")
def generate_novel(req:UserRequest) -> Dict(str, str):
    writer_llm = AzureChatOpenAI()