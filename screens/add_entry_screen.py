from textual.app import ComposeResult
from textual.widgets import Static, Input, Button
from textual.containers import Vertical, Horizontal
from textual.screen import Screen
from security.password_helper import PasswordHelper
from models.entry import Entry
from security.mfa import MFA

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
                yield Input(value=self._get_entry_password() if self.selected_entry else "", placeholder="password", password=True, id="password_input")
                yield Button("Show", id="toggle_password")
                yield Button("Generate", id="generate_password")
            with Horizontal(id="mfa_row"):
                yield Input(value=self._get_entry_mfa() if self.selected_entry else "", placeholder="MFA secret (optional)",password=True, id="mfa_input")
                yield Button("Show", id="toggle_mfa")
                yield Static("", id="mfa_button_spacer")
            yield Input(value=self.selected_entry.notes if self.selected_entry else "", placeholder="Notes", id="notes_input")
            yield Static("[#4a5a6a]AES-256-CBC  ◆  PBKDF2-HMAC-SHA256  ◆  Local Only[/#4a5a6a]", id="security_footer")
            with Horizontal(id="button_row"):
                yield Button("Cancel", id="cancel")
                yield Button("Save", id="save", variant="primary")

    # logic for when the user hits save
    def action_save(self):
        totp = self.query_one("#mfa_input", Input).value
        totp = totp.replace(" ", "").upper().rstrip("=")

        if totp and not MFA.validate_secret(totp):
            self.notify("Key value is invalid.", severity="warning")
            return

        # get all the values from the new entry
        site = self.query_one("#site_name", Input).value.strip()
        url = self.query_one("#url_input", Input).value.strip()
        username = self.query_one("#username", Input).value.strip()
        password = self.query_one("#password_input", Input).value
        notes = self.query_one("#notes_input", Input).value.strip()

        # to save a site the entry needs a site name at a minimum
        if not site:
            self.notify("Enter a site name.", severity="warning")
            return
        
        if not username:
            self.notify("Enter a username.", severity="warning")
            return
        
        if not password:
            self.notify("Enter a password.", severity="warning")
            return

        password_strength = PasswordHelper.password_strength(password)
        encrypted_password, iv = PasswordHelper.encrypt(password, self.key)

        # Encrypt a new mfa secret
        if totp:
            encrypted_totp, totp_iv = PasswordHelper.encrypt(totp, self.key)

        # store the old mfa
        else:
            encrypted_totp = None
            totp_iv = None

        # get the current time to update modified and created on new entries
        current_time = self.vault_db.get_now()

        # if it is the edit option
        if self.selected_entry:
            entry = Entry(
                self.selected_entry.id,
                site,
                url,
                username,
                encrypted_password,
                iv,
                self.selected_entry.created_at,
                current_time,
                notes,
                self.selected_entry.favorite,
                password_strength,
                encrypted_totp,
                totp_iv,
            )

            # modify the existing entry
            self.vault_db.modify_entry(self.selected_entry.id, entry)

        # add new entry option
        else:
            entry = Entry(
                None,
                site,
                url,
                username,
                encrypted_password,
                iv,
                current_time,
                current_time,
                notes,
                0,
                password_strength,
                encrypted_totp,
                totp_iv,
            )
            
            # add the new entry to the database
            self.vault_db.add_entry(entry)

        # dismiss the screen, callback and update the vault screen
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
            event.button.label = "Hide" if not pw.password else "Show"

        elif event.button.id == "generate_password":
            pw = PasswordHelper.generate_password()
            self.query_one("#password_input", Input).value = pw

        elif event.button.id == "toggle_mfa":
            mfa_input = self.query_one("#mfa_input", Input)
            mfa_input.password = not mfa_input.password
            event.button.label = "Hide" if not mfa_input.password else "Show"

    def _get_entry_password(self):
        encrypted_password = self.selected_entry.encrypted_password
        iv = self.selected_entry.iv

        pw = PasswordHelper.decrypt(encrypted_password, self.key, iv)

        return pw.decode()
    
    def _get_entry_mfa(self):
        if not self.selected_entry.totp_secret or not self.selected_entry.totp_iv:
            return ""
        
        encrypted_mfa = self.selected_entry.totp_secret
        iv = self.selected_entry.totp_iv

        mfa = PasswordHelper.decrypt(encrypted_mfa, self.key, iv)

        return mfa.decode()
