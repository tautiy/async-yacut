import secrets

from .constants import SHORT_ID_ALPHABET, DEFAULT_SHORT_ID_LENGTH
from .models import URLMap


def generate_unique_short_id() -> str:
    """Сгенерировать уникальный короткий идентификатор."""
    while True:
        short_id = ''.join(
            secrets.choice(SHORT_ID_ALPHABET)
            for _ in range(DEFAULT_SHORT_ID_LENGTH)
        )
        if not URLMap.query.filter_by(short=short_id).first():
            return short_id


def is_forbidden_id(short_id: str) -> bool:
    """Проверить, является ли идентификатор запрещенным."""
    from .constants import FORBIDDEN_IDS
    return short_id in FORBIDDEN_IDS
