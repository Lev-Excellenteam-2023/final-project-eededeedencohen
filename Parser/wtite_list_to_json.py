import json
import aiofiles
import asyncio


async def write_data_to_json(content_data: list, destination_path: str, summary_topic: str) -> None:
    """
    @summary:
        Write the content data of the slide's summary to a JSON file.
        the content data is a list of lists, where each list represents a slide.
        example for content data parameter:
            [
                [["slide 1 title"], ["section1 of slide1"], ["sectionN of slide1"]],
                [["slide 2 title"], ["section1 of slide2"], ["sectionN of slide2"]],
                ...,
                [["slide N title"], ["section1 of slideN"], ["sectionN of slideN"]]
            ]
    @param:
        list content_data: The data to write to the JSON file.
        str destination_path: The destination path of the JSON file.
        str summary_topic: The topic name of the presentation.
    @return:
        None
    """
    formatted_data = {
        "summary_topic": summary_topic,
        "slides": []
    }
    for i, slide in enumerate(content_data, start=1):
        slide_dict = {
            "slide number": i,
            "slide title": slide[0][0] if slide else "",
            "slide content": {f"section {j}": content[0] for j, content in enumerate(slide[1:], start=1)}
        }
        formatted_data["slides"].append(slide_dict)

    async with aiofiles.open(destination_path, 'w') as f:
        await f.write(json.dumps(formatted_data, indent=4))

# if __name__ == "__main__":
#     data = [
#         [["slide 1 title"], ["section1 of slide1"], ["sectionN of slide1"]],
#         [["slide 2 title"], ["section1 of slide2"], ["sectionN of slide2"]],
#         # ...,
#         [["slide N title"], ["section1 of slideN"], ["sectionN of slideN"]]
#     ]
#
#     asyncio.run(write_data_to_json(data, 'data.json', "Sample Presentation"))

