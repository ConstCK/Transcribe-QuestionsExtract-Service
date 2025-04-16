import asyncio

from config import logger
from services.g_tables import g_tables_service
from services.transcription import DeadLinkException, transcript_service
from utils.constants import HEADERS, MESSAGES


async def main_service(rows_number: int):
    rows = g_tables_service.get_rows_without_questions()[:rows_number]
    logger.info(f'DATA!!! --->>>{rows}')
    for i in rows.values:
        try:
            logger.info('Получение прямой ссылки на файл')
            download_url = transcript_service.get_direct_url(i[0])
            logger.info('Начало транскрибации файла')
            result = await transcript_service.run_process(
                audio_url=download_url
            )
            questions = '\n'.join(result)
            g_tables_service.update_cell_by_row_and_column_name(
                int(i[3]), HEADERS.get('questions'), questions
            )
            logger.info('Успешная транскрибация файла')
        except DeadLinkException:
            g_tables_service.update_cell_by_row_and_column_name(
                int(i[3]), HEADERS.get('comments'), MESSAGES.get('dead_link_error')
            )
            logger.info(MESSAGES.get('dead_link_error'))
        except Exception as e:
            logger.info(MESSAGES.get('questions_upload_error').format(e))


async def main():
    print('!!!')
    await main_service(3)


if __name__ == '__main__':
    asyncio.run(main())
