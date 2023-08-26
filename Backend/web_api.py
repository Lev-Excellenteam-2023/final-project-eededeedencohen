import os
from tenacity import retry, stop_after_attempt, wait_fixed
from flask import Flask, request, json
from flask_restx import Api, Resource, fields
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from DB.schema import get_status_by_uid, get_data_by_uid, add_new_pptx_file


# Initialize Flask and Flask-RESTx
app = Flask(__name__)
api = Api(app)


# File extensions
allowed_extensions = {'pptx'}


def allowed_file(filename: str) -> bool:
    """
    @summary:
        Checks if the filename has a valid extension.
    @param filename:
        The filename to check.
    @return:
        True if the filename has a valid extension, False otherwise.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


upload_parser = api.parser()
upload_parser.add_argument('file', location='files',
                           type=FileStorage, required=True)  # Add the file argument to the parser

# Define a simple model for the response data from the POST request
model = api.model('ResponseModel', {
    'id': fields.String(required=True, description='ID'),
    'message': fields.String(required=True, description='Message'),
})


@api.route('/upload', methods=['POST'])
class FileUploadResource(Resource):
    @api.expect(upload_parser)
    def post(self) -> (dict, int):
        """
        @summary:
            Uploads a file to the database.
        @param:
            file: FileStorage
                The file to upload.
        @return:
            case status code 200:
                dict: The unique ID of the file.
            case status code 400:
                dict: The error message - the body of the request is empty.
            case status code 415:
                dict: The error message - the file is not a pptx file.
        """
        if 'file' not in request.files:
            # case the body of the request is empty: no file part
            return {"error": "No file part in the request."}, 400

        file = request.files['file']
        if file.filename == '':
            # case the user does not select a file to upload
            return {"error": "No file selected for uploading"}, 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = os.path.splitext(filename)[0]
            file_content = file.read()
            uid_dictionary = add_new_pptx_file(file_content, filename)
            return uid_dictionary, 200

        else:
            # case the file is invalid (not a pptx file):
            return {"error": "Invalid file type"}, 415


# Retry up to 2 times, waiting 2 seconds between retries
@retry(stop=stop_after_attempt(2), wait=wait_fixed(2))
def find_file(uid: str) -> (dict, int):
    """
    @summary:
        Finds the file with the given unique ID.
        if the file is found in the 'outputs' folder (json file):
            -> return json format of the file.

        if the file is not found in the output's folder but found in the 'uploads' folder (pptx file):
            -> the file is still being processed.

        if the file is not found in the output's folder and not found in the 'uploads' folder:
            -> the file not found.
    @param uid:
        str: The unique ID of the file to find.
    @return:
        case status code 200:
            dict: The JSON content of the file (summary of the presentation) and status code 200.
        case status code 202:
            dict: The message "File is still being processed" and status code 202.
        case status code 404:
            dict: The message "File not found" and status code 404.
    @raise FileNotFoundError:
        If the file was not found, causing a retry.
    """
    upload_data = get_data_by_uid(uid)
    # case1: there is no file with the given unique ID:
    if upload_data is None:
        return {"status": "not found"}, 404

    # case2: the file just uploaded and not processed yet:
    elif upload_data["status"] == "pending":
        return {"status": "pending"}, 202

    # case3: the file right now is being processed:
    elif upload_data["status"] == "processing":
        return {"status": "processing"}, 202

    # case4: the file was processed successfully:
    else:
        return {
            "status": upload_data["status"],
            "filename": upload_data["filename"],
            "upload time": upload_data["upload_time"].strftime('%d %B %Y %H:%M:%S'),
            "processing end time": upload_data["finish_time"].strftime('%d %B %Y %H:%M:%S'),
            "explanation": upload_data["explanation"]
        }, 200


@api.route('/content/json/<string:uid>', methods=['GET'])
class JsonContentResource(Resource):
    def get(self, uid: str) -> (dict, int):
        """
        @summary:
            Sends get request to the server with the unique ID of the file.
            The responses are:
                200 - "done": the file was processed successfully.
                202 - "pending": the file is still being processed.
                404 - "not found": the file was not found.
        @param uid:
        """
        try:
            return find_file(uid)
        except FileNotFoundError:
            return {"message": "File not found"}, 404


def run_server(with_debug: bool) -> None:
    """
    @summary:
        Runs the server on localhost:5000.
    @param with_debug:
        bool: True if the server should run with debug, False otherwise.
        the debug mode is similar to nodemon - it restarts the server when something changes in the project (code or files).
    @return:
        None
    """
    app.run(debug=with_debug)
    print("Server is running...")


if __name__ == '__main__':
    run_server(True)  # with debug - similar to nodemon


