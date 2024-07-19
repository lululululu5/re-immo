import logging
from logging.handlers import RotatingFileHandler
import os

from flask import Flask, request, current_app
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_babel import Babel, lazy_gettext as _l

def get_locale():
    return request.accept_languages.best_match(current_app.config["LANGUAGES"])


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = "auth.login"
login.login_message = _l("Please log in to access this page.")
babel = Babel()

def create_app(config_class=Config):
    app=Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    login.init_app(app)
    babel.init_app(app, locale_selector=get_locale)
    
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, prefix="/auth")
    
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.error import bp as error_bp
    app.register_blueprint(error_bp)
    
    
    if not app.debug and not app.testing:
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
        
    return app
    

from app import models