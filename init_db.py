
import sqlite3
import json

def initialize_database():
    conn = sqlite3.connect('templates.db')
    cursor = conn.cursor()

    # Создание таблицы
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Details (
        detail_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT,
        template BLOB NOT NULL,
        allowed_params TEXT NOT NULL
    )
    ''')

    # Пример добавления новой детали
    detail_data = {
        "p": {"x": 10.0, "y": 20.0},
        "o": {"x": 5.0, "y": 15.0, "z": 25.0},
        "N": {"size": 30.0, "width_original": 100.0, "width_a": 150.0, "width_b": 200.0}
    }
    allowed_params = ["p.x", "p.y", "N.width_a"]

    template_blob = json.dumps(detail_data).encode('utf-8')
    params_blob = ", ".join(allowed_params)

    cursor.execute('''
    INSERT INTO Details(name, description, template, allowed_params)
    VALUES (?, ?, ?, ?)
    ''', ('Пример детали', 'Это демонстрационная деталь.', template_blob, params_blob))

    conn.commit()
    conn.close()

initialize_database()