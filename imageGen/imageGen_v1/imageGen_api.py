import os

from openai import AzureOpenAI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


client = AzureOpenAI(
    api_version="2024-02-01",
    azure_endpoint="https://hatcheryopenaieastus.openai.azure.com/",
    api_key="97a434b6dfa44788b4d702dd4d38904b",
)

app = FastAPI(debug = True)
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

class ImageGenRequest(BaseModel):
    message: str


@app.post("/image")
def imageGen(req: ImageGenRequest):
    res = client
    result = client.images.generate(
        model = "Dalle3",
        prompt = req.message,
        n = 1)
    
    image_url = json.loads(result.model_dump_json())['data'][0]['url']

    return image_url


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host = "0.0.0.0", port = 124)