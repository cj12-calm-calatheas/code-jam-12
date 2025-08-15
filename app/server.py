# app/server.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.calm_calatheas.services.description_generation import pokemon_card_generator

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextInput(BaseModel):
    text: str

@app.post("/generate_description/")
async def generate_description(input: TextInput):
    generated_text = pokemon_card_generator(input.text)
    return {"description": generated_text}
