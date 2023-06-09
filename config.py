import logging
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

UPLOAD_FOLDER = 'static/uploads'
app = Flask(__name__)

log_file = 'app.log'
log_handler = logging.FileHandler(log_file)
log_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_handler.setFormatter(formatter)

app.logger.addHandler(log_handler)
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

