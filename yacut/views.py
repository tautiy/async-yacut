import urllib.parse

import requests
from flask import Blueprint, redirect, render_template, request, Response
from sqlalchemy.exc import IntegrityError

from . import db
from .forms import FileUploadForm, URLForm
from .models import URLMap
from .utils import generate_unique_short_id, is_forbidden_id
from .yandex_disk import get_download_url_sync, upload_files

blueprint = Blueprint('views', __name__)


@blueprint.route('/', methods=['GET', 'POST'])
def index():
    """Главная страница для создания коротких ссылок."""
    form = URLForm()
    short_url = None

    if form.validate_on_submit():
        original = form.original_link.data
        custom_id = form.custom_id.data or None

        if custom_id:
            if is_forbidden_id(custom_id):
                msg = 'Предложенный вариант короткой ссылки уже существует.'
                form.custom_id.errors.append(msg)
                return render_template('index.html', form=form)

            existing = URLMap.query.filter_by(short=custom_id).first()
            if existing:
                msg = 'Предложенный вариант короткой ссылки уже существует.'
                form.custom_id.errors.append(msg)
                return render_template('index.html', form=form)
            short_id = custom_id
        else:
            short_id = generate_unique_short_id()

        url_map = URLMap(original=original, short=short_id, is_file=False)
        try:
            db.session.add(url_map)
            db.session.commit()
            short_url = request.host_url + short_id
        except IntegrityError:
            db.session.rollback()
            if not custom_id:
                short_id = generate_unique_short_id()
                new_url_map = URLMap(original=original, short=short_id)
                db.session.add(new_url_map)
                db.session.commit()
                short_url = request.host_url + short_id

    return render_template('index.html', form=form, short_url=short_url)


@blueprint.route('/files', methods=['GET', 'POST'])
def files():
    """Страница для загрузки файлов."""
    form = FileUploadForm()
    uploaded_files = []

    if form.validate_on_submit():
        files = form.files.data
        if files:
            uploaded_files = upload_files(files)

    return render_template(
        'files.html',
        form=form,
        uploaded_files=uploaded_files
    )


@blueprint.route('/<short_id>')
def redirect_to_original(short_id):
    """Перенаправить на оригинальную ссылку или скачивание файла."""
    url_map = URLMap.query.filter_by(short=short_id).first_or_404()

    if url_map.is_file and url_map.file_path:
        try:
            download_url = get_download_url_sync(url_map.file_path)
            file_response = requests.get(download_url, stream=True)

            response = Response(
                file_response.iter_content(chunk_size=8192),
                status=200,
                content_type=file_response.headers.get('Content-Type')
            )

            filename = url_map.file_name or 'file'
            response.headers['Content-Disposition'] = (
                f'attachment; filename="{filename}"'
            )
            return response

        except Exception as e:
            return render_template('error.html', error=str(e)), 500

    return redirect(url_map.original)
