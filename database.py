import sqlite3
import hashlib

def init_database():
    """Ініціалізація бази даних"""
    conn = sqlite3.connect('sokoban.db')
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS leaderboard (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        level INTEGER,
        steps INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    """Хешування пароля"""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    """Реєстрація нового користувача"""
    try:
        conn = sqlite3.connect('sokoban.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                      (username, hash_password(password)))
        conn.commit()
        conn.close()
        return True, "Реєстрація успішна!"
    except sqlite3.IntegrityError:
        return False, "Користувач вже існує!"
    except Exception as e:
        return False, f"Помилка: {str(e)}"

def login_user(username, password):
    """Авторизація користувача"""
    conn = sqlite3.connect('sokoban.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    
    if result and result[1] == hash_password(password):
        return True, result[0]
    return False, None

def save_score(user_id, level, steps):
    """Збереження результату гри"""
    conn = sqlite3.connect('sokoban.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT steps FROM leaderboard WHERE user_id = ? AND level = ?", (user_id, level))
    existing = cursor.fetchone()
    
    if existing is None or steps < existing[0]:
        if existing:
            cursor.execute("DELETE FROM leaderboard WHERE user_id = ? AND level = ?", (user_id, level))
        cursor.execute("INSERT INTO leaderboard (user_id, level, steps) VALUES (?, ?, ?)", 
                      (user_id, level, steps))
        conn.commit()
    
    conn.close()

def get_leaderboard(level):
    """Отримання таблиці лідерів для рівня"""
    conn = sqlite3.connect('sokoban.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT users.username, leaderboard.steps 
        FROM leaderboard 
        JOIN users ON leaderboard.user_id = users.id 
        WHERE leaderboard.level = ? 
        ORDER BY leaderboard.steps ASC 
        LIMIT 10
    ''', (level,))
    results = cursor.fetchall()
    conn.close()
    return results