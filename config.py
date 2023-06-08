import os

from flask import Flask, logging
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

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
image_names = os.listdir('static/uploads')
# logging.basicConfig(level=logging.DEBUG)
#
# file_handler = logging.FileHandler('app.log')
# file_handler.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# file_handler.setFormatter(formatter)
#
# app.logger.addHandler(file_handler)