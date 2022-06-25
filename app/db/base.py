import databases
import sqlalchemy

from app.core.config import get_app_settings

settings = get_app_settings()


db_options = settings.db_options

metadata = sqlalchemy.MetaData()
database = databases.Database(settings.database_url, **db_options)
