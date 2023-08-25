import asyncio
import os

from Explainer.convert_pptx_summary_to_json import convert_pptx_to_summary_and_write_to_json
from Explainer.get_data_from_filename import get_unique_id, get_original_filename, get_uploaded_datetime

base_dir = os.path.dirname(os.path.abspath(__file__))

uploads_folder = os.path.join(base_dir, '..', 'Shared', 'uploads')
uploads_folder = os.path.abspath(uploads_folder)

outputs_folder = os.path.join(base_dir, '..', 'Shared', 'outputs')
outputs_folder = os.path.abspath(outputs_folder)


async def process_pptx_file_to_json(filename: str) -> None:
    """
    @summary:
        This function checks if the file exists in the 'uploads' folder
        and if the file is a pptx file, converts it to a json summary,
        writes the json to a destination path,
        and then deletes the original file.
    @param filename:
        str: The name of the file to process.
             The format of the filename should be:
             <original_filename>__<uploaded_datetime>__<unique_id>.pptx
    @return:
        None
    """
    uploaded_file_path = os.path.join(uploads_folder, filename)

    # Process only if the file is pptx file
    if os.path.isfile(uploaded_file_path) and filename.endswith(".pptx"):

        # Extract data from the filename
        original_filename = get_original_filename(filename)
        unique_id = get_unique_id(filename)
        uploaded_datetime = get_uploaded_datetime(filename)

        output_filename = filename.replace(".pptx", "") + ".json"
        output_file_path = os.path.join(outputs_folder, output_filename)
        title_name = original_filename

        await convert_pptx_to_summary_and_write_to_json(uploaded_file_path, output_file_path, title_name)
        os.remove(uploaded_file_path)

        print(f"The file {original_filename}.pptx with the unique id: {unique_id} witch uploaded at {uploaded_datetime} was processed successfully.\n")


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
        new_uploaded_filenames = [file_name for file_name in os.listdir(uploads_folder) if file_name.endswith('.pptx')]

        # Gather tasks and run them in parallel
        print("Processing new uploaded files...")
        tasks = [process_pptx_file_to_json(file) for file in new_uploaded_filenames]
        if not tasks:
            print("No new uploaded files.")
        await asyncio.gather(*tasks)

        # Wait 10 seconds
        print("Waiting 10 seconds...")
        print("===============================================================================")
        await asyncio.sleep(10)


def start():
    asyncio.run(process_new_uploaded_files_to_json())


if __name__ == '__main__':
    start()
