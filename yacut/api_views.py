from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from . import db
from .models import URLMap
from .utils import generate_unique_short_id, is_forbidden_id

blueprint = Blueprint('api', __name__, url_prefix='/api')


@blueprint.route('/id/', methods=['POST'])
def create_short_link():
    """Создать короткую ссылку через API."""
    data = request.get_json()

    if not data or 'url' not in data:
        msg = 'Отсутствует поле "url"'
        return jsonify({'message': msg}), 400

    original = data['url']
    custom_id = data.get('custom_id')

    if custom_id is not None and custom_id != '':
        if len(custom_id) > 16:
            msg = 'Длина custom_id не должна превышать 16 символов'
            return jsonify({'message': msg}), 400

        if not custom_id.isalnum():
            msg = 'Некорректный короткий идентификатор'
            return jsonify({'message': msg}), 400

        if is_forbidden_id(custom_id):
            msg = 'Предложенный вариант короткой ссылки уже существует.'
            return jsonify({'message': msg}), 400

        existing = URLMap.query.filter_by(short=custom_id).first()
        if existing:
            msg = 'Предложенный вариант короткой ссылки уже существует.'
            return jsonify({'message': msg}), 400

        short_id = custom_id
    else:
        short_id = generate_unique_short_id()

    url_map = URLMap(original=original, short=short_id, is_file=False)

    try:
        db.session.add(url_map)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        if not custom_id:
            short_id = generate_unique_short_id()
            url_map = URLMap(original=original, short=short_id)
            db.session.add(url_map)
            db.session.commit()
        else:
            msg = 'Предложенный вариант короткой ссылки уже существует.'
            return jsonify({'message': msg}), 400

    return jsonify({
        'url': original,
        'short_link': request.host_url + short_id,
    }), 201


@blueprint.route('/id/<short_id>/', methods=['GET'])
def get_original_link(short_id):
    """Получить оригинальную ссылку по короткому идентификатору."""
    url_map = URLMap.query.filter_by(short=short_id).first()
    if not url_map:
        msg = 'Указанный id не найден'
        return jsonify({'message': msg}), 404

    return jsonify({'url': url_map.original}), 200
