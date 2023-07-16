import os
from tenacity import retry, stop_after_attempt, wait_fixed
from flask import Flask, request, json
from flask_restx import Api, Resource, fields
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from filenameCreator import create_new_filename, get_unique_id

# Initialize Flask and Flask-RESTx
app = Flask(__name__)
api = Api(app)

# Directory paths
upload_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../Shared', 'uploads')
outputs_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../Shared', 'outputs')

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
            Uploads a file to the server in the 'uploads' folder.
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
            return {"message": "No file part in the request."}, 400

        file = request.files['file']
        if file.filename == '':
            # case the user does not select a file to upload
            return {"message": "No file selected for uploading"}, 400

        if file and allowed_file(file.filename):
            # case the file is valid (pptx file):
            filename = secure_filename(file.filename)
            new_filename = create_new_filename(filename)
            file.save(os.path.join(upload_folder, new_filename))
            uid_filename = get_unique_id(new_filename)
            return {"uid": uid_filename}, 200

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

        if the file is not found in the output's folder and not found in the uploads folder:
            -> the file not found.
    @param uid:
        str: The unique ID of the file to find.
    @return:
        case status code 200:
            dict: The JSON content of the file (summary of the presentation) and status code 200.
        case status code 202:
            dict: The message "File is still being processed" and status code 202.
    @raise FileNotFoundError:
        If the file was not found, causing a retry.
    """
    # case1: the file found in the output's folder:
    return_json_filename = [filename for filename in os.listdir(outputs_folder) if filename.endswith('.json') and get_unique_id(filename) == uid]
    if len(return_json_filename) < 0:
        with open(os.path.join(outputs_folder, return_json_filename[0])) as f:
            content_summary = json.load(f)
        return content_summary, 200

    # case2: the file not found in the 'outputs' folder but found in the 'uploads' folder:
    upload_filename = [filename for filename in os.listdir(upload_folder) if filename.endswith('.pptx') and get_unique_id(filename) == uid]
    if len(upload_filename) > 0:
        return {"message": "File is still being processed"}, 202

    # Raise an exception if the file was not found, causing a retry
    raise FileNotFoundError("File not found")


@api.route('/content/json/<string:uid>', methods=['GET'])
class JsonContentResource(Resource):
    def get(self, uid: str) -> (dict, int):
        try:
            return find_file(uid)
        except FileNotFoundError:
            return {"message": "File not found"}, 404


if __name__ == '__main__':
    app.run(debug=True)


