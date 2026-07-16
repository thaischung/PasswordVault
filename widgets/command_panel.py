from textual.app import ComposeResult
from textual.widgets import Static
from textual.widget import Widget
from rich.table import Table

# display the different commands that the user has access to
class CommandPanel(Widget):
    def compose(self) -> ComposeResult:
        yield Static(id="command_table")

    def on_mount(self) -> None:
        self.border_title = "COMMANDS"
        table = Table(box=None, show_header=False)
        table.add_row("[^A] Add", "[^E] Edit", "[^D] Delete", "[^S] Search", "[^Y] Copy Pass", "[^T] Copy MFA", "[?] Help")
        self.query_one("#command_table", Static).update(table)
