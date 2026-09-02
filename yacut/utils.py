import secrets

from sqlalchemy.exc import IntegrityError

from .config import Config
from .models import URLMap


def generate_unique_short_id() -> str:
    """Сгенерировать уникальный короткий идентификатор."""
    max_attempts = 100
    for _ in range(max_attempts):
        short_id = ''.join(
            secrets.choice(Config.SHORT_ID_ALPHABET)
            for _ in range(Config.DEFAULT_SHORT_ID_LENGTH)
        )
        if not URLMap.query.filter_by(short=short_id).first():
            return short_id
    return generate_unique_short_id_with_length(
        Config.DEFAULT_SHORT_ID_LENGTH + 1
    )


def generate_unique_short_id_with_length(length: int) -> str:
    """Сгенерировать уникальный короткий идентификатор заданной длины."""
    max_attempts = 100
    for _ in range(max_attempts):
        short_id = ''.join(
            secrets.choice(Config.SHORT_ID_ALPHABET)
            for _ in range(length)
        )
        if not URLMap.query.filter_by(short=short_id).first():
            return short_id
    return generate_unique_short_id_with_length(length + 1)


def is_forbidden_id(short_id: str) -> bool:
    """Проверить, является ли идентификатор запрещенным."""
    return short_id in Config.FORBIDDEN_IDS


def validate_custom_id(custom_id: str):
    """Проверить корректность custom_id."""
    if custom_id is None or custom_id == '':
        return None, None

    if not isinstance(custom_id, str):
        msg = 'Указано недопустимое имя для короткой ссылки'
        return None, msg

    if len(custom_id) > Config.MAX_CUSTOM_ID_LENGTH:
        msg = 'Указано недопустимое имя для короткой ссылки'
        return None, msg

    if not custom_id.isascii() or not custom_id.isalnum():
        msg = 'Указано недопустимое имя для короткой ссылки'
        return None, msg

    if is_forbidden_id(custom_id):
        msg = 'Предложенный вариант короткой ссылки уже существует.'
        return None, msg

    existing = URLMap.query.filter_by(short=custom_id).first()
    if existing:
        msg = 'Предложенный вариант короткой ссылки уже существует.'
        return None, msg

    return custom_id, None


def save_url_map(original: str, short_id: str, custom_id: str = None):
    """Сохранить ссылку в БД."""
    from . import db

    url_map = URLMap(
        original=original,
        short=short_id,
        is_file=False
    )

    try:
        db.session.add(url_map)
        db.session.commit()
        return url_map, None
    except IntegrityError:
        db.session.rollback()
        if custom_id:
            msg = 'Предложенный вариант короткой ссылки уже существует.'
            return None, msg

        new_short_id = generate_unique_short_id()
        new_url_map = URLMap(
            original=original,
            short=new_short_id,
            is_file=False
        )
        db.session.add(new_url_map)
        db.session.commit()
        return new_url_map, None
