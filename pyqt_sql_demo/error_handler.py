class ErrorHandler(object):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_value:
            print(exc_value.message)
        return True
