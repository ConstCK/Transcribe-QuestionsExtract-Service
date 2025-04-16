import numpy as np
import pandas as pd
from gspread import ValueRange, Worksheet, service_account
from pandas import DataFrame

from config import logger, settings
from utils.constants import HEADERS, MESSAGES


class GoogleTableService:
    def __init__(self, api_key: str, table_id: str):
        self.client = service_account(api_key)
        self.table_id = table_id

    def _get_table_by_id(self):
        return self.client.open_by_key(self.table_id)

    def _get_worksheet(self) -> Worksheet:
        table = self._get_table_by_id()
        worksheet = table.get_worksheet(0)
        return worksheet

    def _get_all_records_from_table(
        self,
        columns: str
    ) -> ValueRange:
        worksheet = self._get_worksheet()
        records = worksheet.get(columns)
        return records

    def get_rows_without_questions(self) -> DataFrame:
        selected_columns = [
            HEADERS.get('file_link'),
            HEADERS.get('comments'),
            HEADERS.get('questions'),
            HEADERS.get('ids'),
        ]
        table_data = (
            self._get_all_records_from_table('G:S')
        )
        target_frame = pd.DataFrame(
            data=table_data[1:], columns=table_data[0]
        )
        target_frame.replace([None, np.nan, "", " "], np.nan, inplace=True)
        result_frame = target_frame.copy()[selected_columns]
        result_frame.dropna(subset=[HEADERS.get('file_link')], inplace=True)
        result_frame = result_frame[result_frame['Вопросы'].isnull()]
        result_frame = result_frame[result_frame[HEADERS.get('comments')] != MESSAGES.get('dead_link_error')]
        logger.info(f'Размер итогового "дата фрейма": {len(result_frame)}')
        return result_frame

    def update_cell_by_row_and_column_name(
        self,
        row_number: int,
        column_name: str,
        new_value: str
    ) -> None:
        table = self._get_table_by_id()
        worksheet = table.get_worksheet(0)
        headers = worksheet.row_values(1)

        col_index = headers.index(column_name) + 1
        worksheet.update_cell(row_number, col_index, new_value)


g_tables_service = GoogleTableService(
    api_key=settings.GOOGLE_ACCOUNT_JSON,
    table_id=settings.GOOGLE_TABLE_ID
)
