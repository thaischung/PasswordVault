from textual.app import ComposeResult
from textual.widgets import DataTable
from textual.widget import Widget
from security.password_helper import PasswordHelper

# display all the entries
class VaultPanel(Widget):
    def __init__(self, vault_db, **kwargs):
        super().__init__(**kwargs)
        self.vault_db = vault_db

    def compose(self) -> ComposeResult:
        yield DataTable(id="vault_table", classes="box")

    def on_mount(self) -> None:
        # set panel title
        self.border_title = "VAULT"

        # finds a widget by type or css selector and allows you to call methods on it
        table = self.query_one(DataTable)

        # set the cursor to select the row rather than the column
        table.cursor_type = "row"

        # set up the columns 
        table.add_column("SITE", width=10)
        table.add_column("MFA", width=25)
        table.add_column("FAVORITE", width=10)
        table.expand = True

        # if the ebale is not empty fill in the rows
        if self.vault_db is not None:
            # get all the entries from the database
            entries = self.vault_db.get_all_entries()
            # for each entry get the elements we want to display
            for entry in entries:
                # tenary operator do this if this condition else do this
                mfa = "●" if entry.totp_secret else "○"
                favorite = "★" if entry.favorite else "☆"
                table.add_row(
                    entry.site_name,
                    mfa,
                    favorite,
                    key=str(entry.id)
                )

    def refresh_table(self):
        table = self.query_one("#vault_table", DataTable)
        table.clear()
        if self.vault_db is not None:
            entries = self.vault_db.get_all_entries()
            for entry in entries:
                mfa = "●" if entry.totp_secret else "○"
                favorite = "★" if entry.favorite else "☆"
                table.add_row(
                    entry.site_name,
                    mfa,
                    favorite,
                    key=str(entry.id)
                )

        # make sure that the selected entry remains selected
        selected = self.app.selected_entry
        if selected:
            try:
                table.move_cursor(row=table.get_row_index(str(selected.id)))
            except:
                pass
    