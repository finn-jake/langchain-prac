import os
import yaml
from pprint import pprint
from typing import Dict, List
from operator import itemgetter

from fastapi import FastAPI

from langchain_openai import AzureChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate
from langchain.chains import SequentialChain
from langchain_core.output_parsers import StrOutputParser

from pydantic import BaseModel


# API 버전, 엔드포인트 및 API 키를 설정
with open('/Users/kdh/Desktop/project/langchain-prac/key.yaml') as f:
    config = yaml.safe_load(f)


api_version = config["config"]["api_version"]
azure_endpoint = config["config"]["azure_endpoint"]
api_key = config["config"]["api_key"]
model = config["config"]["model"]


app = FastAPI(debug = True)


DEFAULT_PATH = "/Users/kdh/Desktop/project/langchain-prac/novel_chain_prac/langchain/prompt_templates"

STEP1_PROMPT_TEMPLATE = os.path.join(DEFAULT_PATH, "1_extract_idea.txt")
STEP2_PROMPT_TEMPLATE = os.path.join(DEFAULT_PATH, "2_write_outline.txt")
STEP3_PROMPT_TEMPLATE = os.path.join(DEFAULT_PATH, "3_write_plot.txt")
WRITE_PROMPT_TEMPLATE = os.path.join(DEFAULT_PATH, "6_write_chapter.txt")


class UserRequest(BaseModel):
    genre: str
    characters: List[Dict[str, str]]
    news_text: str

def read_prompt_template(file_path: str) -> str:
    with open(file_path, "r") as f:
        prompt_template = f.read()

    return prompt_template


@app.post("/writer")
def generate_novel(req:UserRequest) -> Dict[str, str]:
    writer_llm = AzureChatOpenAI(
        azure_deployment = model,
        api_version = api_version,
        azure_endpoint = azure_endpoint,
        api_key = api_key
    )

    novel_idea_template = read_prompt_template(STEP1_PROMPT_TEMPLATE)
    novel_idea_template = ChatPromptTemplate.from_template(template=novel_idea_template)
    novel_outline_template = read_prompt_template(STEP2_PROMPT_TEMPLATE)
    novel_outline_template = ChatPromptTemplate.from_template(template = novel_outline_template)
    novel_plot_template = read_prompt_template(STEP3_PROMPT_TEMPLATE)
    novel_plot_template = ChatPromptTemplate.from_template(template= novel_plot_template)
    novel_chapter_template = read_prompt_template(WRITE_PROMPT_TEMPLATE)
    novel_chapter_template = ChatPromptTemplate.from_template(template=novel_chapter_template)

    novel_idea_chain = novel_idea_template | writer_llm | StrOutputParser()

    novel_outline_chain = (
        {"novel_idea" : novel_idea_chain,
         "genre": itemgetter("genre"),
         "characters": itemgetter("characters"),
         "news_text": itemgetter("news_text")}
        | novel_outline_template | writer_llm | StrOutputParser()
    )
    novel_plot_chain = (
        {"novel_idea" : novel_idea_chain, "novel_outline" : novel_outline_chain,
         "genre": itemgetter("genre"),
         "characters": itemgetter("characters"),
         "news_text": itemgetter("news_text")}
        | novel_plot_template | writer_llm | StrOutputParser()
    )

    novel_chapter_chain = (
        {
            "novel_outline" : novel_outline_chain,
            "novel_plot" : novel_plot_chain,
            "genre": itemgetter("genre"),
            "characters": itemgetter("characters"),
            "news_text": itemgetter("news_text"),
            "chapter_number": itemgetter("chapter_number")
        } | novel_chapter_template | writer_llm | StrOutputParser()
    )

    context = req.dict()
    #context = novel_chapter_chain(context)

    context["novel_chapter"] = []
    for chapter_number in range(1, 3):
        context["chapter_number"] = chapter_number
        result = novel_chapter_chain.invoke(context)
        context["novel_chapter"].append(result)

    contents = "\n\n".join(context["novel_chapter"])
    return {"results": contents}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host = "0.0.0.0", port = 8000)
