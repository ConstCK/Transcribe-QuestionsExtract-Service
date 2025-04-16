import re

import requests
from deepgram import DeepgramClient, PrerecordedOptions

from config import logger, settings
from utils.constants import MESSAGES


class DeadLinkException(Exception):
    pass


class TranscriptService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.transcription_options = PrerecordedOptions(
            model="nova-2",
            smart_format=True,
            language='ru',
        )

    async def _transcribe_file_from_url(self, audio_url: str) -> str:
        try:
            deepgram = DeepgramClient(api_key=self.api_key)

            response = await deepgram.listen.asyncrest.v('1').transcribe_url(
                {'url': audio_url},
                self.transcription_options,
                timeout=99999
            )
            result = response.to_dict(
            )['results']['channels'][0]['alternatives'][0]['transcript']
            return result

        except Exception as e:
            logger.error(e)

    @staticmethod
    async def _extract_questions_from_data(data: str) -> list[str]:
        try:
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

    @staticmethod
    def get_direct_url(yandex_url: str) -> str:
        url = settings.yandex_cloud_api_url.format(yandex_url)
        response = requests.get(url)
        if not response:
            raise DeadLinkException(MESSAGES.get('direct_link_error', ''))
        download_url = response.json().get('href')
        return download_url

    async def run_process(
        self,
        audio_url: str | None = None
    ) -> list[str]:
        try:
            data = await self._transcribe_file_from_url(audio_url)
            questions_pool = await self._extract_questions_from_data(data)
            return questions_pool

        except Exception as e:
            logger.error(e)


transcript_service = TranscriptService(
    api_key=settings.DEEPGRAM_API_KEY,
)
