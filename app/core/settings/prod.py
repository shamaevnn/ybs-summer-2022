from app.core.settings.api import AppSettings


class ProdAppSettings(AppSettings):
    class Config(AppSettings.Config):
        env_file = "prod.env"
