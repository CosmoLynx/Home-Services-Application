import os

# Get the base directory where `config.py` is located
basedir = os.path.abspath(os.path.dirname(__file__))

class Config():
    DEBUG = False
    SQLITE_DB_DIR = None
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class LocalDevelopmentConfig(Config):
    # Correctly set the directory path to `db-directory` relative to `config.py`
    SQLITE_DB_DIR = os.path.join(basedir, '../db-directory')
    # Construct the full path for SQLAlchemy to locate `testdb.db`
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(SQLITE_DB_DIR, 'homevibes.db')
    DEBUG = True
