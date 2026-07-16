from textual.app import ComposeResult
from textual.widgets import Static, Button
from textual.widget import Widget
from textual.containers import Vertical, Horizontal
from security.password_helper import PasswordHelper

class EntryPanel(Widget):
    def __init__(self, key, **kwargs):
        super().__init__(**kwargs)
        self.entry = None
        self.key = key
        self.selected_entry = None
        self.show_password = False
        self.show_mfa = False

    def display_entry(self, selected_entry):
        self.selected_entry = selected_entry
        self.show_password = False
        self.show_mfa = False
  
    def compose(self) -> ComposeResult:
        with Vertical(id="vertical_entry_details"):
            yield Static("site - —", id="details_site_name")
            yield Static("url - —", id="details_url")
            yield Static("username - —", id="details_username")

            with Horizontal(id="details_password"):
                yield Static("password - ************", id="details_password")
                yield Button("Show", id="toggle_password")
                yield Button("Copy", id="copy_password")

            with Horizontal(id="details_mfa"):
                yield Static("mfa - ******", id="details_mfa")
                yield Button("Show", id="toggle_mfa")
                yield Button("Copy", id="copy_mfa")

            yield Static("notes - —", id="details_notes")
            

        
    
