import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or "secret-key-123"
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') # Replace with actual email once domain is up and running.
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') # Replace with actual email once domain is up and running.
    ADMIN = os.environ.get("ADMIN") # Replace with actual email once domain is up and running.
    LANGUAGES = ["en", "de"]