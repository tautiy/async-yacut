from datetime import datetime

from yacut import db
from .config import Config


class URLMap(db.Model):
    """Модель для хранения связей оригинальных и коротких ссылок."""

    __tablename__ = 'url_map'

    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(512), nullable=False)
    short = db.Column(
        db.String(Config.MAX_CUSTOM_ID_LENGTH),
        unique=True,
        nullable=False
    )
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_file = db.Column(db.Boolean, default=False)
    file_path = db.Column(db.String(256), nullable=True)
    file_name = db.Column(db.String(256), nullable=True)

    def to_dict(self) -> dict:
        """Преобразовать модель в словарь для API."""
        return {
            'url': self.original,
            'short_link': self.short,
        }
