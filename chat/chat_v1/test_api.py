import os
from openai import AzureOpenAI
import json

import requests

api_version = "2024-02-01"
azure_endpoint = "https://hatcheryopenaicanadaeast.openai.azure.com/"
api_key = "14a3d1c6a6094c6a8950c1f1ddad33a6"
model = "hatcheryOpenaiCanadaGPT4"

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=azure_endpoint,
    api_key = api_key
)

res = client.chat.completions.create(
    model = model,
    messages = [
        {"role" : "system", "content": "You are a helpful assistant"},
        {"role" : "user", "content" : "who are you?"}
    ]
)

res_ = res.choices[0].message.model_dump()["content"]
print(res_)