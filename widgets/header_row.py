from textual.widgets import Static
from textual.app import RenderResult
from textual.reactive import reactive
from rich.text import Text

# display the header information
class HeaderRow(Static):
    content = reactive("")

    def __init__(self, label_name: str, content: str, **kwargs):
        super().__init__(**kwargs)
        self.label_name = label_name
        self.content = content

    def render(self) -> RenderResult:
        text = Text()
        text.append(self.label_name + "\n", style="#4a5a6a")
        text.append(str(self.content), style="#00b4d8")
        return text

    def set_content(self, content):
        self.content = content