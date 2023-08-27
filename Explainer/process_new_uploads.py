import asyncio
from Explainer.convert_pptx_summary_to_json import convert_pptx_bytes_to_dictionary_format_summary
from DB.schema import get_all_id_pending_files, get_pptx_bytes, change_status, insert_upload_explanation, delete_pptx_file, get_file_name, update_finish_time


async def process_uploaded_pptx(file_id: int) -> None:
    """
    @summary:
        This function take the pptx bytes from the database (by file_id),
        converts it to a dictionary format summary,
        and then writes the dictionary to the database in json format.
    @param file_id:
        int: The id of the file to process.
    @return:
        None
    """
    change_status(file_id, "processing")
    pptx_bytes = get_pptx_bytes(file_id)
    filename = get_file_name(file_id)
    explanation = await convert_pptx_bytes_to_dictionary_format_summary(pptx_bytes, filename)
    update_finish_time(file_id)
    insert_upload_explanation(file_id, explanation)
    change_status(file_id, "done")
    delete_pptx_file(file_id)


async def process_new_uploaded() -> None:
    """
    @summary:
        This function runs the process_file function every 10 seconds in an infinite loop.
        it checks for uploaded with status pending in the database and processes them
        in parallel.
    @return:
        None
    """
    while True:
        id_pending_files = get_all_id_pending_files()

        # Gather tasks and run them in parallel
        print("Processing new uploaded files...")
        tasks = [process_uploaded_pptx(file_id) for file_id in id_pending_files]
        if not tasks:
            print("No new uploaded files.")
        await asyncio.gather(*tasks)

        # Wait 10 seconds
        print("Waiting 10 seconds...")
        print("===============================================================================")
        await asyncio.sleep(10)


# def start():
#     asyncio.run(process_new_uploaded_files_to_json())
def start():
    asyncio.run(process_new_uploaded())


if __name__ == '__main__':
    start()
