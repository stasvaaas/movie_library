import os
import psycopg2
from flask import Blueprint

from .models import Movie

from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, url_for, redirect, flash
from werkzeug.security import generate_password_hash, check_password_hash


# app = Flask(__name__)
# app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:new_password@localhost/movies_db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)

main= Blueprint('main', __name__)


def get_db_connection():
    conn = psycopg2.connect(host="localhost",
                            database="movies_db",
                            user=os.environ['DB_USERNAME'],
                            password=os.environ['DB_PASSWORD'])
    return conn


@main.route("/")
def home():
    return render_template('index.html')


@main.route("/movies")
def movies_all():
    movies = Movie.query.all()
    return render_template('movies.html', movies=movies)

# @app.route('/create', methods=('GET', 'POST'))
# def create():
#     if request.method == 'POST':
#         title = request.form['title']
#         genre = request.form['genre']
#         director = request.form['director']
#         released = request.form['released']
#         synopsis = request.form['synopsis']
#         rating = request.form['rating']
#         poster = request.form['poster']
#         #posted_by =
#
#     return render_template('create.html')

# @main.route('/signup', methods=('POST', 'GET'))
# def signup():
#     error = None
#     if request.method == 'POST':
#         username = request.form['username']
#         email = request.form['email']
#         phash = generate_password_hash(request.form['password'])
#
#         # Validate inputs
#         if not username or not email or not phash:
#             error = 'Please fill out all fields.'
#             flash(error)
#             return render_template('signup.html')
#
#         # Check if username or email already exists
#         if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
#             error = 'Username or email already exists.'
#             flash(error)
#             return render_template('signup.html')
#
#         # Add user to database
#         user = User(username=username, email=email, password=phash)
#         db.session.add(user)
#         db.session.commit()
#
#         return redirect(url_for('login'))
#
#     return render_template('signup.html', error=error)
#
#
# @main.route('/login', methods=('POST', 'GET'))
# def login():
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']
#         remember = True if request.form['remember-me'] else False
#         user = User.query.filter_by(email=email).first()
#         if not user or not check_password_hash(user.password, password):
#             flash('Please, check your login details and try again')
#             return redirect(url_for('login'))
#         return redirect(url_for('movies_all'))
#     return render_template('login.html')
