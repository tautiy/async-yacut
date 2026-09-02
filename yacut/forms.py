from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, MultipleFileField
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp

from .config import Config


class URLForm(FlaskForm):
    """Форма для создания короткой ссылки."""

    original_link = StringField(
        'Длинная ссылка',
        validators=[
            DataRequired(message='Обязательное поле'),
            Length(1, 512),
        ]
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[
            Length(0, Config.MAX_CUSTOM_ID_LENGTH),
            Regexp(
                r'^[A-Za-z0-9]*$',
                message='Допустимы только латиница и цифры'
            )
        ]
    )
    submit = SubmitField('Создать')


class FileUploadForm(FlaskForm):
    """Форма для загрузки файлов."""

    files = MultipleFileField(
        'Файлы для загрузки',
        validators=[
            FileRequired(message='Выберите хотя бы один файл'),
        ]
    )
    submit = SubmitField('Загрузить')
