import asyncio

import aiohttp
from flask import current_app, request

from . import db
from .models import URLMap
from .utils import generate_unique_short_id


async def get_upload_url(session, file_path):
    """Получить URL для загрузки файла на Яндекс Диск."""
    token = current_app.config.get('DISK_TOKEN')
    if not token:
        raise ValueError('DISK_TOKEN не установлен')

    url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
    headers = {'Authorization': f'OAuth {token}'}
    params = {'path': file_path, 'overwrite': 'true'}

    async with session.get(url, headers=headers, params=params) as response:
        if response.status != 200:
            error_text = await response.text()
            raise Exception(
                f'Ошибка получения URL: {response.status} - {error_text}'
            )
        data = await response.json()
        return data['href']


async def upload_file_to_disk(session, file, file_path):
    """Загрузить файл на Яндекс Диск."""
    upload_url = await get_upload_url(session, file_path)

    file.seek(0)
    file_data = file.read()

    async with session.put(upload_url, data=file_data) as response:
        if response.status != 201:
            raise Exception(f'Ошибка загрузки: {response.status}')


async def get_download_url(session, file_path):
    """Получить URL для скачивания файла с Яндекс Диска."""
    token = current_app.config.get('DISK_TOKEN')
    if not token:
        raise ValueError('DISK_TOKEN не установлен')

    url = 'https://cloud-api.yandex.net/v1/disk/resources/download'
    headers = {'Authorization': f'OAuth {token}'}
    params = {'path': file_path}

    async with session.get(url, headers=headers, params=params) as response:
        if response.status != 200:
            error_text = await response.text()
            raise Exception(
                f'Ошибка получения ссылки: {response.status} - {error_text}'
            )
        data = await response.json()
        return data['href']


def get_download_url_sync(file_path):
    """Синхронная обертка для получения ссылки на скачивание."""
    async def _get():
        async with aiohttp.ClientSession() as session:
            return await get_download_url(session, file_path)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(_get())


def upload_files(files):
    """Загрузить несколько файлов на Яндекс Диск и создать короткие ссылки."""
    async def upload_all():
        async with aiohttp.ClientSession() as session:
            results = []
            for file in files:
                try:
                    file_name = file.filename
                    file_path = f'app:/{file_name}'

                    await upload_file_to_disk(session, file, file_path)

                    download_url = await get_download_url(session, file_path)

                    short_id = generate_unique_short_id()
                    url_map = URLMap(
                        original=download_url,
                        short=short_id,
                        is_file=True,
                        file_path=file_path,
                        file_name=file_name
                    )

                    db.session.add(url_map)
                    db.session.commit()

                    short_link = request.host_url + short_id

                    results.append({
                        'name': file_name,
                        'short_link': short_link,
                        'download_url': download_url
                    })

                except Exception as e:
                    results.append({
                        'name': file.filename,
                        'error': str(e)
                    })

            return results

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(upload_all())
