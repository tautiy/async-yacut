import os


class Config:
    """Класс с настройками приложения."""

    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URI', 'sqlite:///db.sqlite3'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DISK_TOKEN = os.environ.get('DISK_TOKEN')

    MAX_CUSTOM_ID_LENGTH = 16
    DEFAULT_SHORT_ID_LENGTH = 6
    SHORT_ID_ALPHABET = (
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        'abcdefghijklmnopqrstuvwxyz'
        '0123456789'
    )
    FORBIDDEN_IDS = {'files'}
    