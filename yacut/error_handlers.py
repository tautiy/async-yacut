from flask import jsonify, render_template


class APIError(Exception):
    """Базовое исключение для API."""

    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code


def register_error_handlers(app):
    """Зарегистрировать обработчики ошибок."""

    @app.errorhandler(404)
    def page_not_found(error):
        """Обработчик ошибки 404."""
        return render_template('error.html', error='Страница не найдена'), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        """Обработчик ошибки 500."""
        return render_template('error.html', error='Ошибка сервера'), 500

    @app.errorhandler(400)
    def bad_request(error):
        """Обработчик ошибки 400."""
        return render_template('error.html', error='Некорректный запрос'), 400

    @app.errorhandler(APIError)
    def handle_api_error(error):
        """Обработчик ошибок API."""
        return jsonify({'error': error.message}), error.status_code
