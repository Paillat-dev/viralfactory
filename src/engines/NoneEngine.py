from . import BaseEngine


class NoneEngine(BaseEngine):
    num_options = 0
    name = "None"
    description = "No engine selected"

    def __init__(self):
        pass

    @classmethod
    def get_options(cls):
        return []
