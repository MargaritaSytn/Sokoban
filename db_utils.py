import sqlite3
from functools import wraps

class DatabaseManager:
    #Технічний клас для керування з'єднанням з БД
    def __init__(self, db_name='sokoban.db'):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
        self.conn.close()

def db_transaction(func):
    #Декоратор для автоматизації транзакцій
    @wraps(func)
    def wrapper(*args, **kwargs):
        with DatabaseManager() as cursor:
            return func(cursor, *args, **kwargs)
    return wrapper