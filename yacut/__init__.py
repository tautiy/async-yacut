import os

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()


def create_app() -> Flask:
    """Создать и настроить экземпляр Flask-приложения."""
    static_folder = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 'static'
    )
    app = Flask(
        __name__,
        static_folder=static_folder,
        static_url_path='/static'
    )

    app.config.from_object('yacut.config.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    from . import api_views, views, error_handlers

    app.register_blueprint(views.blueprint)
    app.register_blueprint(api_views.blueprint)

    error_handlers.register_error_handlers(app)

    return app

app = create_app()
