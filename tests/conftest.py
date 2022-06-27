import os
import uuid
from argparse import Namespace
from pathlib import Path
from types import SimpleNamespace
from typing import Union
from alembic.config import Config


import pytest
from sqlalchemy_utils import create_database, drop_database
from yarl import URL

from app.db.base import settings

PROJECT_PATH = Path(__file__).parent.parent.resolve()


def make_alembic_config(
    cmd_opts: Union[Namespace, SimpleNamespace], base_path: str = PROJECT_PATH
) -> Config:
    """
    Создает объект конфигурации alembic на основе аргументов командной строки,
    подменяет относительные пути на абсолютные.
    """
    # Подменяем путь до файла alembic.ini на абсолютный
    if not os.path.isabs(cmd_opts.config):
        cmd_opts.config = os.path.join(base_path, cmd_opts.config)

    config = Config(file_=cmd_opts.config, ini_section=cmd_opts.name, cmd_opts=cmd_opts)

    # Подменяем путь до папки с alembic на абсолютный
    alembic_location = config.get_main_option("script_location")
    if not os.path.isabs(alembic_location):
        config.set_main_option(
            "script_location", os.path.join(base_path, alembic_location)
        )
    if cmd_opts.pg_url:
        config.set_main_option("sqlalchemy.url", cmd_opts.pg_url)

    return config


@pytest.fixture()
def alembic_config(postgres):
    """
    Создает объект с конфигурацией для alembic, настроенный на временную БД.
    """
    cmd_options = SimpleNamespace(
        config="alembic.ini", name="alembic", pg_url=postgres, raiseerr=False, x=None
    )
    return make_alembic_config(cmd_options)


@pytest.fixture
def postgres():
    """
    Создает временную БД для запуска теста.
    """
    tmp_name = ".".join([uuid.uuid4().hex, "pytest"])
    tmp_url = str(URL(settings.database_url).with_path(tmp_name))
    create_database(tmp_url)

    try:
        yield tmp_url
    finally:
        drop_database(tmp_url)
