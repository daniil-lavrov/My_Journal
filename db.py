import sqlite3


class Cursor:

    def __enter__(self):
        self.connect = sqlite3.connect(r'/root/db/myJournal.db')
        self.cursor = self.connect.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connect.commit()
        self.cursor.close()
        self.connect.close()
