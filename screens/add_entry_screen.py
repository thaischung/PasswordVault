from textual.app import ComposeResult
from textual.widgets import Static, Input, Button
from textual.containers import Vertical, Horizontal
from textual.screen import Screen
from security.password_helper import PasswordHelper
from models.entry import Entry

# add a new entry to the vault
class AddEntryScreen(Screen):
    # commands to save or cancel the action
    BINDINGS = [
        ("escape", "app.pop_screen", "Cancel"),
        ("ctrl+s", "save", "Save"),
    ]

    def __init__(self, vault_db, key, entry=None, **kwargs):
        super().__init__(**kwargs)
        self.vault_db = vault_db
        self.key = key
        self.selected_entry = entry

    # display two different screens depending if there is a selected entry or not
    # if there is a selected entry then enter edit mode else enter add new entry mode
    def compose(self) -> ComposeResult:
        # title/subtitle 
        title = "EDIT VAULT ENTRY" if self.selected_entry else "ADD VAULT ENTRY"
        subtitle = "Edit an encrypted credential" if self.selected_entry else "Create a new encrypted credential"

        # layout 
        with Vertical(id="add_entry_vertical"):
            yield Static(title, id="add_form_title")
            yield Static(f"[#4a5a6a]{subtitle}[/#4a5a6a]", id="add_form_subtitle")
            yield Input(value=self.selected_entry.site_name if self.selected_entry else "", placeholder="Site", id="site_name")
            yield Input(value=self.selected_entry.url if self.selected_entry else "", placeholder="URL — https://example.com", id="url_input")
            yield Input(value=self.selected_entry.username if self.selected_entry else "", placeholder="Username", id="username")
            with Horizontal(id="password_row"):
                yield Input(placeholder="Password", password=True, id="password_input")
                yield Button("Show", id="toggle_password")
                yield Button("Generate", id="generate_password")
            yield Input(placeholder="MFA secret (optional)", id="mfa_input")
            yield Input(value=self.selected_entry.notes if self.selected_entry else "", placeholder="Notes", id="notes_input")
            yield Static("[#4a5a6a]AES-256-CBC  ◆  PBKDF2-HMAC-SHA256  ◆  Local Only[/#4a5a6a]", id="security_footer")
            with Horizontal(id="button_row"):
                yield Button("Cancel", id="cancel")
                yield Button("Save", id="save", variant="primary")

    # logic for when the user hits save
    def action_save(self):
        # encrypt password
        password = self.query_one("#password_input", Input).value
        if password:
            password_strength = PasswordHelper.password_strength(password)
            encrypted_password, iv = PasswordHelper.encrypt(password, self.key)
            
        elif self.selected_entry:
            encrypted_password = self.selected_entry.encrypted_password
            iv = self.selected_entry.iv
            password_strength = self.selected_entry.password_strength
        else:
            self.notify("Password is required", severity="warning")
            return

        # encrypt the totp if there is one
        totp = self.query_one("#mfa_input", Input).value
        if totp:
            encrypted_totp, totp_iv = PasswordHelper.encrypt(totp, self.key)
        else:
            encrypted_totp = self.selected_entry.totp_secret if self.selected_entry else None
            totp_iv = self.selected_entry.totp_iv if self.selected_entry else None

        site = self.query_one("#site_name", Input).value
        url = self.query_one("#url_input", Input).value
        username = self.query_one("#username", Input).value
        notes = self.query_one("#notes_input", Input).value
        current_time = self.vault_db.get_now()

        if self.selected_entry: 
            entry = Entry(self.selected_entry.id, site, url, username, encrypted_password, iv, self.selected_entry.created_at, current_time, notes, self.selected_entry.favorite, password_strength, encrypted_totp, totp_iv)
            self.vault_db.modify_entry(self.selected_entry.id, entry)
        else:
            entry = Entry(None, site, url, username, encrypted_password, iv, current_time, current_time, notes, 0, password_strength, encrypted_totp, totp_iv)
            self.vault_db.add_entry(entry)
        
        # close this screen and notify the parent screen
        # this triggers the callback passed into push_screen()
        # dismiss() return a result to the parent screen and exectutes the callback
        # unlike pop_screen(), which only removes the screen
        self.dismiss(True)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            # close screen without saving
            self.dismiss(False)
        elif event.button.id == "save":
            self.action_save()
        elif event.button.id == "toggle_password":
            pw = self.query_one("#password_input", Input)
            pw.password = not pw.password
        elif event.button.id == "generate_password":
            pw = PasswordHelper.generate_password()
            self.query_one("#password_input", Input).value = pw
