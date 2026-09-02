from http import HTTPStatus

from flask import jsonify, render_template


class APIError(Exception):
    """Базовое исключение для API."""

    def __init__(self, message, status_code=HTTPStatus.BAD_REQUEST):
        self.message = message
        self.status_code = status_code


def register_error_handlers(app):
    """Зарегистрировать обработчики ошибок."""

    @app.errorhandler(HTTPStatus.NOT_FOUND)
    def page_not_found(error):
        """Обработчик ошибки 404."""
        return (
            render_template('error.html', error='Страница не найдена'),
            HTTPStatus.NOT_FOUND
        )

    @app.errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR)
    def internal_server_error(error):
        """Обработчик ошибки 500."""
        return (
            render_template('error.html', error='Ошибка сервера'),
            HTTPStatus.INTERNAL_SERVER_ERROR
        )

    @app.errorhandler(HTTPStatus.BAD_REQUEST)
    def bad_request(error):
        """Обработчик ошибки 400."""
        return (
            render_template('error.html', error='Некорректный запрос'),
            HTTPStatus.BAD_REQUEST
        )

    @app.errorhandler(APIError)
    def handle_api_error(error):
        """Обработчик ошибок API."""
        return jsonify({'message': error.message}), error.status_code
