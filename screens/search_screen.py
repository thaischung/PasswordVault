from textual.app import ComposeResult
from textual.widgets import Static, DataTable, Input, Button
from textual.containers import Vertical, Horizontal
from textual.screen import Screen

class SearchScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Close"),
        ("ctrl+s", "save", "Save"),
    ]

    def __init__(self, vault_db, **kwargs):
        super().__init__(**kwargs)
        self.vault_db = vault_db

    def compose(self) -> ComposeResult:
        with Vertical(id="search_vertical"):
            yield Static("SEARCH VAULT", id="search_title")
            yield Static("[#4a5a6a]Search by site name[/#4a5a6a]", id="search_subtitle")
            yield Input(placeholder="Type to search...", id="search_input")
            yield DataTable(id="search_results")
            with Horizontal(id="search_button_row"):
                yield Button("Close", id="close")

    def on_mount(self) -> None:
        table = self.query_one("#search_results", DataTable)
        table.cursor_type = "row"
        table.add_column("SITE", width=10)
        table.add_column("MFA", width=25)
        table.add_column("FAVORITE", width=10)

        table.expand = True

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "search_input":
            self.filter_results(event.value)

    def filter_results(self, query: str) -> None:
        table = self.query_one("#search_results", DataTable)
        table.clear()
        if self.vault_db is not None:
            results = self.vault_db.search_for_entry(query)
            for entry in results:
                mfa = "●" if entry.totp_secret else "○"
                favorite = "★" if entry.favorite else "☆"                
                table.add_row(
                    entry.site_name,
                    mfa,
                    favorite,
                    key=str(entry.id)
                )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close":
            self.app.pop_screen()