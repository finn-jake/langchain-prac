import os, json, yaml
import requests

from fastapi import FastAPI
from pydantic import BaseModel


current_direc = os.getcwd()
key_path = "utils/search_key.yaml"

config_path = os.path.join(current_direc, key_path)

with open(config_path) as f:
    config = yaml.safe_load(f)

search_key = config["config"]["BING_SUBSCRIPTION_KEY"]
search_endpoint = config["config"]["BING_SEARCH_ENDPOINT"]
news_endpoint = config["config"]["BING_NEWS_ENDPOINT"]
image_endpoint = config["config"]["BING_IMAGE_ENDPOINT"]
video_endpoint = config["config"]["BING_VIDEO_ENDPOINT"]
suggest_endpoint = config["config"]["BING_SUGGESTION_ENDPOINT"]

app = FastAPI(debug=True)

class searchRequest(BaseModel):
    query: str
    search_type: str
    mkt: str

def get_news(query, mkt, key, endpoint):
    params = { 'q': query, 'mkt': mkt }
    headers = { 'Ocp-Apim-Subscription-Key': key }

    resp = requests.get(endpoint, headers=headers, params=params)
    res = resp.json()['value']

    return res

def get_search(query, mkt, key, endpoint):
    params = { 'q': query, 'mkt': mkt}
    headers = { 'Ocp-Apim-Subscription-Key': key }

    resp = requests.get(endpoint, headers = headers, params=params)
    res = resp.json()

    return res

@app.post("/search")
def search_news(req: searchRequest):
    print(req.query)

    if req.search_type == 'news':
        res = get_news(req.query, req.mkt, search_key, news_endpoint)

    elif req.search_type == "search":
        res = get_search(req.query, req.mkt, search_key, search_endpoint)

    elif req.search_type == "image":
        res = get_search(req.query, req.mkt, search_key, image_endpoint)

    return {"content": res}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host = "0.0.0.0", port= 125)