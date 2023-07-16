def get_unique_id(uploaded_filename: str) -> str:
    """
    @summary:
        Returns the unique id from the filename.
    @param uploaded_filename:
        str: The name of the file to process.
                The format of the filename should be:
                <original_filename>__<date>--<time>__<unique_id>.pptx
    @return:
        str: The unique id from the filename.
    """
    # remove the extension from the filename
    uploaded_filename = uploaded_filename.split('.')[0]
    return uploaded_filename.split('__')[-1]


def get_uploaded_datetime(uploaded_filename: str) -> str:
    """
    @summary:
        Returns the datetime from the filename.
        The format of the datetime is: <date>--<time>
    @param uploaded_filename:
        str: The name of the file to process.
                The format of the filename should be:
                <original_filename>__<date>--<time>__<unique_id>.pptx
    @return:
        str: The uploaded datetime from the filename.
    """
    date = uploaded_filename.split('__')[-2].split('--')[0]
    time = uploaded_filename.split('__')[-2].split('--')[1].replace('-', ':')
    return f'{date} {time}'


def get_original_filename(uploaded_filename: str) -> str:
    """
    @summary:
        Returns the original filename from the uploaded filename.
        assume that the original filename can contain '__' in it.
    @param uploaded_filename:
        str: The name of the file to process.
                The format of the filename should be:
                <original_filename>__<date>--<time>__<unique_id>.pptx
    @return:
        str: The original filename from the uploaded filename.
    """
    file_name_parts = uploaded_filename.split('__')[:-2]
    original_filename = '__'.join(file_name_parts)
    return original_filename
