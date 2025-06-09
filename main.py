from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import openai
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# Serve static files from /frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.post("/match-movies")
async def match_movies(request: Request):
    data = await request.json()
    search_term = data.get("search_term")
    movie_titles = data.get("movie_titles", [])

    prompt = f"""
You're a helpful assistant. A user is looking for movies related to: "{search_term}".

From this list, choose any strong matches and explain in one sentence why they relate.

Movies:
{chr(10).join(movie_titles)}

Return your answer ONLY in this JSON format:
[
  {{ "title": "...", "reason": "..." }},
  ...
]
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        text = response.choices[0].message.content.strip()
        return { "matches": text }
    except Exception as e:
        return JSONResponse(status_code=500, content={ "error": str(e) })
