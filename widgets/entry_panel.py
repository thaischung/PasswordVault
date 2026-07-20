from textual.app import ComposeResult
from textual.widgets import Static, Button
from textual.widget import Widget
from textual.containers import Vertical, Horizontal, VerticalScroll
from security.password_helper import PasswordHelper
from security.mfa import MFA
import pyperclip

class EntryPanel(Widget):
    def __init__(self, key, **kwargs):
        super().__init__(**kwargs)
        self.entry = None
        self.key = key
        self.selected_entry = None
        self.show_password = False
        self.show_mfa = False
    
    # compose creates the panel when the app first starts up, no selected entry
    def compose(self) -> ComposeResult:
        with VerticalScroll(id="entry_details_card"):
            yield Static("SITE", classes="entry_label")
            yield Static("--", id="details_site", classes="entry_value")

            yield Static("URL", classes="entry_label")
            yield Static("--", id="details_url", classes="entry_value")

            yield Static("USERNAME", classes="entry_label")
            yield Static("--", id="details_username", classes="entry_value")

            yield Static("PASSWORD", classes="entry_label")

            with Horizontal(classes="secret_row"):
                yield Static("************", id="details_password", classes="secret_value")
                yield Button("Show", id="toggle_password")
                yield Button("Copy", id="copy_password")

            yield Static("AUTHENTICATOR", classes="entry_label")

            with Horizontal(classes="secret_row"):
                yield Static("******", id="details_mfa", classes="secret_value")
                yield Button("Show", id="toggle_mfa")
                yield Button("Copy", id="copy_mfa")

            yield Static("NOTES", classes="entry_label")
            yield Static("--", id="details_notes", classes="notes_value")
    
    def on_mount(self) -> None:
        self.border_title = "ENTRY DETAILS"
    
    # when an entry is selected update the fields accordingly 
    def display_entry(self, selected_entry):
        self.selected_entry = selected_entry
        self.show_password = False
        self.show_mfa = False

        self.query_one("#details_site", Static).update(selected_entry.site_name or "--")
        self.query_one("#details_url", Static).update(selected_entry.url or "--")
        self.query_one("#details_username", Static).update(selected_entry.username or "--")
        self.query_one("#details_password", Static).update("**********" if selected_entry.encrypted_password else "--")

        self.query_one("#details_mfa", Static).update("******" if selected_entry.totp_secret else "MFA not enabled")

        self.query_one("#details_notes", Static).update(selected_entry.notes or "--")

        self.query_one("#toggle_password", Button).label = "Show"
        self.query_one("#toggle_mfa", Button).label = "Show"

    # if the entry is deleted or unselected then update the panel
    def clear_entry(self) -> None:
        self.selected_entry = None
        self.show_password = False
        self.show_mfa = False

        self.query_one("#details_site", Static).update("--")
        self.query_one("#details_url", Static).update("--")
        self.query_one("#details_username", Static).update("--")
        self.query_one("#details_password", Static).update("**********")

        self.query_one("#details_mfa", Static).update("******")
        self.query_one("#details_notes", Static).update("--")

        self.query_one("#toggle_password", Button).label = "Show"
        self.query_one("#toggle_mfa", Button).label = "Show"
        
    # get the password to display it to the panel
    def _get_decrypted_password(self) -> str:
        encrypted_password = self.selected_entry.encrypted_password
        iv = self.selected_entry.iv

        decrypted_password = PasswordHelper.decrypt(encrypted_password, self.key, iv)

        return decrypted_password.decode()

    def _get_mfa_code(self) -> str:
        encrypted_mfa = self.selected_entry.totp_secret
        mfa_iv = self.selected_entry.totp_iv

        decrypted_mfa = PasswordHelper.decrypt(encrypted_mfa, self.key, mfa_iv)

        code = str(MFA.get_code(decrypted_mfa.decode()))

        return code

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if self.selected_entry is None:
            self.notify("Select an entry first", severity="warning")
            return

        if event.button.id == "toggle_password":
            self.show_password = not self.show_password

            if self.show_password:
                password = self._get_decrypted_password()
                self.query_one("#details_password", Static).update(f"password — {password}")
                event.button.label = "Hide"
            else:
                self.query_one("#details_password", Static).update("password — **********")
                event.button.label = "Show"

        elif event.button.id == "copy_password":
            password = self._get_decrypted_password()
            pyperclip.copy(password)
            self.notify("Password copied to clipboard")
        
        elif event.button.id == "toggle_mfa":
            mfa_code = self._get_mfa_code()

            if mfa_code is None:
                self.notify("MFA is not enabled", severity="warning")
                return
            
            self.show_mfa = not self.show_mfa

            if self.show_mfa:
                mfa_code = self._get_mfa_code()
                self.query_one("#details_mfa", Static).update(f"mfa — {mfa_code}")
                event.button.label = "Hide"
            else:
                self.query_one("#details_mfa", Static).update(f"mfa — ******")
                event.button.label = "Show"

        elif event.button.id == "copy_mfa":
            mfa_code = self._get_mfa_code()
            pyperclip.copy(mfa_code)
            self.notify("MFA code copied to clipboard")
        
    
from textual.app import ComposeResult
from textual.widgets import Static, Button
from textual.widget import Widget
from textual.containers import Vertical, Horizontal
from security.password_helper import PasswordHelper
from security.mfa import MFA
import pyperclip

