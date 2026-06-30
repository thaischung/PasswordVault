from vault_database import VaultDatabase

class App:
    def __init__(self, fname_db = "vault.db"):
        self.database = VaultDatabase(fname_db)
    