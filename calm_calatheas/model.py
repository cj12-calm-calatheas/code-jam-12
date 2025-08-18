import json
from enum import StrEnum, auto
from functools import lru_cache
from typing import override

from pydantic import BaseModel, Field, ValidationError
from transformers import AutoModelForCausalLM, AutoTokenizer

from .logger import LOGGER


class PokemonType(StrEnum):
    """An enumeration of Pokemon types."""

    BUG = auto()
    DARK = auto()
    DRAGON = auto()
    ELECTRIC = auto()
    FAIRY = auto()
    FIGHTING = auto()
    FIRE = auto()
    FLYING = auto()
    GHOST = auto()
    GRASS = auto()
    GROUND = auto()
    ICE = auto()
    NORMAL = auto()
    POISON = auto()
    PSYCHIC = auto()
    ROCK = auto()
    STEEL = auto()
    WATER = auto()

    @classmethod
    @override
    def _missing_(cls, value: object) -> "PokemonType | None":
        """
        The model will sometimes generate types that don't match the enum exactly.

        Try normalizing the input by converting it to lowercase.
        """
        if isinstance(value, str):
            value = value.lower()

        for member in cls:
            if member.lower() == value:
                return member

        return None


class PokemonDescription(BaseModel):
    """A description of a Pokemon."""

    ability: str = Field(
        description="The primary ability of the Pokemon, which can affect its performance in battles.",
    )

    category: str = Field(
        description="The category of the Pokemon, phrased as a noun.",
    )

    flavor_text: str = Field(
        description="Flavor text to add characterization or lore to the Pokemon in question.",
        max_length=255,
    )

    habitat: str = Field(
        description="The natural habitat where the Pokemon can typically be found, phrased as a noun.",
        max_length=15,
    )

    height: float = Field(
        description="The height of the Pokemon in meters.",
    )

    name: str = Field(
        description="The creative name for the Pokemon. Avoid using real names or actual Pokemon names.",
    )

    types: set[PokemonType] = Field(
        description="The type(s) of the Pokemon.",
        max_length=2,
        min_length=1,
    )

    weight: float = Field(
        description="The weight of the Pokemon in kilograms.",
    )


MODEL_NAME = "Qwen/Qwen3-1.7B"

TOKENIZER = AutoTokenizer.from_pretrained(MODEL_NAME)
MODEL = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype="auto",
    device_map="auto",
)

DESCRIPTION_PROMPT = f"""
You are a helpful Pokemon professor.
The user is a Pokemon trainer seeking information.
The user will prompt you with a caption for a picture of a Pokemon.
Answer using the following schema: {json.dumps(PokemonDescription.model_json_schema())}
"""

REPAIR_PROMPT = f"""
You are a helpful Pokemon professor.
The input is a Pokemon description and a validation error.
The description needs to be repaired based on the error.
Leave fields not mentioned in the error unchanged.
Answer using the following schema: {json.dumps(PokemonDescription.model_json_schema())}
"""


@lru_cache
def generate_description(user_prompt: str) -> PokemonDescription:
    """Generate a Pokemon description based on the user's prompt."""
    LOGGER.debug('Generating a description based on user prompt: "%s"', user_prompt)

    messages = [
        {
            "role": "system",
            "content": DESCRIPTION_PROMPT,
        },
        {
            "role": "user",
            "content": user_prompt,
        },
    ]

    thinking_content, content = _prompt(messages)

    LOGGER.debug(thinking_content)

    try:
        result = PokemonDescription.model_validate_json(content)
    except ValidationError as e:
        result = _repair(content, e)

    return result


def _repair(content: str, validation_error: ValidationError) -> PokemonDescription:
    """Attempt to repair the given content based on the given validation error."""
    LOGGER.debug("Repairing content based on validation error: %s", validation_error)
    LOGGER.debug("Original content: %s", content)

    messages = [
        {
            "role": "system",
            "content": REPAIR_PROMPT,
        },
        {
            "role": "user",
            "content": f"Description: {content}\n\nError: {validation_error}",
        },
    ]

    thinking_content, content = _prompt(messages)

    LOGGER.debug(thinking_content)

    return PokemonDescription.model_validate_json(content)


def _prompt(messages: list[dict[str, str]]) -> tuple[str, str]:
    """Prompt the model with the given messages and return the generated text."""
    text = TOKENIZER.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=True,
    )

    model_inputs = TOKENIZER([text], return_tensors="pt").to(MODEL.device)

    # The magic numbers below taken from the model documentation, see https://huggingface.co/Qwen/Qwen3-1.7B#quickstart
    generated_ids = MODEL.generate(**model_inputs, max_new_tokens=32768)
    output_ids = generated_ids[0][len(model_inputs.input_ids[0]) :].tolist()

    try:
        index = len(output_ids) - output_ids[::-1].index(151668)
    except ValueError:
        index = 0

    thinking_content = TOKENIZER.decode(
        output_ids[:index],
        skip_special_tokens=True,
    ).strip("\n")
    content = TOKENIZER.decode(output_ids[index:], skip_special_tokens=True).strip("\n")

    return thinking_content, content
