from textual.app import ComposeResult
from textual.widgets import Static, Input, Button
from textual.containers import Vertical, Horizontal
from textual.screen import Screen

class ConfirmationScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Cancel"),
        ("enter", "save", "Save"),
    ]

    def __init__(self, message, callback, user_db, **kwargs):
        super().__init__(**kwargs)
        self.message = message
        self.callback = callback
        self.user_db = user_db

    def compose(self) -> ComposeResult:
        with Vertical(id="confirmation_vertical"):
            yield Static(f"[#e05252]{self.message}[/#e05252]", id="confirmation_message")
            yield Static("[#4a5a6a]Enter your master password to confirm[/#4a5a6a]", id="confirmation_subtitle")
            yield Input(placeholder="Master password", password=True, id="confirmation_input")
            with Horizontal(id="confirmation_buttons"):
                yield Button("Cancel", id="cancel")
                yield Button("Confirm", id="confirm", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.app.pop_screen()
        elif event.button.id == "confirm":
            password = self.query_one("#confirmation_input", Input).value
            if self.callback:
                success = self.callback(password)
                if success:
                    self.dismiss(True)
