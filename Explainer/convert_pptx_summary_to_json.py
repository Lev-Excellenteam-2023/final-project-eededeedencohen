import asyncio
from get_summary_from_gpt import get_explanation_of_text, get_titles_of_slides
from Explainer.Parser.parse_pptx_file import get_list_of_content_from_pptx_file
from Explainer.Parser.wtite_list_to_json import write_data_to_json


def convert_list_to_sections_list(summary_list: list) -> list:
    """
    @summary:
        Convert the summary list to a list of sections.
    @param summary_list:
        list: The summary list is this format: [[slide_title1, slide_summary1], [slide_title2, slide_summary2], ...]
    @return:
    """
    content_slide_separated_by_sections = [summary_list[0], summary_list[1].split("\n\n")]
    title = [content_slide_separated_by_sections[0]]
    content_slide_separated_by_list_sections = [content_slide_separated_by_sections[1][i].split("\n") for i in range(len(content_slide_separated_by_sections[1]))]
    content_slide_separated_by_list_sections.insert(0, title)
    return content_slide_separated_by_list_sections


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


async def convert_pptx_to_summary_and_write_to_json(pptx_source_path: str, json_destination_path: str, summary_topic_name: str) -> None:
    """
    @summary:
        Convert the pptx file to a summary of the slides and write the summary to a JSON file.
    @param pptx_source_path:
        The path to the pptx file.
    @param json_destination_path:
        The path to the JSON file.
    @param summary_topic_name:
        The name of the topic of the summary.
    @return:
        None
    """
    pptx_content = await convert_pptx_to_summary(pptx_source_path)
    # print(convert_list_to_sections_list(pptx_content[0]))

    converting_List_to_Section_List = [convert_list_to_sections_list(pptx_content[i]) for i in range(len(pptx_content))]
    # print(converting_List_to_Section_List)
    await write_data_to_json(converting_List_to_Section_List, json_destination_path, summary_topic_name)


# Run the async function
# asyncio.run(convert_pptx_to_summary_and_write_to_json("../files/asyncio-intro.pptx", "./asyncio-intro.json", "asyncio-intro"))










