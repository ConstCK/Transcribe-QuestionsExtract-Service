from config import logger
from services.g_tables import g_tables_service
from services.transcription import DeadLinkException, transcript_service
from utils.constants import HEADERS, MESSAGES


def questions_update_from_file_links(rows_number: int):
    rows = g_tables_service.get_rows_without_questions()[:rows_number]
    for i in rows.values:
        try:
            download_url = transcript_service.get_direct_url(i[0])
            result = transcript_service.run_process(
                audio_url=download_url
            )
            questions = '\n'.join(result)
            g_tables_service.update_cell_by_row_and_column_name(
                int(i[2]), HEADERS.get('questions'), questions
            )
        except DeadLinkException:
            g_tables_service.update_cell_by_row_and_column_name(
                int(i[2]), HEADERS.get('comments'), MESSAGES.get('dead_link_error')
            )
            logger.info(MESSAGES.get('dead_link_error'))
        except Exception as e:
            logger.info(MESSAGES.get('questions_upload_error').format(e))


if __name__ == '__main__':
    pass