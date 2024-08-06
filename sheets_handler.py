import logging
import pygsheets
import os
from datetime import datetime
from linebot.models import TextSendMessage

# 設定日誌記錄
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 認證 Google Sheets API
gc = pygsheets.authorize(service_file='/etc/secrets/key.json')  # /etc/secrets 是 Render 預設的 secret file 路徑

# 開啟指定的 Google Sheet
sht = gc.open_by_key(os.getenv('SPREADSHEET_ID'))

worksheet_mapping = {
    # "U02c370807baaf7ae3f6064d7705a8638": '筮修工作紀錄表',
    "U1afd46e95a1eac5a28fbf9fb889a8d5e": '姵蓁工作紀錄表',
    # "U33bccf9dadb498e7d31b5a4cea9ae297": '政憲工作紀錄表',
    "U864716975bfc7e1c5b93975470810bcc": '致嘉工作紀錄表',
    "U0de51624c010c4a2ec439e10fbd67b1f": '玟君工作紀錄表',
    "U5234be59bcac751016f6d0248fd3cd1b": '蕎安工作紀錄表',
    "U771ef1814950547f3dc72681f305c6e5": '欣妍工作紀錄表',
    "U42d032c70f43518578b14d5d25df9d1f": '又瑋工作紀錄表'
}

content_mapping = {
    "工作日期": 2,
    "工作時數": 3,
    "工作內容": 4,
    "完成度": 5,
    "工作內容細節": 6,
    "心得": 7,
    "任務來源": 8,
    "交接/合作對象": 9,
    "資料來源": 10,
    "資料存放位置": 11
}

def find_last_non_empty_row_index(col_data):
    start_row = 4
    col_data_from_sixth_row = col_data[start_row - 1:]
    last_non_empty_row_index = start_row + len(col_data_from_sixth_row) - 1
    while last_non_empty_row_index >= start_row and not col_data_from_sixth_row[last_non_empty_row_index - start_row].strip():
        last_non_empty_row_index -= 1
    return last_non_empty_row_index

def check_today_entry(user_id):
    sheet_name = worksheet_mapping.get(user_id)
    if not sheet_name:
        return "找不到對應的工作表"

    wks = sht.worksheet_by_title(sheet_name)
    today = datetime.today().strftime("%Y/%m/%d")

    col_data = wks.get_col(content_mapping['工作日期'], include_tailing_empty=False)
    last_non_empty_row_index = find_last_non_empty_row_index(col_data)
    last_filled_date = col_data[last_non_empty_row_index - 1] if last_non_empty_row_index >= 1 else None

    if last_filled_date and is_valid_date(last_filled_date, "%Y/%m/%d"):
        if datetime.strptime(last_filled_date, "%Y/%m/%d").date() == datetime.strptime(today, "%Y/%m/%d").date():
            work_detail_col_data = wks.get_col(content_mapping['工作內容細節'], include_tailing_empty=False)
            if last_non_empty_row_index - 1 < len(work_detail_col_data):
                work_detail = work_detail_col_data[last_non_empty_row_index - 1] if last_non_empty_row_index >= 1 else None
                if work_detail:
                    return True
    return False

def is_valid_date(date_string, date_format="%Y/%m/%d"):
    try:
        datetime.strptime(date_string, date_format)
        return True
    except ValueError:
        return False

