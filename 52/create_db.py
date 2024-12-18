import sqlite3

# Подключение к базе данных
conn = sqlite3.connect('universities.db')
cursor = conn.cursor()

# Создание таблицы для университетов
cursor.execute('''
    CREATE TABLE IF NOT EXISTS universities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        rating REAL DEFAULT 0,
        latitude REAL,
        longitude REAL
    )
''')

# Добавим несколько университетов в Варшаве для примера
universities = [
    ("Варшавский университет", "Один из ведущих университетов Польши, известен исследованиями.", 4.8, 52.2394, 21.0151),
    ("Политехника Варшавская", "Технический университет с сильной инженерной программой.", 4.6, 52.2200, 21.0119),
    ("Варшавская школа экономики", "Престижный вуз с фокусом на экономику и бизнес.", 4.5, 52.2120, 21.0074)
]

# Вставка данных
cursor.executemany('INSERT INTO universities (name, description, rating, latitude, longitude) VALUES (?, ?, ?, ?, ?)', universities)

# Сохранение и закрытие соединения
conn.commit()
conn.close()

print("База данных успешно создана и данные добавлены!")
