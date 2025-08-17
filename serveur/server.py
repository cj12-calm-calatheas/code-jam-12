
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline


# Initialisation of model and pipeline
model_name = "google/flan-t5-large"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
generator = pipeline("text2text-generation", model=model, tokenizer=tokenizer)


def pokemon_card_generator(pokemon_name):
    prompt = f"""
Create a card for an invented Pokémon. Follow this format:
Name: 
Type:
Gender:
Size:
Weight:
Description:
"""
    if pokemon_name:
        prompt = f"Create a card for an invented Pokemon which is a {pokemon_name}. Respect this format :\nName :\nType :\nGender :\nSize :\nWeight \nDescription :"

    result = generator(prompt, max_length=150, num_return_sequences=1, do_sample=True, temperature=0.7, top_p=0.9)
    return result[0]['generated_text']

# Create FastAPI
app = FastAPI()

# We want str models
class InputText(BaseModel):
    text: str

# Endpoint for text generation
@app.post("/generate_description/")
def predict(input: InputText):
    # Here, call model to generate the response
    output = pokemon_card_generator(input.text)
    return {"description": output}