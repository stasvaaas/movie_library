import os
import psycopg2
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from sqlalchemy import Column, DateTime, text
from flask import Markup, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask import render_template, request, url_for, redirect, flash, Flask
from flask_login import LoginManager, UserMixin, current_user, login_required, logout_user, login_user

UPLOAD_FOLDER = 'static/uploads'
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:new_password@localhost/movies_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(500), nullable=False)
    email = db.Column(db.String(150), unique=True)

    def __repr__(self):
        return f"<your id : {self.user_id}>"


class Movie(db.Model):
    __tablename__ = 'movies'
    title = db.Column(db.String(150), nullable=False)
    genre = db.Column(db.String(150), nullable=False)
    director = db.Column(db.String(100), nullable=True)
    released = db.Column(db.Date, nullable=False)
    synopsis = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    poster = db.Column(db.String(255), nullable=False)
    posted_by = db.Column(db.String(100), db.ForeignKey('users.username'), nullable=False)
    movie_id = db.Column(db.Integer, nullable=False, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow, server_default=text('(now() at time zone \'utc\')'))

    def __repr__(self):
        return f"<Movie id: {self.movie_id}>"


def get_db_connection():
    conn = psycopg2.connect(host="localhost",
                            database="movies_db",
                            user=os.environ['DB_USERNAME'],
                            password=os.environ['DB_PASSWORD'])
    return conn


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def home():
    flash('Your movie was added successfully!', category='success')
    return render_template('index.html', )


@app.route('/upload/<filename>')
def send_image(filename):
    return send_from_directory('static/uploads', filename)


@app.route("/movies")
def movies_all():
    page = request.args.get('page', 1, type=int)
    movies = Movie.query.order_by(Movie.created_at.desc()).paginate(page=page, per_page=10)
    image_names = os.listdir('static/uploads')
    return render_template('movies.html', movies=movies, image_names=image_names)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/create', methods=['GET', 'POST'])
def create():
    if current_user.is_authenticated:
        if request.method == 'POST':
            title = request.form['title']
            genre = request.form['genre']
            director = request.form['director']
            released = request.form['released']
            synopsis = request.form.get('synopsis')
            rating = request.form['rating']
            posted_by = current_user.username
            if 'poster' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['poster']
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            files = request.files.getlist('poster')
            file_names = []
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_names.append(filename)
                    upload_folder = app.config['UPLOAD_FOLDER']
                    if not os.path.exists(upload_folder):
                        os.makedirs(upload_folder)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                    movie = Movie(title=title, genre=genre, director=director, released=released,
                                  synopsis=synopsis, rating=rating, poster=filename, posted_by=posted_by)
                db.session.add(movie)
                db.session.commit()
                return redirect(url_for('movies_all', movie=movie, filenames=file_names))
            else:
                flash('Invalid poster file type. Please upload .png or .jpeg')
    else:
        flash(Markup('Please, login to add a new movie.Click <a href="/login">here</a>'))
        # return redirect(url_for('login'))
    return render_template('create.html')


def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)


# delete method
# @app.route('/delete/<int:record_id>', methods=['POST'])
# def delete_record(movie_id):
#     # Find the record in the database and retrieve the associated image filename
#     record = Movie.query.get(movie_id)
#     if record is not None:
#         filename = record.poster
#
#         # Delete the record from the database
#         db.session.delete(record)
#         db.session.commit()
#
#         # Remove the image file from the upload folder
#         if filename:
#             file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             if os.path.exists(file_path):
#                 os.remove(file_path)
#                 flash('Image deleted successfully', 'success')
#             else:
#                 flash('Image file not found', 'error')
#         else:
#             flash('No image associated with the record', 'warning')
#
#         return redirect(url_for('movies_all'))
#     else:
#         flash('Record not found', 'error')
#         return redirect(url_for('movies_all'))

@app.route('/signup', methods=('POST', 'GET'))
def signup():
    error = None
    if request.method == 'POST':
        # check if password == confirm password
        if request.form['password'] == request.form['password2']:
            username = request.form['username']
            email = request.form['email']
            phash = generate_password_hash(request.form['password'])
            max_id = db.session.query(db.func.max(User.id)).scalar()
            new_id = (max_id or 0) + 1
            # Validate inputs
            if not username or not email or not phash:
                error = 'Please fill out all fields.'
                flash(error)
                return render_template('signup.html')

            # Check if username or email already exists
            if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
                error = 'Username or email already exists.'
                flash(error)
                return render_template('signup.html')

            # Add user to database
            user = User(id=new_id, username=username, email=email, password=phash)
            db.session.add(user)
            db.session.commit()
            flash('You have successfully registered!', category='success')
            return redirect(url_for('login'))

    return render_template('signup.html', error=error)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        remember = True if request.form.get('remember-me') else False
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.', category='error')
            return redirect(url_for('login'))
        login_user(user, remember=remember)
        return redirect(url_for('home'))
        # return redirect(request.form.get('next'))
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run()
