import asyncio

from config import logger
from services.general import main_service
from services.transcription import transcript_service

from utils.constants import MESSAGES


async def main():
    logger.info(MESSAGES.get('starting_program'))
    await transcript_service.get_service_info()
    await main_service(rows_number=2)
    logger.info(MESSAGES.get('finishing_program'))


if __name__ == '__main__':
    asyncio.run(main())
