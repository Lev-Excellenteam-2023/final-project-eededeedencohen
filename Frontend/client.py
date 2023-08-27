import requests
from Frontend.status import Status
import os


# Directory of the uploads folder
upload_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../Tests/', 'files')


def upload(file_path: str) -> str:
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


def status(uid: str) -> Status:
    """
    @summary:
        Sends the appropriate HTTP request to the web app, with the UID attached to the URL.
        and returns Status object with the data from the response.
    @param uid:
        The UID of the file to get the status of.
    @return:
        Status object with the data from the response.
    @raise:
        Exception: if the server is down.
        Exception: if the server returned an error.
    """
    # Prepare the request URL and data (the UID is in the URL)
    url = 'http://localhost:5000/content/json/' + uid

    try:
        # Send the GET request
        response = requests.get(url)

        # case request was successful:
        if response.status_code == 200 or response.status_code == 202:
            """
            format of the response:
            {
                "status": "done",
                "filename": "asyncio-intro",
                "timestamp": "07-11-2023 03:23",
                "explanation": {...}
            }
            """

            response_json = response.json()
            response_status = response_json.get('status', '')
            filename = response_json.get('filename', '')
            timestamp = response_json.get('timestamp', '')
            explanation = response_json.get('explanation', '')
            return Status(response_status, filename, timestamp, explanation)

        # case 404 error:
        elif response.status_code == 404:
            response_json = response.json()
            response_status = response_json.get('status', '')
            return Status(response_status)

        # case an error occurred:
        elif 400 <= response.status_code < 500:
            # server error message: "error"
            raise Exception('Server error.')

    except requests.exceptions.ConnectionError:
        raise Exception('Server is down.')


# test upload:
# print(upload(os.path.join(upload_folder, 'asyncio-intro.pptx')))
