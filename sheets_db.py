import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

SHEET_NAME = "triathlon-checks"

def get_sheet():
    creds_dict = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        dict(creds_dict),
        SCOPE
    )
    client = gspread.authorize(creds)

    # NÃO tenta criar
    sh = client.open(SHEET_NAME)

    return sh.sheet1


def load_checks():
    sheet = get_sheet()
    rows = sheet.get_all_values()

    checks = {}

    # Ignora cabeçalho
    for row in rows[1:]:
        if len(row) >= 2:
            key = row[0]
            value = row[1]
            checks[key] = value == "True"

    return checks


def save_check(key: str, value: bool):
    sheet = get_sheet()
    rows = sheet.get_all_values()

    # Se planilha estiver vazia, cria cabeçalho
    if not rows:
        sheet.append_row(["key", "value"])
        rows = sheet.get_all_values()

    for i, row in enumerate(rows):
        if len(row) > 0 and row[0] == key:
            sheet.update_cell(i + 1, 2, str(value))
            return


    sheet.append_row([key, str(value)])
