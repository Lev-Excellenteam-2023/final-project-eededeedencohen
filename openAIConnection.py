import os
import openai
from dotenv import load_dotenv
import asyncio


def configure() -> None:
    """Configures the OpenAI API key from the environment variables."""
    load_dotenv()


def getSummaryFromString(slideText: str) -> str:
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
    print(content)
    print(f'ChatGPT: {chat_response}')
    print("=====================================")
    messages.append({"role": "system", "content": chat_response})
    return chat_response





