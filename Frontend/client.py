import requests
import os


# Directory of the uploads folder
upload_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../Shared', 'uploads')


def upload(file_path: str) -> None:
    """
    @summary:
        Sends the appropriate HTTP request to the web app, with the file attached.
        the file will be in the body of the request with the key "file".
    @param file_path:
        The path to the file to upload - the file will be in the body of the request.
    @return:
        The UID (not the entire JSON, just the UID) from the response, if it was successful.
    @raise:
        Exception: if the path does not exist.
        Exception: if the server is down.
        Exception: if the server returned an error.
    """
    # Check if the file path exists
    if not os.path.exists(file_path):
        raise Exception('File does not exist.')

    # Prepare the request URL and data
    url = 'http://localhost:5000/upload'
    files = {'file': open(file_path, 'rb')}

    try:
        # Send the POST request
        response = requests.post(url, files=files)

        # case request was successful:
        if response.status_code == 200:
            response_json = response.json()
            return response_json.get('uid', '')

        # case an error occurred:
        elif 400 <= response.status_code < 500:
            raise Exception(response.json().get('error', ''))
        else:
            raise Exception('Server error.')

    # catch connection error:
    except requests.exceptions.ConnectionError:
        raise Exception('Server is down.')


