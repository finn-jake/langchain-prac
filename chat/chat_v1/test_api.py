import os
import yaml
from openai import AzureOpenAI
import json

import requests

with open('/home/dongha/langchain-prac/chat/key.yaml') as f:
    config = yaml.safe_load(f)

api_version = config["config"]["api_version"]
azure_endpoint = config["config"]["azure_endpoint"]
api_key = config["config"]["api_key"]
model = config["config"]["model"]

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