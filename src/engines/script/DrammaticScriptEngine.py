from AbstractScriptEngine import AbstractScriptEngine

class DramaticScriptEngine(AbstractScriptEngine):
    def __init__(self):
        super().__init__()
        self.options = {"tone": ["Serious", "Light-hearted"]}
