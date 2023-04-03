#from flask_login import UserMixin
from init_db import db


class User(db.Model):
    __tablename__ = 'users'
    # user_id = db.Column(db.Integer, db.Sequence('user_id_seq'))
    username = db.Column(db.String(100), unique=True, primary_key=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)

    def __repr__(self):
        return f"<your id : {self.user_id}>"


class Movie(db.Model):
    __tablename__ = 'movies'
    name = db.Column(db.String(150))
    genre = db.Column(db.String(150))
    director = db.Column(db.String(100))
    released = db.Column(db.Date)
    synopsis = db.Column(db.Text)
    rating = db.Column(db.Float)
    poster = db.Column(db.LargeBinary)
    posted_by = db.Column(db.String(100), db.ForeignKey('users.username'), nullable=False)
    movie_id = db.Column(db.Integer, db.Sequence('movie_id_seq'), primary_key=True)

    def __repr__(self):
        return f"<Movie id: {self.movie_id}>"
