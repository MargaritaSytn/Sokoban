import sqlite3
from db_utils import DatabaseManager, db_transaction

# Ініціалізує базу даних — створює таблиці, якщо вони ще не існують
def init_database():
    # Ініціалізація бази даних
    with DatabaseManager() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS leaderboard (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    level INTEGER,
                    steps INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
    # Збереження змін

@db_transaction
def register_user(cursor, username, password):
    # Реєстрація нового користувача. 
    try:
        # ? захищає від SQL-інʼєкцій
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        return True, "Реєстрація успішна!"
    except sqlite3.IntegrityError:
        return False, "Користувач вже існує!"
    except Exception as e:
        return False, f"Помилка: {str(e)}"# обробляє будь-які інші помилки

@db_transaction
def login_user(cursor, username, password):
    # Авторизація користувача
    cursor.execute(
        "SELECT id, password FROM users WHERE username = ?",
        (username,)
    )
    result = cursor.fetchone()
    # пряме порівняння пароля
    if result and result[1] == password:
        return True, result[0]
    return False, None

def save_score(user_id, level, steps):
    # Збереження результату гри
    with DatabaseManager() as cursor:
        cursor.execute(
            "SELECT steps FROM leaderboard WHERE user_id = ? AND level = ?",
            (user_id, level)
        )
        existing = cursor.fetchone()

        # зберігаємо тільки кращий результат
        if existing is None or steps < existing[0]:
            if existing:
                cursor.execute(
                    "DELETE FROM leaderboard WHERE user_id = ? AND level = ?",
                    (user_id, level)
                )
            cursor.execute(
                "INSERT INTO leaderboard (user_id, level, steps) VALUES (?, ?, ?)",
                (user_id, level, steps)
            )

# Отримує ТОП-10 гравців для конкретного рівня
@db_transaction
def get_leaderboard(cursor, level):
    # Отримання таблиці лідерів для рівня
    """Отримання списку лідерів"""
    cursor.execute('''
        SELECT users.username, leaderboard.steps
        FROM leaderboard
        JOIN users ON leaderboard.user_id = users.id
        WHERE leaderboard.level = ?
        ORDER BY leaderboard.steps ASC
        LIMIT 10
    ''', (level,))
    return cursor.fetchall()