def update_google_sheet(line_bot_api, user_id, user_state, message):
    logger.info("User_state1: %s", user_state.get(user_id))
    sheet_name = worksheet_mapping.get(user_id)
    if not sheet_name:
        return "找不到對應的工作表"

    wks = sht.worksheet_by_title(sheet_name)
    today = datetime.today().strftime("%Y/%m/%d")

    if '工作日期' not in user_state.get(user_id, {}):
        col_data = wks.get_col(content_mapping['工作日期'], include_tailing_empty=False)
        last_non_empty_row_index = find_last_non_empty_row_index(col_data)

        wks.update_value((last_non_empty_row_index+1, content_mapping['工作日期']), today)
        user_state.setdefault(user_id, {})['工作日期'] = today
        return f"請問你今天的工作時數"
    elif '工作時數' not in user_state.get(user_id, {}):
        col_data = wks.get_col(content_mapping['工作時數'], include_tailing_empty=False)
        last_non_empty_row_index = find_last_non_empty_row_index(col_data)

        wks.update_value((last_non_empty_row_index+1, content_mapping['工作時數']), message)
        user_state.setdefault(user_id, {})['工作時數'] = message
        return f"請問你今天的工作內容(標題)"
    elif '工作內容' not in user_state.get(user_id, {}):
        col_data = wks.get_col(content_mapping['工作內容'], include_tailing_empty=False)
        last_non_empty_row_index = find_last_non_empty_row_index(col_data)

        wks.update_value((last_non_empty_row_index+1, content_mapping['工作內容']), message)
        user_state.setdefault(user_id, {})['工作內容'] = message
        return f"請問你今天的完成度"
    elif '完成度' not in user_state.get(user_id, {}):
        col_data = wks.get_col(content_mapping['完成度'], include_tailing_empty=False)
        last_non_empty_row_index = find_last_non_empty_row_index(col_data)

        wks.update_value((last_non_empty_row_index+1, content_mapping['完成度']), message)
        user_state.setdefault(user_id, {})['完成度'] = message
        return f"請問你今天的工作內容(細節)"
    elif '工作內容細節' not in user_state.get(user_id, {}):
        col_data = wks.get_col(content_mapping['工作內容細節'], include_tailing_empty=False)
        last_non_empty_row_index = find_last_non_empty_row_index(col_data)

        wks.update_value((last_non_empty_row_index+1, content_mapping['工作內容細節']), message)
        user_state.setdefault(user_id, {})['工作內容細節'] = message
        return f"請問你今天還有任何需要補充的嗎？"
    elif message == "有":
        user_state.setdefault(user_id, {})['additional'] = True
        logger.info("additional: %s", user_state[user_id]['additional'])
        return f"請問你要補充？ 1. 心得 2. 任務來源 3. 交接/合作對象 4. 資料來源 5. 資料存放位置"
    elif user_state.get(user_id, {}).get('additional', False) == True:
        col_data = wks.get_col(content_mapping['工作時數'], include_tailing_empty=False)
        last_non_empty_row_index = find_last_non_empty_row_index(col_data)
        msg = user_state.setdefault(user_id, {}).get('msg', 0)
        logger.info("msg: %s", msg)
        
        if "1" in message or "心得" in message:
            user_state[user_id]['msg'] = 1
            return "請輸入你的心得"
        if '心得' not in user_state.get(user_id, {}) and user_state[user_id]['msg'] == 1:
            wks.update_value((last_non_empty_row_index, content_mapping['心得']), message)
            user_state.setdefault(user_id, {})['心得'] = message
            return "請問你今天還有任何需要補充的嗎？"
        if "2" in message or "任務來源" in message:
            user_state[user_id]['msg'] = 2
            return "請輸入你的任務來源"
        if '任務來源' not in user_state.get(user_id, {}) and user_state[user_id]['msg'] == 2:
            wks.update_value((last_non_empty_row_index, content_mapping['任務來源']), message)
            user_state.setdefault(user_id, {})['任務來源'] = message
            return "請問你今天還有任何需要補充的嗎？"
        if "3" in message or "交接/合作對象" in message:
            user_state[user_id]['msg'] = 3
            return "請輸入你的交接/合作對象"
        if '交接/合作對象' not in user_state.get(user_id, {}) and user_state[user_id]['msg'] == 3:
            wks.update_value((last_non_empty_row_index, content_mapping['交接/合作對象']), message)
            user_state.setdefault(user_id, {})['交接/合作對象'] = message
            return "請問你今天還有任何需要補充的嗎？"

        if "4" in message or "資料來源" in message:
            user_state[user_id]['msg'] = 4
            return "請輸入你的資料來源"
        if '資料來源' not in user_state.get(user_id, {}) and msg == 4:
            wks.update_value((last_non_empty_row_index, content_mapping['資料來源']), message)
            user_state.setdefault(user_id, {})['資料來源'] = message
            return "請問你今天還有任何需要補充的嗎？"
        if "5" in message or "資料存放位置" in message:
            user_state[user_id]['msg'] = 5
            return "請問你今天還有任何需要補充的嗎？"
        if '資料存放位置' not in user_state.get(user_id, {}) and msg == 5:
            wks.update_value((last_non_empty_row_index+1, content_mapping['資料存放位置']), message)
            user_state.setdefault(user_id, {})['資料存放位置'] = message
            return "請問你今天還有任何需要補充的嗎？"
        user_state[user_id]['additional'] = False
        user_state[user_id]['msg'] = 0

    logger.info(user_state)
    # sheet_name = worksheet_mapping.get(user_id)
    # result_str = "\n ".join([f"{key}: {value}" for key, value in user_state[user_id].items()])
    # line_bot_api.push_message('C169b23c827c28e4c5d3c7ddbfb5aa6b9', TextSendMessage(text=f'{sheet_name} \n {result_str}'))  # 群組id
    user_state.pop(user_id, None)
    return "所有紀錄已完成，謝謝！"
