from excel_w_r import read_excel_to_dict,save_leave_requests_to_excel, save_overtime_requests_to_excel
from linebot.models import TextSendMessage
# from app import line_bot_api,leave_requests
import re
from datetime import datetime,timedelta

state=0
def leave_talking(leave_requests,line_bot_api, user_id, message, user_name):
    global state, leave_date, leave_reason,file_leave

    if "我要請假!" in message :
            state = 0
            leave_date=None
            leave_reason=None
            start_date=None
            end_date=None
            state = 1
            print(f'start leaving,state={state}')
            return f"好的{user_name}，請問你要請哪天"
    if state == 1:
        if '請假日期' not in leave_requests.get(user_id, {}) :
            print('date input')
            leave_requests.setdefault(user_name, {})['請假日期'] = message
            pattern = r'^\d{2}-\d{2}$'
            print(message)
            leave_date = leave_requests.get(user_name, {}).get('請假日期', '未提供理由')

            if not re.match(pattern, leave_date):
                print('no')
                if "～" in leave_date:
                    print("到")
                    start_date_str, end_date_str = leave_date.split('～')
                    # 验证并格式化日期
                    start_date = datetime.strptime(start_date_str.strip(), "%m-%d")
                    end_date = datetime.strptime(end_date_str.strip(), "%m-%d")
                    if not re.match(pattern, start_date_str) or not re.match(pattern, end_date_str):
                        state = 1
                        print('wrong1')
                        leave_date=None
                        leave_requests.pop('請假日期',None)
                        return "輸入的日期格式不正確，請使用 MM/DD~MM/DD 格式"
                    else:
                        state = 2
                        print(start_date, end_date)
                        file_leave = read_excel_to_dict(f"D:\\LEDB_0801\\{leave_date}_請假單.xlsx")
                        print(file_leave)
                        if user_name not in file_leave:
                            state = 3
                            # print(leave_requests)
                            return f"好的{user_name}，請問你的請假理由"
                        else:
                            print('already')
                            leave_requests.clear()
                            file_leave.clear()
                            state=0
                            return f"你已經請過{leave_date}的假囉"
                else:
                    print(leave_date)
                    state = 1
                    print('wrong2')
                    leave_date=None
                    leave_requests.pop('請假日期',None)
                    return "輸入的日期格式不正確，請使用 MM/DD 格式"
            else:
                state = 2
                print(leave_date)
                file_leave = read_excel_to_dict(f"D:\\LEDB_0801\\{leave_date}_請假單.xlsx")
                print(file_leave)

                if user_name not in file_leave:
                    state = 3
                    # print(leave_requests)
                    return f"好的{user_name}，請問你的請假理由"
                else:
                    print('already')
                    leave_requests.clear()
                    file_leave.clear()
                    state=0
                    return f"你已經請過{leave_date}的假囉"
    
    if '請假理由' not in leave_requests.get(user_id, {}) and state == 3:
        leave_requests.setdefault(user_name, {})['請假理由'] = message
        leave_date = leave_requests[user_name]['請假日期']  
        print('日期收到')
        leave_reason = leave_requests[user_name]['請假理由']  
        print('日期收到')
        print('理由收到')
        toboss = f"{user_name}，{leave_date}請假，請假原因是{leave_reason}"
        save_leave_requests_to_excel({user_name: {'請假日期': leave_date, '請假理由': leave_reason}}, leave_date)
        line_bot_api.push_message('U1afd46e95a1eac5a28fbf9fb889a8d5e', TextSendMessage(text=toboss)) #blake id

        leave_requests.clear()
        file_leave.clear()

        state=0
        return f"{user_name}，{leave_date}請假，請假原因是{leave_reason}"
    # state=0
    # print(state)
    # return "無法識別的請求"

def work_overtime(user_id,message, user_name):
    if "我要加班!" in message:
        today = datetime.now().strftime('%Y-%m-%d')
        save_overtime_requests_to_excel(user_id, user_name, today)
 
        return f"今天({today}) {user_name}加班"