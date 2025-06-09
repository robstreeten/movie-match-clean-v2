from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import openai
import os

# Load environment variables (e.g., OpenAI key)
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Create FastAPI app
app = FastAPI()

# CORS middleware: allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static frontend files from /frontend directory
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Serve the index.html at the root URL
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    try:
        with open("frontend/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    except FileNotFoundError:
        return HTMLResponse("<h1>Frontend not found</h1>", status_code=404)

# GPT-powered movie matcher endpoint
@app.post("/match-movies")
async def match_movies(request: Request):
    try:
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

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        content = response.choices[0].message.content.strip()
        return { "matches": content }

    except Exception as e:
        return JSONResponse(status_code=500, content={ "error": str(e) })
