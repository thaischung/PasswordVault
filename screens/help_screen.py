from textual.app import ComposeResult
from textual.widgets import Static, Button
from textual.containers import Vertical
from textual.screen import Screen

class HelpScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Close")]

    def on_mount(self):
        self.query_one("#help_commands", Static).focus()

    def compose(self) -> ComposeResult:
        with Vertical(id="help_vertical"):
            yield Static("AVAILABLE COMMANDS", id="help_title")
            yield Static("[#4a5a6a]Keyboard shortcuts[/#4a5a6a]", id="help_subtitle")
            yield Static(
                "[#00b4d8]^A[/#00b4d8]  [#4a5a6a]Add Entry[/#4a5a6a]\n"
                "[#00b4d8]^E[/#00b4d8]  [#4a5a6a]Edit Entry[/#4a5a6a]\n"
                "[#00b4d8]^D[/#00b4d8]  [#4a5a6a]Delete Entry[/#4a5a6a]\n"
                "[#00b4d8]^S[/#00b4d8]  [#4a5a6a]Search[/#4a5a6a]\n"
                "[#00b4d8]^Y[/#00b4d8]  [#4a5a6a]Copy Password[/#4a5a6a]\n"
                "[#00b4d8]^U[/#00b4d8]  [#4a5a6a]Copy Username[/#4a5a6a]\n"
                "[#00b4d8]^T[/#00b4d8]  [#4a5a6a]Copy MFA Code[/#4a5a6a]\n"
                "[#00b4d8]^F[/#00b4d8]  [#4a5a6a]Toggle Favorite[/#4a5a6a]\n"
                "[#00b4d8]^C[/#00b4d8]  [#4a5a6a]Change Master Password[/#4a5a6a]\n"
                "[#00b4d8]^K[/#00b4d8]  [#4a5a6a]Delete All Entries[/#4a5a6a]\n"
                "[#00b4d8]?[/#00b4d8]   [#4a5a6a]This help screen[/#4a5a6a]\n"
                "[#00b4d8]ESC[/#00b4d8] [#4a5a6a]Close / Cancel[/#4a5a6a]",
                id="help_commands"
            )
            yield Button("Close", id="close")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close":
            self.app.pop_screen()