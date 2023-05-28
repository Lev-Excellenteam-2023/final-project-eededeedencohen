import os
import openai
from retrying import retry
from dotenv import load_dotenv
# from parse_pptx_file import get_list_of_content_from_pptx_file
import asyncio


def configure() -> None:
    """Load environment variables from .env file."""
    load_dotenv()


@retry(stop_max_attempt_number=5, wait_exponential_multiplier=1000, wait_exponential_max=10000)
def chat_completion_wrapper(model, messages):
    try:
        return openai.ChatCompletion.create(
            model=model,
            messages=messages
        )
    except openai.error.RateLimitError as e:
        print(f"RateLimitError: {e}. Retrying...")
        raise


async def get_explanation_of_text(slide_text: str) -> str:
    """
    @summary:
        Apply the GPT-3.5-turbo model to the given text and return a summary of the text.
    @param:
        slideText (str): The text to summarize. (assumed the str was taken from a pptx slide)
    @return:
        str: The summary of the text.
    @raise:
        ValueError: If the OPENAI_API_KEY environment variable is not set.
    """
    configure()
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        raise ValueError("Failed to get OpenAI API key from environment variable.")
    messages = [
        {"role": "system", "content": os.getenv("content2")},
    ]
    content = slide_text
    messages.append({"role": "system", "content": content})
    loop = asyncio.get_event_loop()
    try:
        completion = await loop.run_in_executor(None, chat_completion_wrapper, "gpt-3.5-turbo", messages)
    except openai.error.RateLimitError as e:
        print(f"RateLimitError: {e}. Retrying...")
        raise
    chat_response = completion.choices[0].message.content
    messages.append({"role": "system", "content": chat_response})
    cleaned_response = await clean_gpt_response(chat_response)
    return cleaned_response


async def clean_gpt_response(gpt_response: str) -> str:
    """
    @summary:
        Helper function for get_explanation_of_text. Get the response from GPT-3.5-turbo that is like the
        way a lecturer would explain the text and return cleaned version of the response.
    @param:
        gpt_response (str): text to summarize of the slide like the way a lecturer would explain the text.
    @return:
        str: The cleaned version of the summary of the text.
    @raise:
        ValueError: If the OPENAI_API_KEY_CLEAN_DATA environment variable is not set.
    """
    configure()
    openai.api_key = os.getenv("OPENAI_API_KEY_CLEAN_DATA")
    if not openai.api_key:
        raise ValueError("Failed to get OpenAI API key from environment variable.")
    messages = [
        {"role": "system", "content": os.getenv("content3")},
    ]
    content = gpt_response
    messages.append({"role": "system", "content": content})
    loop = asyncio.get_event_loop()
    try:
        completion = await loop.run_in_executor(None, chat_completion_wrapper, "gpt-3.5-turbo", messages)
    except openai.error.RateLimitError as e:
        print(f"RateLimitError: {e}. Retrying...")
        raise
    chat_response = completion.choices[0].message.content
    messages.append({"role": "system", "content": chat_response})
    return chat_response


async def get_titles_of_slides(slides_content: list) -> list:
    """
    @summary:
        Get the titles of the slides from the slides content.
    @param slides_content:
        list: The list of the slides content.
    @return:
        list: The list of the titles of the slides.
    """
    return [slide_content[0][0] for slide_content in slides_content]


async def convert_pptx_to_summary(pptx_path: str) -> list:
    """
    @summary:
        Convert the pptx file to a summary of the slides.
    @param pptx_path:
        str: The path to the pptx file.
    @return:
        list: The list of the summary of the slides is this format: [[slide_title1, slide_summary1], [slide_title2, slide_summary2], ...]
    @raise:
        ValueError: If the OPENAI_API_KEY environment variable is not set.
    """
    slides_content_list = await get_list_of_content_from_pptx_file(pptx_path)
    slides_titles = await get_titles_of_slides(slides_content_list)
    summary_pptx_list = []

    for slide_text in slides_content_list:
        slide_summary = asyncio.create_task(get_explanation_of_text(str(slide_text)))
        summary_pptx_list.append(slide_summary)

    await asyncio.gather(*summary_pptx_list)

    result = []
    for i, slide_summary in enumerate(summary_pptx_list):  # Here also change "slide_summary" to "task"
        result.append([slides_titles[i], slide_summary.result()])
    return result


async def main():
    pptxSlideContent = [['Parallelism'], ['Parallelism consists of performing multiple operations at the same time. Multiprocessing is a means to effect parallelism, and it entails spreading tasks over a computer’s central processing units (CPUs, or cores). '], ['Multiprocessing is well-suited for CPU-bound tasks: tightly bound for loops and mathematical computations usually fall into this category.']]
    # results = await convert_pptx_to_summary("./files/asyncio-intro.pptx")
    results = await get_explanation_of_text(str(pptxSlideContent))

    # for slide in results:
    #     print(slide[0])  # This will print the slide title
    #     print(slide[1])  # This will print the GPT explanation of the slide
    #     print("==================================")
    print(pptxSlideContent[0][0] + ":")
    print(results)

asyncio.run(main())




