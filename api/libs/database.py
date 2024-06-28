import sqlite3
from hashlib import sha256


class Crypt:

    def hash_password(password):
        return sha256(password.encode()).hexdigest()


class Account:
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()

    def user_login(self, user_id, user_password) -> dict:
        hashed_password = Crypt.hash_password(password=user_password)
        self.cursor.execute(
            "SELECT * FROM users WHERE user_id=? AND user_password=?", (user_id, hashed_password))
        user = self.cursor.fetchone()
        if user:
            return {"status": '0', "data": user}
        else:
            return {"status": '1', "data": 'user not found!'}

    def delete_user(self, user_id, user_password) -> dict:
        hashed_password = Crypt.hash_password(password=user_password)
        try:
            self.cursor.execute(
                "DELETE FROM users WHERE user_id=? AND user_password=?", (user_id, hashed_password))
            self.connection.commit()
            return {"status": '0'}
        except:
            return {"status": '1'}
