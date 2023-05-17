import os
import openai
from dotenv import load_dotenv


def configure() -> None:
    """Load environment variables from .env file."""
    load_dotenv()


def get_summary_rom_String(slideText: str) -> str:
    """
    Apply the GPT-3.5-turbo model to the given text and return a summary of the text.
    :param:
        slideText (str): The text to summarize. (assumed the str was taken from a pptx slide)
    :return:
        str: The summary of the text.
    Raises:
        ValueError: If the OPENAI_API_KEY environment variable is not set.
    """
    configure()
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        raise ValueError("Failed to get OpenAI API key from environment variable.")
    messages = [
        {"role": "system", "content": os.getenv("content")},
    ]
    content = slideText
    messages.append({"role": "system", "content": content})
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    chat_response = completion.choices[0].message.content
    messages.append({"role": "system", "content": chat_response})
    return chat_response







