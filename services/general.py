from config import logger
from services.g_tables import g_tables_service
from services.transcription import BadFileException, DeadLinkException, HugeFileException, transcript_service
from utils.constants import HEADERS, MESSAGES


async def main_service(rows_number: int = 1000):
    rows = g_tables_service.get_rows_without_questions()[:rows_number]
    for i in rows.values:
        try:
            logger.info(MESSAGES.get('direct_link_obtain').format(i[3]))
            download_url = transcript_service.get_direct_url(i[0])
            transcript_service.check_file_size(i[0])
            logger.info(MESSAGES.get('start_transcribing_file').format(i[3]))
            result = await transcript_service.run_process(
                file_url=download_url
            )
            questions = '\n'.join(result)
            g_tables_service.update_cell_by_row_and_column_name(
                int(i[3]), HEADERS.get('questions'), questions
            )
            logger.info(MESSAGES.get('successful_file_transcribing').format(i[3]))
        except HugeFileException:
            g_tables_service.update_cell_by_row_and_column_name(
                int(i[3]), HEADERS.get('comments'), MESSAGES.get('big_file_message')
            )
            logger.info(MESSAGES.get('big_file_issue').format(int(i[3])))
        except DeadLinkException:
            g_tables_service.update_cell_by_row_and_column_name(
                int(i[3]), HEADERS.get('comments'), MESSAGES.get('dead_link_message')
            )
            logger.info(MESSAGES.get('dead_link_error').format(int(i[3])))
        except BadFileException:
            g_tables_service.update_cell_by_row_and_column_name(
                int(i[3]), HEADERS.get('comments'), MESSAGES.get('bad_file_message')
            )
            logger.info(MESSAGES.get('bad_file_error').format(int(i[3])))
        except Exception as e:
            logger.info(MESSAGES.get('questions_upload_error').format(e))
