import os
import sys
import psutil
import pytest
import subprocess
import time

from Frontend.client import upload, status

test_files_folder = os.path.join(os.path.dirname(__file__), 'test_files')

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env = os.environ.copy()  # Copy the current environment variables.
env['PYTHON-PATH'] = project_root  # Set the PYTHON-PATH environment variable to the project root.

python_path = sys.executable


@pytest.fixture
def server_process() -> subprocess.Popen:
    """
    @summary:
        This fixture starts the server process before a test and terminates it after the test.
    @return:
        A subprocess.Popen object that represents the server process.
    """
    # Start the server process
    server = subprocess.Popen([python_path, "-m", "Backend.web_api"], env=env)
    yield server

    # After the test finishes, kill the server process and its child processes
    parent = psutil.Process(server.pid)
    for child in parent.children(recursive=True):
        child.kill()
    parent.kill()


@pytest.fixture
def explainer_process() -> subprocess.Popen:
    """
       @summary:
            This fixture starts the explainer process before a test and terminates it after the test.
        @return:
            A subprocess.Popen object that represents the explainer process.
    """
    # Start the explainer process
    explainer = subprocess.Popen([python_path, "-m", "Explainer.process_new_pptx_files"], env=env)
    yield explainer

    # After the test finishes, kill the explainer process and its child processes
    parent = psutil.Process(explainer.pid)
    for child in parent.children(recursive=True):
        child.kill()
    parent.kill()


def test_system(server_process, explainer_process):
    # Upload a file
    uploaded_file_path = os.path.join(test_files_folder, 'asyncio-intro.pptx')
    uid = upload(uploaded_file_path)

    # get the explanation
    status_response = status(uid)
    while status_response.status != "done":
        status_response = status(uid)
        time.sleep(5)

    # Check the result
    assert status_response.status == "done"
    
