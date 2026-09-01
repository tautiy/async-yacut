from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from . import db
from .models import URLMap
from .utils import generate_unique_short_id, is_forbidden_id

blueprint = Blueprint('api', __name__, url_prefix='/api')


def validate_custom_id(custom_id):
    """Проверить корректность custom_id."""
    if custom_id is None or custom_id == '':
        return None, None

    if not isinstance(custom_id, str):
        msg = 'Указано недопустимое имя для короткой ссылки'
        return None, msg

    if len(custom_id) > 16:
        msg = 'Длина custom_id не должна превышать 16 символов'
        return None, msg

    if not custom_id.isalnum():
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


def save_url_map(original, short_id, custom_id):
    """Сохранить ссылку в БД."""
    url_map = URLMap(original=original, short=short_id, is_file=False)

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
        new_url_map = URLMap(original=original, short=new_short_id)
        db.session.add(new_url_map)
        db.session.commit()
        return new_url_map, None


@blueprint.route('/id/', methods=['POST'])
def create_short_link():
    """Создать короткую ссылку через API."""
    data = request.get_json(silent=True)

    if not data:
        msg = 'Отсутствует тело запроса'
        return jsonify({'message': msg}), 400

    if 'url' not in data or not data['url']:
        msg = '"url" является обязательным полем!'
        return jsonify({'message': msg}), 400

    original = data['url']
    custom_id = data.get('custom_id')

    short_id, error = validate_custom_id(custom_id)
    if error:
        return jsonify({'message': error}), 400

    if short_id is None:
        short_id = generate_unique_short_id()

    url_map, error = save_url_map(original, short_id, custom_id)
    if error:
        return jsonify({'message': error}), 400

    return jsonify({
        'url': original,
        'short_link': request.host_url + url_map.short,
    }), 201


@blueprint.route('/id/<short_id>/', methods=['GET'])
def get_original_link(short_id):
    """Получить оригинальную ссылку по короткому идентификатору."""
    url_map = URLMap.query.filter_by(short=short_id).first()
    if not url_map:
        msg = 'Указанный id не найден'
        return jsonify({'message': msg}), 404

    return jsonify({'url': url_map.original}), 200
