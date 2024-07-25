import os
import yaml
import json

from openai import AzureOpenAI
from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# azure api key import
with open('/home/dongha/langchain-prac/imageGen/key.yaml') as f:
    config = yaml.safe_load(f)

api_version = config["config"]["api_version"]
azure_endpoint = config["config"]["azure_endpoint"]
api_key = config["config"]["api_key"]
default_model = config["config"]["model"]

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=azure_endpoint,
    api_key=api_key
)

app = FastAPI(debug = True)
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"])

class ImageGenRequest(BaseModel):
    message: str


@app.post("/image")
def imageGen(req: ImageGenRequest):
    result = client.images.generate(
        model = "Dalle3",
        prompt = req.message,
        n = 1)
    
    print(req.message)
    image_url = json.loads(result.model_dump_json())['data'][0]['url']

    return {"message" :image_url}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host = "0.0.0.0", port = 124)