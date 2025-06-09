from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
import openai

app = FastAPI()

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data model for requests
class MatchRequest(BaseModel):
    search_term: str
    movie_titles: List[str]

# Root route
@app.get("/")
def read_root():
    return {"message": "API is up"}

# Movie matching route
@app.post("/match-movies")
async def match_movies(request: MatchRequest):
    prompt = f"""
You're a helpful assistant. A user is looking for movies related to: "{request.search_term}".

From this list, choose any strong matches and explain in one sentence why they relate.

Movies:
{chr(10).join(request.movie_titles)}

Return your answer ONLY in this JSON format:
[
  {{ "title": "...", "reason": "..." }},
  ...
]
"""

    openai.api_key = os.getenv("OPENAI_API_KEY")

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You're a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    result = response.choices[0].message.content.strip()

    return {"matches": result}

