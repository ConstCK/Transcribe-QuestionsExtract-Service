import logging

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    GOOGLE_ACCOUNT_JSON: str
    GOOGLE_TABLE_ID: str
    DEEPGRAM_API_KEY: str
    YANDEX_TOKEN: str
    PROJECT_ID: str

    @property
    def yandex_cloud_api_url(self):
        return 'https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={}'

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='allow'
    )


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

settings = Settings()

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)

file_handler = logging.FileHandler('questions.log', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)
