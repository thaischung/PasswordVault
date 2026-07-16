from textual.app import ComposeResult
from textual.widgets import Static, Input, Button
from textual.containers import Vertical, Horizontal
from textual.screen import Screen
from security.password_helper import PasswordHelper
from models.entry import Entry
import os

class ChangeMasterPasswordScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Cancel"),
                ("ctrl+s", "save", "Save"),]

    def __init__(self, vault_db, user_db, key, **kwargs):
        super().__init__(**kwargs)
        self.vault_db = vault_db
        self.user_db = user_db
        self.key = key

    def compose(self) -> ComposeResult:
        with Vertical(id="change_password_vertical"):
            yield Static("CHANGE MASTER PASSWORD", id="change_pw_title")
            yield Static("[#4a5a6a]Enter your current password to continue[/#4a5a6a]", id="change_pw_subtitle")
            yield Input(placeholder="Current password", password=True, id="current_password")
            yield Input(placeholder="New password", password=True, id="new_password")
            yield Input(placeholder="Confirm new password", password=True, id="confirm_password")
            yield Static("[#4a5a6a]AES-256-CBC  ◆  PBKDF2-HMAC-SHA256  ◆  Local Only[/#4a5a6a]", id="change_pw_footer")
            with Horizontal(id="change_pw_buttons"):
                yield Button("Cancel", id="cancel")
                yield Button("Change Password", id="save", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.app.pop_screen()
        # if the user tries to update the password
        elif event.button.id == "save":
            # get the old password
            old_pw = self.query_one("#current_password", Input).value
            new_hashed_pw = PasswordHelper.sha256_hash_util(old_pw, self.user_db.get_salt())
            # if the old password matches what is on record 
            if self.user_db.verify_password(new_hashed_pw):
                # get the new password and the re-typed password
                new_pw = self.query_one("#new_password", Input).value
                conf_pw = self.query_one("#confirm_password", Input).value

                # if the new passwords match
                if new_pw == conf_pw:
                    # since we are updating the user password
                    # we need to generate a new salt
                    new_salt = os.urandom(16)

                    # since the salt is new derive a new key to be used to encrypt the entries passwords
                    new_derived_key = PasswordHelper.derive_key(new_pw.encode(), new_salt)

                    # get all entries
                    entries = self.vault_db.get_all_entries()

                    # decrypt all the entry passwords with the old key
                    # re-encrypt each of the entry passwords with the new key
                    for entry in entries:
                        decrypted_password = PasswordHelper.decrypt(entry.encrypted_password, self.key, entry.iv)
                        re_encrypted_password, new_iv = PasswordHelper.encrypt(decrypted_password.decode(), new_derived_key)

                        if entry.totp_secret:
                            decrypted_mfa = PasswordHelper.decrypt(entry.totp_secret, self.key, entry.totp_iv)
                            re_encrypted_mfa, new_mfa_iv = PasswordHelper.encrypt(decrypted_mfa.decode(), new_derived_key)
                        else:
                            re_encrypted_mfa = None
                            new_mfa_iv = None

                        entry = Entry(entry.id, entry.site_name, entry.url, entry.username, re_encrypted_password, new_iv, entry.created_at, self.vault_db.get_now(), entry.notes, entry.favorite, entry.password_strength, re_encrypted_mfa, new_mfa_iv)

                        self.vault_db.modify_entry(entry.id, entry)
                    hashed_new_password = PasswordHelper.sha256_hash_util(new_pw, new_salt)
                    self.user_db.change_password(hashed_new_password)
                    self.user_db.update_salt(new_salt)

                    # get the instance of PasswordVault and update the value of the key for subsequent decryption/encryption
                    self.app.key = new_derived_key

                    self.notify("Password changed successfully")
                    self.app.pop_screen()

                # if they don't match display a warning
                else:
                    self.notify("Passwords do not match", severity="warning")                

