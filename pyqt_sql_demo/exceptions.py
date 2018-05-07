class Error(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, message):
        self.message = message


class FileError(Error):
    """Base class for exceptions related to files."""

    def __init__(self, filename, message):
        self.filename = filename
        super().__init__(message)


class FileNotFoundError(FileError):
    def __init__(self, filename):
        super().__init__(
            filename,
            'File {} is not found or is unaccessible'.format(filename)
        )
