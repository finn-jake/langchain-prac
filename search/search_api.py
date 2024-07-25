import os, json, yaml
import requests

from fastapi import FastAPI
from pydantic import BaseModel


current_direc = os.getcwd()
key_path = "search/key.yaml"

config_path = os.path.join(current_direc, key_path)

with open(config_path) as f:
    config = yaml.safe_load(f)

search_key = config["config"]["BING_SUBSCRIPTION_KEY"]
search_endpoint = config["config"]["BING_SEARCH_ENDPOINT"]
news_endpoint = config["config"]["BING_NEWS_ENDPOINT"]
image_endpoint = config["config"]["BING_IMAGE_ENDPOINT"]
video_endpoint = config["config"]["BING_VIDEO_ENDPOINT"]
suggest_endpoint = config["config"]["BING_SUGGESTION_ENDPOINT"]

class searchRequest(BaseModel):
    query: str
    search_type: str
    mkt: str

def search_news(query, mkt, key, endpoint):
    params = { 'q': query, 'mkt': mkt }
    headers = { 'Ocp-Apim-Subscription-Key': key }

    resp = requests.get(endpoint, headers, params)
    res = resp.json()['value']


@app.post("/search")
def search_news(req: searchRequest):
    if req.search_type == 'news':
        res = search_news(req.query, req.mkt, search_key, news_endpoint)

    return {"content": res}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host = "0.0.0.0", port= 125)