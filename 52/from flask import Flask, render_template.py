from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import sqlite3
import json

app = Flask(__name__)
CORS(app)  # Включает поддержку CORS для всех маршрутов

# Настройка первой базы данных (SQLite) для университетов
UNIVERSITIES_DB = 'universities.db'

def get_db_connection():
    conn = sqlite3.connect(UNIVERSITIES_DB)
    conn.row_factory = sqlite3.Row  # Данные возвращаются как словари
    return conn

# Настройка второй базы данных для отзывов (SQLAlchemy)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reviews.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Определение модели для отзыва (сохранение в базе данных)
class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=False)

# Путь к файлу, куда будут сохраняться отзывы
REVIEWS_FILE = 'reviews.txt'

# Создание базы данных для отзывов (выполняется один раз)
with app.app_context():
    db.create_all()

# Главная страница с картой университетов
@app.route('/')
def index():
    conn = get_db_connection()
    universities = conn.execute('SELECT * FROM universities').fetchall()
    conn.close()
    return render_template('index.html', universities=universities)

# API для получения данных об университетах (GET-запрос)
@app.route('/api/universities', methods=['GET'])
def api_universities():
    conn = get_db_connection()
    universities = conn.execute('SELECT * FROM universities').fetchall()
    conn.close()
    
    # Форматируем данные для JSON
    universities_list = [
        {
            'id': university['id'],
            'name': university['name'],
            'description': university['description'],
            'rating': university['rating'],
            'latitude': university['latitude'],
            'longitude': university['longitude']
        } for university in universities
    ]
    return jsonify(universities_list)

# API для получения всех отзывов (GET-запрос), сначала из базы данных
@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    # Читаем отзывы из файла
    reviews = []
    try:
        with open(REVIEWS_FILE, 'r') as file:
            for line in file:
                reviews.append(json.loads(line.strip()))  # Преобразуем строку обратно в словарь
    except Exception as e:
        return jsonify({"message": f"Ошибка при чтении отзыва из файла: {str(e)}"}), 500

    # Если в файле нет отзывов, получаем их из базы данных
    if not reviews:
        reviews_db = Review.query.all()
        reviews = [
            {'id': review.id, 'username': review.username, 'rating': review.rating, 'comment': review.comment}
            for review in reviews_db
        ]
    
    return jsonify(reviews)

# API для добавления нового отзыва в файл и базу данных (POST-запрос)
@app.route('/api/reviews', methods=['POST'])
def add_review():
    data = request.json
    # Проверяем, что все необходимые данные переданы
    if 'username' not in data or 'rating' not in data or 'comment' not in data:
        return jsonify({'error': 'Invalid data'}), 400

    # Сначала добавляем отзыв в текстовый файл
    review = {
        'username': data['username'],
        'rating': int(data['rating']),
        'comment': data['comment']
    }

    try:
        with open(REVIEWS_FILE, 'a') as file:
            file.write(json.dumps(review) + '\n')  # Записываем отзыв в формате JSON
    except Exception as e:
        return jsonify({"message": f"Ошибка при сохранении отзыва в файл: {str(e)}"}), 500

    # Теперь добавляем отзыв в базу данных
    new_review = Review(
        username=data['username'],
        rating=int(data['rating']),
        comment=data['comment']
    )

    try:
        db.session.add(new_review)
        db.session.commit()
        return jsonify({
            'id': new_review.id,
            'username': new_review.username,
            'rating': new_review.rating,
            'comment': new_review.comment
        }), 201
    except Exception as e:
        return jsonify({"message": f"Ошибка при сохранении отзыва в базе данных: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)








