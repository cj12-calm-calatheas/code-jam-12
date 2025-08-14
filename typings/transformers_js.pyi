class ModelOutputItem:
    generated_text: str

class ModelOutput:
    def at(self, index: int) -> ModelOutputItem: ...
