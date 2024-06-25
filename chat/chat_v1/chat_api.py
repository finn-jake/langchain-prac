import os

from openai import AzureOpenAI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


api_version = "2024-02-01"
azure_endpoint = "https://hatcheryopenaicanadaeast.openai.azure.com/"
api_key = "API_KEY"
model = "hatcheryOpenaiCanadaGPT4"

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=azure_endpoint,
    api_key = api_key
)


app = FastAPI(debug = True)
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)


class ChatRequest(BaseModel):
    message: str


def get_prompt_parsing_assistant():
    return "You are an assistant who helps people live their lives more energetically."

@app.post("/chat")
def chat(req: ChatRequest):
    res = client.chat.completions.create(
        model = model,
        messages = [
            {"role": "system", "content": get_prompt_parsing_assistant()},
            {"role": "user", "content": req.message}
        ]
    )

    res_ = res.choices[0].message.model_dump()["content"]
    return res_


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host = "0.0.0.0", port = 123)