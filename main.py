from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import requests
import secrets
from dateutil import parser
import requests
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles



app = FastAPI(
    title="Hanime API", 
    version="0.0.2", 
    description="An Unofficial API for Hanime.tv",
    docs_url="/docs",
    )

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get('/', response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": "Hanime API",
        "description": "An enhanced API for Hanime.tv content",
        "endpoints": [
            {"name": "Search", "path": "/search", "description": "Search for hentai videos"},
            {"name": "Recent", "path": "/recent", "description": "Get recently added videos"},
            {"name": "Trending", "path": "/trending", "description": "Get trending videos"},
            {"name": "Details", "path": "/details", "description": "Get video details"},
            {"name": "Watch", "path": "/play", "description": "Watch a video"},
        ]
    })

@app.get('/search')
async def search(query: str, page: int):
    res = {
        "search_text": query,
        "tags": [],
        "brands": [],
        "blacklist": [],
        "order_by": [],
        "ordering": [],
        "page": page,
    }
    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }
    x = requests.post("https://search.htv-services.com", headers=headers, json=res)
    rl = x.json()
    text = {
        "response": rl['hits'],
        "page": rl['page']
    }
    return text

@app.get('/recent')
async def recent(page: int = 0):
    url = "https://search.htv-services.com"
    res = {
        "search_text": "",
        "tags": [],
        "brands": [],
        "blacklist": [],
        "order_by": "created_at_unix",
        "ordering": "desc",
        "page": page,
    }
    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }
    x = requests.post(url, headers=headers, json=res)
    rl = x.json()
    text = {
        "response": rl['hits'],
        "page": rl['page']
    }
    return text

@app.get('/trending')
async def trending(time: str = "month", page: int = 0):
    headers = {
        "X-Signature-Version": "web2",
        "X-Signature": secrets.token_hex(32)
    }
    x = requests.get(f"https://hanime.tv/api/v8/browse-trending?time={time}&page={page}", headers=headers)
    rl = x.json()
    text = {
        "response": rl["hentai_videos"],
        "time": rl["time"],
        "page": rl["page"]
    }
    return text

@app.get('/details')
async def details(id: str):
    x = f"https://hanime.tv/api/v8/video?id={id}"
    x = requests.get(x)
    rl = x.json()
    created_at = rl["hentai_video"]["created_at"] = parser.parse(
        rl["hentai_video"]["created_at"]).strftime("%Y %m %d")
    released_date = rl["hentai_video"]["released_at"] = parser.parse(
        rl["hentai_video"]["released_at"]).strftime("%Y %m %d")
    view = rl["hentai_video"]["views"] = "{:,}".format(
        rl["hentai_video"]["views"])
    tags = rl["hentai_video"]["hentai_tags"]    
    text = {
        "query": rl["hentai_video"]["slug"],
        "name": rl["hentai_video"]["name"],
        "poster": rl["hentai_video"]["cover_url"],
        "id": rl["hentai_video"]["id"],   
        "description": rl["hentai_video"]["description"],     
        "views": view,
        "brand": rl["hentai_video"]["brand"],
        "created_at": created_at,
        "released_date": released_date,
        "is_censored": rl["hentai_video"]["is_censored"],         
        "tags": [x["text"] for x in tags]         
    }
    return text

@app.get('/link')
async def hentai_video(id: str):
    url = f"https://hanime.tv/api/v8/video?id={id}" 
    x = requests.get(url, headers={
        "X-Session-Token": "PhzIzReFsg7g2GZi-tz9KVpR2LskgMP8-l_xJ0kmbwhSuBOcD3yZJeOoQKS-ND1w3qFCGj0Y2HzfJ4renU82W25BNSVI6KnmwfiN5e9lueyQOYbZ0RVKmS2Ek1fLKvMnS_3ktEUiFOTjSCezPusemw==(-(0)-)hDLS0eC_45mNW15pn3ZJYQ==",
    })   
    rl = x.json()   
    text = {
        "data": rl["videos_manifest"]["servers"][0]["streams"]
    }
    return text

@app.get('/play')
async def play_video(link: str):
    if link.endswith('.m3u8'):
        video_type = "application/x-mpegURL"
    elif link.endswith('.mp4'):
        video_type = "video/mp4"
    else:
        return {"error": "Unsupported video format"}
    
    x = f'''
    <!DOCTYPE html>
    <html>
    <body>
    <video id="live" autoplay controls>
        <source src="{link}" type="{video_type}">
    </video>
    </body>
    </html>
    '''
    return HTMLResponse(content=x, status_code=200)


