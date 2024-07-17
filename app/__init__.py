import logging
from logging.handlers import RotatingFileHandler
import os

from flask import Flask, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_babel import Babel, lazy_gettext as _l

def get_locale():
    return request.accept_languages.best_match(app.config["LANGUAGES"])

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=True) # configuration for SQLite and Development server for production change the render as batch.
login = LoginManager(app)
login.login_view = "login"
login.login_message = _l("Please log in to access this page.")
babel = Babel(app, locale_selector=get_locale)

if not app.debug:
    if not os.path.exists("logs"):
        os.mkdir("logs")
    file_handler = RotatingFileHandler("logs/re_immo.log", maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    
    app.logger.setLevel(logging.INFO)
    app.logger.info("Re:immo startup")
    

from app import routes, models