class EntryPanel(Widget):
    def __init__(self, key, **kwargs):
        super().__init__(**kwargs)
        self.entry = None
        self.key = key
        self.selected_entry = None
        self.show_password = False
        self.show_mfa = False
    
    # compose creates the panel when the app first starts up, no selected entry
    def compose(self) -> ComposeResult:
        with Vertical(id="entry_details_card"):
            yield Static("SITE", classes="entry_label")
            yield Static("--", id="details_site", classes="entry_value")

            yield Static("URL", classes="entry_label")
            yield Static("--", id="details_url", classes="entry_value")

            yield Static("USERNAME", classes="entry_label")
            yield Static("--", id="details_username", classes="entry_value")

            yield Static("PASSWORD", classes="entry_label")

            with Horizontal(classes="secret_row"):
                yield Static("************", id="details_password", classes="secret_value")
                yield Button("Show", id="toggle_password")
                yield Button("Copy", id="copy_password")

            yield Static("AUTHENTICATOR", classes="entry_label")

            with Horizontal(classes="secret_row"):
                yield Static("******", id="details_mfa", classes="secret_value")
                yield Button("Show", id="toggle_mfa")
                yield Button("Copy", id="copy_mfa")

            yield Static("NOTES", classes="entry_label")
            yield Static("--", id="details_notes", classes="notes_value")
    
    def on_mount(self) -> None:
        self.border_title = "ENTRY DETAILS"
        self.set_interval(1, self._refresh_mfa_code)
    
    # when an entry is selected update the fields accordingly 
    def display_entry(self, selected_entry):
        self.selected_entry = selected_entry
        self.show_password = False
        self.show_mfa = False

        self.query_one("#details_site", Static).update(selected_entry.site_name or "--")
        self.query_one("#details_url", Static).update(selected_entry.url or "--")
        self.query_one("#details_username", Static).update(selected_entry.username or "--")
        self.query_one("#details_password", Static).update("**********" if selected_entry.encrypted_password else "--")

        self.query_one("#details_mfa", Static).update("******" if selected_entry.totp_secret else "MFA not enabled")

        self.query_one("#details_notes", Static).update(selected_entry.notes or "--")

        self.query_one("#toggle_password", Button).label = "Show"
        self.query_one("#toggle_mfa", Button).label = "Show"

    # if the entry is deleted or unselected then update the panel
    def clear_entry(self) -> None:
        self.selected_entry = None
        self.show_password = False
        self.show_mfa = False

        self.query_one("#details_site", Static).update("--")
        self.query_one("#details_url", Static).update("--")
        self.query_one("#details_username", Static).update("--")
        self.query_one("#details_password", Static).update("**********")

        self.query_one("#details_mfa", Static).update("******")
        self.query_one("#details_notes", Static).update("--")

        self.query_one("#toggle_password", Button).label = "Show"
        self.query_one("#toggle_mfa", Button).label = "Show"
        
    # get the password to display it to the panel
    def _get_decrypted_password(self) -> str:
        encrypted_password = self.selected_entry.encrypted_password
        iv = self.selected_entry.iv

        decrypted_password = PasswordHelper.decrypt(encrypted_password, self.key, iv)

        return decrypted_password.decode()

    def _get_mfa_code(self) -> str:
        encrypted_mfa = self.selected_entry.totp_secret
        mfa_iv = self.selected_entry.totp_iv

        decrypted_mfa = PasswordHelper.decrypt(encrypted_mfa, self.key, mfa_iv)

        code = str(MFA.get_code(decrypted_mfa.decode()))

        return code

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if self.selected_entry is None:
            self.notify("Select an entry first", severity="warning")
            return

        if event.button.id == "toggle_password":
            self.show_password = not self.show_password

            if self.show_password:
                password = self._get_decrypted_password()
                self.query_one("#details_password", Static).update(f"password — {password}")
                event.button.label = "Hide"
            else:
                self.query_one("#details_password", Static).update("password — **********")
                event.button.label = "Show"

        elif event.button.id == "copy_password":
            password = self._get_decrypted_password()
            pyperclip.copy(password)
            self.notify("Password copied to clipboard")
        
        elif event.button.id == "toggle_mfa":
            if not self.selected_entry.totp_secret:
                self.notify("MFA is not enabled", severity="warning")
                return

            self.show_mfa = not self.show_mfa

            if self.show_mfa:
                mfa_code = self._get_mfa_code()
                self.query_one("#details_mfa", Static).update(
                    f"mfa — {mfa_code[:3]} {mfa_code[3:]}"
                )
                event.button.label = "Hide"
            else:
                self.query_one("#details_mfa", Static).update(
                    "mfa — ******"
                )
                event.button.label = "Show"

        elif event.button.id == "copy_mfa":
            if not self.selected_entry.totp_secret:
                self.notify("MFA is not enabled", severity="warning")
                return

            mfa_code = self._get_mfa_code()
            pyperclip.copy(mfa_code)
            self.notify("MFA code copied to clipboard")
            
    def _refresh_mfa_code(self):
        if not self.show_mfa or self.selected_entry is None or not self.selected_entry.totp_secret:
            return

        mfa_code = self._get_mfa_code()

        self.query_one("#details_mfa", Static).update(f"mfa — {mfa_code[:3]} {mfa_code[3:]}") 
        