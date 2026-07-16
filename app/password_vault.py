from textual.app import App
from textual.widgets import DataTable
from textual.containers import Vertical, Horizontal
from screens.add_entry_screen import AddEntryScreen
from screens.confirmation_screen import ConfirmationScreen
from screens.search_screen import SearchScreen
from screens.change_master_password_screen import ChangeMasterPasswordScreen
from screens.help_screen import HelpScreen
from security.password_helper import PasswordHelper
from widgets.command_panel import CommandPanel
from widgets.entry_panel import EntryPanel
from widgets.header_row import HeaderRow
from widgets.vault_panel import VaultPanel
import pyperclip
from security.mfa import MFA

# main application to hold all widgets
class PasswordVault(App):
    # tcss file (styling file)
    CSS_PATH = "vault_layout.tcss"
    
    # list of commands (key commands)
    BINDINGS = [
        ("ctrl+a", "add_entry", "Add Entry"),
        ("ctrl+e", "edit_entry", "Edit Entry"),
        ("ctrl+d", "delete_entry", "Delete Entry"),
        ("ctrl+s", "search", "Search"),
        ("ctrl+y", "copy_password", "Copy Password"),
        ("ctrl+u", "copy_username", "Copy Username"),
        ("ctrl+t", "copy_mfa", "Copy MFA"),
        ("ctrl+f", "toggle_favorite", "Toggle Favorite"),
        ("ctrl+c", "change_password", "Change Password"),
        ("ctrl+k", "delete_all", "Delete All"),
        ("?", "push_screen('help')", "Help"),
    ]

    # help screen for extra commandsm
    SCREENS = {"help": HelpScreen}

    # constructor for the appliction, passes the vault database, user database
    # **kwargs takes the extra arguments that Textual might pass (id, classes, name)
    def __init__(self, vault_db, key, user_db, **kwargs):
        # registers the widget with textual
        super().__init__(**kwargs)
        self.vault_db = vault_db
        self.key = key
        self.user_db = user_db
        self.selected_entry = None

    # when the user uses the key command to add an entry
    # when the add entry screen closes refresh the vault table and header row
    def action_add_entry(self):
        self.push_screen(
            AddEntryScreen(self.vault_db, self.key),
            # pass the function for AddEntryScreen to use
            callback=self._screen_closed
        )

    # when the user uses the key command to edit an entry
    # when the edit screen closes, refresh the vault table and header row
    def action_edit_entry(self):
        if self.selected_entry is None:
            self.notify("Select an entry first", severity="warning")
        else:
            self.push_screen(
                AddEntryScreen(self.vault_db, self.key, entry=self.selected_entry),
                # pass the function
                callback=self._screen_closed
            )

    # refresh the vault table and header when the add/edit screen closes
    def _screen_closed(self, result=None):
        # refresh the header row with new values
        self._refresh_header()
        # refresh the vault table with the new vault table
        self.query_one("#vault", VaultPanel).refresh_table()
        
        if self.selected_entry is None:
            self.query_one("#entry_panel", EntryPanel).clear_entry()        
        else:
            self.query_one("#entry_panel", EntryPanel).display_entry(
                self.selected_entry
            )

    # when the user uses the key command to delete an entry
    def action_delete_entry(self):
        if self.selected_entry is None:
            self.notify("Select an entry first", severity="warning")
        else:
            self.push_screen(ConfirmationScreen(
                f"This will permanently delete the entry for site: {self.selected_entry.site_name}",
                self._confirm_del_entry,
                self.user_db
            ),
                callback=self._screen_closed
            )

    def _confirm_del_entry(self, password):
        salt = self.user_db.get_salt()
        hashed_password = PasswordHelper.sha256_hash_util(password, salt)
    
        if self.user_db.verify_password(hashed_password):
            self.vault_db.remove_entry(self.selected_entry.id)
            self.selected_entry = None
            return True
        else:
            self.notify("Invalid Password", severity="warning")
            return False
        

    # when the user uses the key command to search for an entry
    def action_search(self):
        self.push_screen(SearchScreen(self.vault_db))

    # when the user uses the key command to copy a password
    def action_copy_password(self):
        if self.selected_entry is None:
            self.notify("Select an entry first", severity="warning")
        else:
            decrypted_password = PasswordHelper.decrypt(self.selected_entry.encrypted_password, self.key, self.selected_entry.iv)
            pyperclip.copy(decrypted_password.decode())
            self.notify("Password copied to clipboard", severity="information")

    # when the user uses the key command to copy a username
    def action_copy_username(self):
        if self.selected_entry is None:
            self.notify("Select an entry first", severity="warning")
        else:
            pyperclip.copy(self.selected_entry.username)
            self.notify("Username copied to clipboard", severity="information")

    # when the user uses the key command to copy a MFA
    def action_copy_mfa(self):
        if self.selected_entry is None:
            self.notify("Select an entry first", severity="warning")
        else:
            if self.selected_entry.totp_secret:
                decrypted_mfa = PasswordHelper.decrypt(self.selected_entry.totp_secret, self.key, self.selected_entry.totp_iv)
                pyperclip.copy(MFA.get_code(decrypted_mfa.decode()))
                self.notify("MFA code copied to clipboard", severity="information")
            else:
                self.notify(f"MFA not enabled for entry with id:{self.selected_entry.id}", severity="warning")
                return

    # when the user uses the key command to toggle favorite
    def action_toggle_favorite(self):
        if self.selected_entry is None:
            self.notify("Select an entry first", severity="warning")
        else:
            new_favorite = 0 if self.selected_entry.favorite else 1
            self.vault_db.toggle_favorite(new_favorite, self.selected_entry.id)
            self.selected_entry.favorite = new_favorite
            self._screen_closed()

    # when the user uses the key command to change the user's password
    def action_change_password(self):
        self.push_screen(ChangeMasterPasswordScreen(self.vault_db, self.user_db, self.key))

    # when the user uses the key command to delete all entries
    def action_delete_all(self):
        self.push_screen(ConfirmationScreen(
            "This will permanently delete ALL entries.",
            self._confirm_del_all,
            self.user_db
        ),
            callback=self._screen_closed()
        )
       
    def _confirm_del_all(self, password):
        salt = self.user_db.get_salt()
        hashed_password = PasswordHelper.sha256_hash_util(password, salt)

        if self.user_db.verify_password(hashed_password):
            self.vault_db.delete_all_entries()
            self.selected_entry = None
            return True

        else:
            self.notify("Invalid Password", severity="warning")
            return False

    # get the row that the user "selects" clicks on
    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        entry_id = int(event.row_key.value)
        self.selected_entry = self.vault_db.get_entry(entry_id)

        self.query_one("#entry_panel", EntryPanel).display_entry(
            self.selected_entry
        )

    def _refresh_header(self):
        if self.vault_db:
            self.query_one("#total_entries", HeaderRow).set_content(str(self.vault_db.count()))
            self.query_one("#total_mfa", HeaderRow).set_content(str(self.vault_db.count_mfa()))

    def on_screen_resume(self):
        self._refresh_header()
        self.query_one("#vault", VaultPanel).refresh_table()
                
    # display them all to the terminal 
    def compose(self):
        with Horizontal(id="header_horizontal"):
            yield HeaderRow("TOTAL ENTRIES", "0", id="total_entries")
            yield HeaderRow("MFA ACTIVE", "0", id="total_mfa")
            yield HeaderRow("LAST LOGIN", "N/A", id="last_logon")
        with Vertical(id="app_vertical"):
            yield VaultPanel(self.vault_db, id="vault", classes="box")
            with Horizontal():
                yield CommandPanel(id="command_panel", classes="box")
                yield EntryPanel(self.key, id="entry_panel", classes="box")

    def on_mount(self):
        if self.vault_db:
            total_entries = self.vault_db.count()
            total_mfa = self.vault_db.count_mfa()

            self.query_one("#total_entries", HeaderRow).set_content(str(total_entries))
            self.query_one("#total_mfa", HeaderRow).set_content(str(total_mfa))
        
        if self.user_db:
            last_logon = self.user_db.get_last_logon()
            self.query_one("#last_logon", HeaderRow).set_content(str(last_logon))
