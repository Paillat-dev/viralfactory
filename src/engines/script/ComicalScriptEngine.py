from AbstractScriptEngine import AbstractScriptEngine

class ComicalScriptEngine(AbstractScriptEngine):
    def __init__(self):
        super().__init__()
        self.options = {"comicality": ["Low", "Medium", "High"]}
