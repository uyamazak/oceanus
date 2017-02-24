#!/usr/bin/env python
from datetime import datetime
import os
import sys
import io
import gspread
from oauth2client.service_account import ServiceAccountCredentials as SAC

from common.utils import oceanus_logging

logger = oceanus_logging()
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

JSON_KEY_FILE = os.environ['JSON_KEY_FILE']
SPREAD_SHEET_KEY = os.environ['SPREAD_SHEET_KEY']


class GoogleSpreadSheetsTasks:
    worksheets_list = None
    gsheet = None
    gclient = None

    def authorize_gspread(self) -> None:
        scope = ['https://spreadsheets.google.com/feeds']
        credentials = SAC.from_json_keyfile_name(JSON_KEY_FILE, scope)
        self.gclient = gspread.authorize(credentials)
        self.gsheet = self.gclient.open_by_key(SPREAD_SHEET_KEY)

    def is_token_valid(self) -> bool:
        if not self.gsheet:
            return False
        try:
            expired = self.gsheet.client.auth.access_token_expired
        except Exception as e:
            logger.debug("expired {}".format(e))
            return False

        if expired:
            return False

        return True

    def update_worksheets_list(self) -> None:
        self.worksheets_list = [ws.title for ws in self.gsheet.worksheets()]

    def __init__(self) -> None:
        self.keep_processing = True
        self.authorize_gspread()
        self.update_worksheets_list()

    def prepare_worksheet(self, ws_title) -> None:
        if ws_title not in self.worksheets_list:
            self.gsheet.add_worksheet(ws_title, 1, 20)
            logger.info("create worksheet:{}".format(ws_title))
            self.update_worksheets_list()

        logger.debug("worksheets: {}".format(self.worksheets_list))

    def create_ws_title(self, prefix="", suffix="", date_format="%Y-%m"):
        if date_format is None:
            date_format = "%Y-%m"
        d = datetime.now()
        return "{}{}{}".format(prefix,
                               d.strftime(date_format),
                               suffix)

    def get_ws(self, ws_title=None):
        if not ws_title:
            ws_title = self.create_ws_title()
        self.prepare_worksheet(ws_title)
        try:
            self.worksheet = self.gsheet.worksheet(ws_title)
        except Exception:
            self.update_worksheets_list()
            self.prepare_worksheet(ws_title)
            self.worksheet = self.gsheet.worksheet(ws_title)
        return self.worksheet

    def format_ws_row(self, args) -> list:
        row = []
        for a in args:
            # logger.debug("a: {}".format(a))
            if isinstance(a, tuple):
                row.append(":".join(str(i) for i in a))
            elif isinstance(a, str):
                row.append(a)
            elif a is None:
                row.append("")
            else:
                try:
                    row.append(str(a))
                except Exception as e:
                    logger.error("row format error {} "
                                 "type:{}".format(e, a))
        return row

    def send2ws(self, data, **kwargs):
        title_prefix = kwargs.get("title_prefix", "")
        title_suffix = kwargs.get("title_suffix", "")
        date_format = kwargs.get("date_format", None)
        ws_title = self.create_ws_title(prefix=title_prefix,
                                        suffix=title_suffix,
                                        date_format=date_format)
        row = self.format_ws_row(data)
        ws = self.get_ws(ws_title)
        if not self.is_token_valid():
            self.authorize_gspread()
            ws = self.get_ws(ws_title)
            logger.info("access_token_expired reauthorize.")
        try:
            result = ws.append_row(row)
        except gspread.exceptions.RequestError as e:
            logger.error("401 error reopen retry:{}".format(e))
            self.authorize_gspread()
            ws = self.get_ws(ws_title)
            result = ws.append_row(row)
        logger.debug("result:{}".format(result))
        return result
