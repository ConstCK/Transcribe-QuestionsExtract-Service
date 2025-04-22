import re
import requests
import yadisk

from deepgram import DeepgramClient, PrerecordedOptions

from config import logger, settings
from utils.constants import MESSAGES


class DeadLinkException(Exception):
    pass


class BadFileException(Exception):
    pass


class HugeFileException(Exception):
    pass


class TranscriptService:
    def __init__(self, api_key: str, yandex_token: str):
        self.api_key = api_key
        self.headers = {"Authorization": f"OAuth {yandex_token}"}
        self.yandex_url = 'https://cloud-api.yandex.net/v1/disk/public/resources'
        self.transcription_options = PrerecordedOptions(
            model="nova-2",
            smart_format=True,
            language='ru',
        )

    @staticmethod
    def get_direct_url(yandex_url: str) -> str:
        url = settings.yandex_cloud_api_url.format(yandex_url)
        response = requests.get(url)
        if not response:
            raise DeadLinkException(MESSAGES.get('dead_link_message'))
        download_url = response.json().get('href')
        return download_url

    def check_file_size(self, file_url: str) -> bool:
        response = requests.get(
            self.yandex_url,
            params={'public_key': file_url, 'fields': 'size'},
            headers=self.headers
        )
        response.raise_for_status()
        file_info = response.json()
        file_size = file_info.get('size')
        logger.info(MESSAGES.get('file_size').format(file_size // 1024 // 1024))
        if file_size > 1000000000:
            raise HugeFileException(MESSAGES.get('big_file_message'))
        return True

    async def _transcribe_file_from_url(self, file_url: str) -> str | int | None:
        try:
            deepgram = DeepgramClient(api_key=self.api_key)

            response = await deepgram.listen.asyncrest.v('1').transcribe_url(
                {'url': file_url},
                self.transcription_options,
                timeout=99999
            )
            result = response.to_dict(
            )['results']['channels'][0]['alternatives'][0]['transcript']
            return result

        except Exception as e:
            if hasattr(e, 'status') and e.status == '400':
                raise BadFileException(MESSAGES.get('bad_file_message'))
            else:
                logger.error(e)

    @staticmethod
    async def _extract_questions_from_data(data: str) -> list[str] | None:
        try:
            if not data:
                return None
            result = list()
            sentences = re.split(r'[.!]', data)
            modified_sentences = [sentence.strip().replace('\n', ' ')
                                  for sentence in sentences]
            chosen_sentences = [
                sentence for sentence in modified_sentences if '?' in sentence
            ]

            for item in chosen_sentences:
                counter = item.count('?')
                for _ in range(counter):
                    ind = item.find('?')
                    result.append(item[:ind + 1].strip())
                    item = item[ind + 1:]

            return result

        except Exception as e:
            logger.error(e)

    async def run_process(
        self,
        file_url: str | None = None
    ) -> list[str] | None:

        data = await self._transcribe_file_from_url(file_url)
        questions_pool = await self._extract_questions_from_data(data)
        return questions_pool


transcript_service = TranscriptService(
    api_key=settings.DEEPGRAM_API_KEY,
    yandex_token=settings.YANDEX_TOKEN
)
