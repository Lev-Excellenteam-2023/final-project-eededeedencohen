import asyncio
import os
from Explainer.convert_pptx_summary_to_json import convert_pptx_to_summary_and_write_to_json


async def process_pptx_file_to_json(filename: str) -> None:
    """
    @summary:
        This function checks if the file exists in the 'uploads' folder
        and if file is a pptx file, converts it to a json summary,
        writes the json to a destination path,
        and then deletes the original file.
    @param filename:
        str: The name of the file to process.
    @return:
        None
    """
    uploaded_file_path = os.path.join("../Shared/uploads", filename)

    # Process only if the file is pptx file
    if os.path.isfile(uploaded_file_path) and filename.endswith(".pptx"):
        output_filename = filename.replace(".pptx", "") + ".json"
        output_file_path = "../Shared/outputs/" + output_filename
        title_name = filename.replace(".pptx", "")

        await convert_pptx_to_summary_and_write_to_json(uploaded_file_path, output_file_path, title_name)

        input_filename = filename.replace(".pptx", "")
        os.remove("../Shared/uploads/" + input_filename + ".pptx")
        print(os.listdir("../Shared/outputs/"))


async def process_new_uploaded_files_to_json() -> None:
    """
    @summary:
        This function runs the process_file function every 10 seconds in an infinite loop.
        it checks for new pptx files in the 'uploads' folder and processes them
        in parallel.
    @return:
        None
    """
    while True:
        new_uploaded_filenames = os.listdir("../Shared/uploads")

        # Gather tasks and run them in parallel
        tasks = [process_pptx_file_to_json(file) for file in new_uploaded_filenames]
        await asyncio.gather(*tasks)

        # Wait 10 seconds
        await asyncio.sleep(10)

asyncio.run(process_new_uploaded_files_to_json())
