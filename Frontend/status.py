from datetime import datetime


class Status:
    """
        @summary:
            A class that represents the status of a file.
        @attributes:
        status: str
            The status of processing a presentation in pptx file to summery in json file.
            The status can be one of the following:
             - "done": the file was processed successfully.
             - "pending": the file is still being processed.
             - "not found": the file was not found.
        filename: str
            The filename of the file.
        timestamp: datetime
            The timestamp when the file was uploaded.
        explanation: object
            the output as returned from the Web API.
        @methods:
        __init__(self, status: str, filename: str, timestamp: datetime, explanation: object) -> None
            Constructs a Status object.
        is_done(self) -> bool
            Returns True if the status is "done", False otherwise.
    """

    def __init__(self, status: str, filename: str, timestamp: datetime, explanation: object) -> None:
        """
        @summary:
            Constructs a Status object.
        @param status:
            str: The status of processing a presentation in pptx file to summery in json file.
        @param filename:
            str: The filename of the file.
        @param timestamp:
            datetime: The timestamp when the file was uploaded.
        @param explanation:
            object: the output as returned from the Web API.
        """
        self.status = status
        self.filename = filename
        self.timestamp = timestamp
        self.explanation = explanation

    def is_done(self) -> bool:
        """
        @summary:
            Returns True if the status is "done", False otherwise.
        @return:
            bool: True if the status is "done", False otherwise.
        """
        return self.status == "done"


