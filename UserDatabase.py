import sqlite3
from datetime import datetime
import hmac

class UserDatabase:
    def __init__(self):
        self.connection = sqlite3.connect("auth.db")

        self.cursor = self.connection.cursor()

        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS user ("
            "id INTEGER PRIMARY KEY, "
            "challenge_text TEXT, "
            "challenge_response_hash BLOB, "
            "username TEXT, "
            "password_hash BLOB, "
            "salt BLOB, "
            "failed_attempts INTEGER DEFAULT 0, "
            "lockout_timestamp TEXT, "
            "last_logon_timestamp TEXT, "
            "last_logout_timestamp TEXT "
            ")"
        )

    # check if a user exists 
    def user_exists(self):
        self.cursor.execute("SELECT EXISTS (SELECT 1 FROM user)")
        return self.cursor.fetchone()[0] == 1
    
    # create the user
    def create_user(self, challenge_text, response, username, password, salt):
        # if a user already exists do not allow creation of another user
        if self.user_exists():
            print("A User Already Exists.")
            return
        
        self.cursor.execute(
            "INSERT INTO user (challenge_text, challenge_response_hash, username, password_hash, salt)"
            "VALUES (?, ?, ?, ?, ?)",
            (challenge_text, response, username, password, salt)
        )

        self.connection.commit()

    # checks that the challenge response is correct
    def verify_response(self, response):
        self.cursor.execute(
            "SELECT challenge_response_hash FROM user"
        )

        result = self.cursor.fetchone()[0]

        return hmac.compare_digest(result, response)

    # checks that the password is correct
    def verify_password(self, password):
        self.cursor.execute(
            "SELECT password_hash FROM user"
        )

        result = self.cursor.fetchone()[0]

        return hmac.compare_digest(result, password)

    # set the last logon time
    def last_logon(self):
        now = datetime.now().isoformat()

        self.cursor.execute(
            "UPDATE user SET last_logon_timestamp = ?", (now, )
        )

        self.connection.commit()

    # set the last logout time
    def last_logout(self):
        now = datetime.now().isoformat()

        self.cursor.execute(
            "UPDATE user SET last_logout_timestamp = ?", (now, )
        )

        self.connection.commit()

    # increment the number of failed sign in attempts
    def increment_failed_attempts(self):
        self.cursor.execute(
            "UPDATE user SET failed_attempts = failed_attempts + 1"
        )

        self.connection.commit()

    # reset the number of failed sign in attempts
    def reset_failed_attempts(self):
        self.cursor.execute(
            "UPDATE user SET failed_attempts = 0"
        )

        self.connection.commit()
    
    # get the number of failed sign in attempts
    def get_failed_attempes(self):
        self.cursor.execute(
            "SELECT failed_attempts FROM user"
        )

        return self.cursor.fetchone()[0]

    # set the timestamp that the user was locked out
    def lockout_timestamp(self):
        now = datetime.now().isoformat()

        self.cursor.execute(
            "UPDATE user SET lockout_timestamp = ?", (now, )
        )

        self.connection.commit()
    
    # check if the user is currently locked out, if so calculate the time left
    def is_lockout(self, lockout_duration_minites=10):
        self.cursor.execute(
            "SELECT lockout_timestamp FROM user"
        )

        result = self.cursor.fetchone()[0]

        if result is None:
            return False
        
        lockout_time = datetime.fromisoformat(result)
        elapsed = (datetime.now() - lockout_time).total_seconds() / 60

        return elapsed < lockout_duration_minites
    
    # clear the lockout timestamp
    def clear_lockout(self):
        self.cursor.execute(
            "UPDATE user SET lockout_timestamp = NULL"
        )

        self.connection.commit()
        
    # get the salt
    def get_salt(self):
        self.cursor.execute(
            "SELECT salt FROM user"
        )

        return self.cursor.fetchone()[0]

