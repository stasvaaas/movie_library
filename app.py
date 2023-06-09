import os
from waitress import serve
from datetime import datetime
from sqlalchemy import extract
from flask_login import UserMixin
from sqlalchemy import Column, text
from werkzeug.utils import secure_filename
from flask import Markup, send_from_directory, jsonify
from flask import render_template, request, url_for, redirect, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, login_required, logout_user, login_user

image_names = os.listdir('static/uploads')
from config import db, login_manager, app


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
    created_at = Column(db.DateTime, default=datetime.utcnow, server_default=text('(now() at time zone \'utc\')'))

    def __repr__(self):
        return f"<Movie id: {self.movie_id}>"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)


@app.route('/')
def home():
    # flash('Your movie was added successfully!', category='success')
    return render_template('index.html', )


@app.route('/upload/<filename>')
def send_image(filename):
    return send_from_directory('static/uploads', filename)


@app.route('/movies')
def movies_all():
    page = request.args.get('page', 1, type=int)
    movies = Movie.query.order_by(Movie.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('movies.html', movies=movies, image_names=image_names)


@app.route('/movies/director/<director_name>')
def movie_by_director(director_name):
    movies = Movie.query.filter_by(director=director_name).all()
    director = director_name
    return render_template('movies_by_director.html', movies=movies, director=director, image_names=image_names)


@app.route('/filter_movies', methods=['GET', 'POST'])
def filter_movies():
    if request.method == 'POST':
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
        movies = Movie.query.filter(Movie.released.between(start_date, end_date)).all()
        return render_template('filtered_movies.html', movies=movies, image_names=image_names, start_date=start_date,
                               end_date=end_date)

    else:

        return render_template('filtered_movies.html')


@app.route('/movies/<int:id>')
def moviepage(id):
    movie = Movie.query.get(id)
    return render_template('movie.html', movie=movie, image_names=image_names)


@app.route('/movies/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_movie(id):
    movie = Movie.query.get(id)
    if request.method == 'POST':
        file = request.files['poster']
        filename = secure_filename(file.filename)
        if file:
            movie.poster = filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        movie.title = request.form['title']
        movie.genre = request.form['genre']
        movie.director = request.form['director']
        movie.released = request.form['released']
        movie.synopsis = request.form['synopsis']
        movie.rating = request.form['rating']
        db.session.commit()
        flash('Your movie was updated successfully!')
        return redirect(url_for('moviepage', id=id))
    return render_template('edit.html', movie=movie)


@app.route('/movies/<int:id>/delete', methods=['POST'])
@login_required
def delete_movie(id):
    movie_to_delete = Movie.query.get(id)
    if movie_to_delete is not None:
        filename = movie_to_delete.poster
    if movie_to_delete:
        db.session.delete(movie_to_delete)
        db.session.commit()
        poster_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.remove(poster_path)
        flash('Movie deleted successfully!', 'success')
    else:
        flash('Movie not found!', 'error')

    return redirect(url_for('movies_all'))


@app.route('/directors')
def directors():
    directors = Movie.query.distinct(Movie.director).all()
    directors_names = [director.director for director in directors]
    return render_template('directors.html', directors=directors_names)


@app.route('/genres')
def genres():
    all_genres = Movie.query.distinct(Movie.genre).all()

    return render_template('genres.html', genres=all_genres)


@app.route('/<genre>/movies')
def movies_by_genre(genre):
    movies = Movie.query.filter_by(genre=genre).all()
    genre_name = genre
    return render_template('movies_by_genre.html', movies=movies, genre=genre_name, image_names=image_names)


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
                flash('Your movie was added successfully', category='success')
                return redirect(url_for('movies_all', movie=movie, filenames=file_names))
            else:
                flash('Invalid poster file type. Please upload .png or .jpeg')
    else:
        flash(Markup('Please, login to add a new movie.Click <a href="/login">here</a>'))
    return render_template('create.html')


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
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        searched = request.form['search']
        results = []
        if searched:
            results = Movie.query.filter(Movie.title.ilike(f'%{searched}%')).all()
        return render_template('search.html', image_names=image_names, searched=searched, results=results)
    return render_template('search.html')


@app.route('/api/movies', methods=['GET'])
def get_movies():
    year = request.args.get('year')

    if year:
        movies = Movie.query.filter(extract('year', Movie.released) == year).all()
    else:
        movies = Movie.query.all()

    movie_list = []
    for movie in movies:
        movie_data = {
            'id': movie.movie_id,
            'title': movie.title,
            'director': movie.director,
            'genre': movie.genre,
            'released': movie.released
        }
        movie_list.append(movie_data)

    return jsonify(movie_list)


@app.route('/api/movies/<string:title>', methods=['GET'])
def get_movie(title):
    movie = Movie.query.filter_by(title=title).first()

    if movie is None:
        return jsonify({'message': 'Movie not found'}), 404

    movie_data = {
        'id': movie.movie_id,
        'title': movie.title,
        'director': movie.director,
        'genre': movie.genre
    }

    return jsonify(movie_data)


@app.route('/api/genres', methods=['GET'])
def get_genres():
    genres = Movie.query.distinct(Movie.genre).all()

    genre_list = []
    for genres in genres:
        genre_list.append(genres.genre)

    return jsonify(genre_list)


@app.route('/api/genre/<genre>', methods=['GET'])
def genre_genre(genre):
    movies = Movie.query.filter_by(genre=genre).all()

    if not movies:
        return jsonify({'message': 'No movies found for the given genre'}), 404

    movie_list = []
    for movie in movies:
        movie_data = {
            'id': movie.movie_id,
            'title': movie.title,
            'director': movie.director,
            'genre': movie.genre
        }
        movie_list.append(movie_data)

    return jsonify(movie_list)


@app.route('/api/directors', methods=['GET'])
def get_directors():
    directors = Movie.query.distinct(Movie.director).all()
    directors_list = []
    for director in directors:
        directors_list.append(director.director)

    return jsonify(directors_list)


@app.route('/api/directors/<name>', methods=['GET'])
def get_director(name):
    movies = Movie.query.filter_by(director=name).all()
    if not movies:
        return jsonify({'message': 'No movies found for the given director name'}),
    movie_list = []
    for movie in movies:
        movie_data = {
            'id': movie.movie_id,
            'title': movie.title,
            'director': movie.director,
            'genre': movie.genre
        }
        movie_list.append(movie_data)

    return jsonify(movie_list)


if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000)
