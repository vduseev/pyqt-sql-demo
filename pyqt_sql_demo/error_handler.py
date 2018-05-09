import traceback


class ErrorHandler(object):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_value:
            # If any exception happened at all
            self.handle(exc_type, exc_value, tb)
        return True

    def handle(self, exc_type, exc_value, tb):
        if hasattr(exc_value, 'message'):
            print(exc_type, exc_value.message)
            traceback.print_tb(tb)
        else:
            print(exc_type, exc_value)
            traceback.print_tb(tb)
