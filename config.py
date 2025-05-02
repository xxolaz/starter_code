import os
SECRET_KEY = os.urandom(32)
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = False

SQLALCHEMY_DATABASE_URI = f'postgresql://postgres:postgres@localhost:5432/fyyur'
