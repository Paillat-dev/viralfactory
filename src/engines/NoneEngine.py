from . import BaseEngine


class NoneEngine(BaseEngine):
    """
    This class represents a NoneEngine which is a subclass of BaseEngine.
    It is used when no engine is selected. It does not have any options.
    """

    num_options = 0  # The number of options available for this engine.
    name = "None"  # The name of the engine.
    description = "No engine selected"  # A brief description of the engine.

    def __init__(self, *args, **kwargs):
        """
        Constructor method for the NoneEngine class. It calls the constructor of the BaseEngine class.
        """
        super().__init__()

    @classmethod
    def get_options(cls):
        """
        This class method returns the options available for the NoneEngine.
        Since NoneEngine does not have any options, it returns an empty list.

        Returns:
            list: An empty list as there are no options for NoneEngine.
        """
        return []
