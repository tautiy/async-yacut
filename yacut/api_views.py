from http import HTTPStatus

from flask import Blueprint, jsonify, request

from .models import URLMap
from .utils import (
    generate_unique_short_id,
    save_url_map,
    validate_custom_id
)


blueprint = Blueprint('api', __name__, url_prefix='/api')


@blueprint.route('/id/', methods=['POST'])
def create_short_link():
    """Создать короткую ссылку через API."""
    data = request.get_json(silent=True)

    if not data:
        msg = 'Отсутствует тело запроса'
        return jsonify({'message': msg}), HTTPStatus.BAD_REQUEST

    if 'url' not in data or not data['url']:
        msg = '"url" является обязательным полем!'
        return jsonify({'message': msg}), HTTPStatus.BAD_REQUEST

    original = data['url']
    custom_id = data.get('custom_id')

    short_id, error = validate_custom_id(custom_id)
    if error:
        return jsonify({'message': error}), HTTPStatus.BAD_REQUEST

    if short_id is None:
        short_id = generate_unique_short_id()

    url_map, error = save_url_map(original, short_id, custom_id)
    if error:
        return jsonify({'message': error}), HTTPStatus.BAD_REQUEST

    return jsonify({
        'url': original,
        'short_link': request.host_url + url_map.short,
    }), HTTPStatus.CREATED


@blueprint.route('/id/<short_id>/', methods=['GET'])
def get_original_link(short_id):
    """Получить оригинальную ссылку по короткому идентификатору."""
    url_map = URLMap.query.filter_by(short=short_id).first()
    if not url_map:
        msg = 'Указанный id не найден'
        return jsonify({'message': msg}), HTTPStatus.NOT_FOUND

    return jsonify({'url': url_map.original}), HTTPStatus.OK
