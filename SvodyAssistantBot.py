import telebot
import config
from datetime import datetime
from dateutil.relativedelta import relativedelta

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

import requestsData

bot = telebot.TeleBot(token=config.TOKEN)

import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning
import json

# Отключаем предупреждения о небезопасном подключении
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Отключаем предупреждения о небезопасном подключении
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

login_url = "https://localhost:5005/Login/DoLogin"  # Ваш URL с формами логина
data_url = "https://localhost:5005/DirectRouter/Index"
rootSession = None

selected_kops = []
get_all_kop = None  # Глобальная переменная для хранения данных КОП

request_get_all_periods = requestsData.request_get_all_periods
request_get_all_components_period = requestsData.request_get_all_components_period
requests_data_get_kop = requestsData.requests_data_get_kop
request_get_period = requestsData.request_get_period


#

def post_request(url: str, request, session):
    """
    :param url:
    :param request:
    :param session:
    :return response.json:
    """
    response = session.post(url, json=request, verify=False)
    if response.status_code == 200:
        try:
            return response.json()
        except ValueError:
            return ('Response is not in JSON format:', response.text)
    else:
        return (f'Failed to retrieve data, status code: {response.status_code}')


def write_response_json(file_name: str, response_svody):
    """
    :param file_name:
    :param response_svody:
    :return:
    """
    with open(f'{file_name}.json', 'w', encoding='utf-8') as f:
        json.dump(response_svody, f, ensure_ascii=False, indent=4)
    print(f"В файл {file_name} ответ от Сводов записан")


@bot.message_handler(commands=['login'])
def login(message):
    global rootSession
    with requests.Session() as session:
        login_data = {
            'Login': 'asd',
            'Password': 'asdasd'
        }  # Данные в виде словаря, которые будут отправляться в POST

        # Добавляем параметр verify=False для отключения проверки сертификата
        session.get(login_url, verify=False)  # Получаем страницу с формой логина
        session.post(login_url, data=login_data,
                     verify=False)  # Отправляем данные в POST, в session записываются наши куки
        rootSession = session
        # Сообщаем пользователю, что сессия создана
        bot.send_message(message.chat.id, 'Сессия создана')

        # # Отправляем информацию о куках
        # cookies_info = "\n".join([f"{k}: {v}" for k, v in session.cookies.items()])
        # bot.send_message(message.chat.id, f'Куки сессии:\n{cookies_info}')


# @bot.message_handler(commands=['start'])
# def start(message):
#     '''
#     Получаем список ОП
#     :param message:
#     :return:
#     '''
#     global rootSession, request_get_all_periods
#     if rootSession is None:
#         bot.send_message(message.chat.id, 'Сначала выполните команду /login')
#         return
#
#     data_get_all_period = post_request(data_url, request_get_all_periods, rootSession)
#
#     if isinstance(data_get_all_period, dict) and 'result' in data_get_all_period and 'data' in data_get_all_period['result']:
#         markup = InlineKeyboardMarkup()
#         for item in data_get_all_period['result']["data"]:
#             button = InlineKeyboardButton(text=item["Code"], callback_data=f"period_{item['Code']}")
#             markup.add(button)
#         bot.send_message(message.chat.id, "Выберите отчетный период:", reply_markup=markup)
#     else:
#         bot.send_message(message.chat.id, f'Ошибка получения данных ОП: {data_get_all_period}')
#
@bot.message_handler(commands=['start'])
def start(message):
    '''
    Получаем список ОП
    :param message:
    :return:
    '''
    global rootSession, request_get_all_periods
    if rootSession is None:
        bot.send_message(message.chat.id, 'Сначала выполните команду /login')
        return

    data_get_all_period = post_request(data_url, request_get_all_periods, rootSession)

    if isinstance(data_get_all_period, dict) and 'result' in data_get_all_period and 'data' in data_get_all_period[
        'result']:
        markup = InlineKeyboardMarkup(row_width=2)  # Устанавливаем row_width=2 для расположения двух кнопок в одной строке
        for item in data_get_all_period['result']["data"]:
            code = item["Code"]
            button = InlineKeyboardButton(text=code, callback_data=f"period_{code}")
            copy_button = InlineKeyboardButton(text='Копировать', callback_data=f"copy_{code}")
            markup.add(button, copy_button)  # Добавляем две кнопки в одну строку
        bot.send_message(message.chat.id, "Выберите отчетный период:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, f'Ошибка получения данных ОП: {data_get_all_period}')

# Функция для изменения даты
def add_time_to_date(date_str, days=0, months=0, year=0):
    '''

    :param date_str:
    :param days:
    :param months:
    :param year:
    :return: new_date_str
    '''
    # Преобразуем строку в объект даты
    date_obj = datetime.fromisoformat(date_str)
    # Добавляем дни, месяцы и года
    new_date_obj = date_obj+relativedelta(days=days, months=months, year=year)
    # Преобразуем обратно в строку в формате ISO 8601
    new_date_str = new_date_obj.isoformat()
    return new_date_str

#Функция для преобразовани даты
def format_date(date_str):
    '''
    :param date_str:
    :return: formatted_date
    '''
    # Преобразуем строку в объект даты
    date_obj = datetime.fromisoformat(date_str)
    # Форматируем дату в "dd-MM-yyy"
    formatted_date = date_obj.strftime("%d-%m-%Y")
    return formatted_date

# Функция копирования отчетного периода
@bot.callback_query_handler(func=lambda call: call.data.startswith("copy_"))
def copy_period_callback(call):
    global rootSession, request_get_all_periods


    period_code = call.data.split("_")[1]

    data_get_all_period = post_request(data_url, request_get_all_periods, rootSession)
    result_id = None

    for item in data_get_all_period['result']["data"]:
        if item['Code'] == period_code:
            result_id = item['id']
            break

    request_get_all_components_period['data'][0]['reportPeriodId'] = result_id
    items_kop = []

    get_all_kop = post_request(data_url, request_get_all_components_period, rootSession)
    for item in get_all_kop['result']['data']:
        item_kop = {"ComponentName": f"{item["Code"]}", "ComponentId": f"{item["id"]}", "NewFormsPackage": False,
              "NewChain": False, "FormPackageName": "", "ChainName": ""}
        items_kop.append(item_kop)


    request_copy_period = {"action": "ReportPeriod", "method": "CreateReportPeriodCopy", "data": [
        {"RPCopyMode": True, "ReportPeriodCode": f"{period_code}", "ReportPeriodID": f"{result_id}",
         "RPComponentList": items_kop, "Disabled": True}], "type": "rpc", "tid": 78}
    post_request(data_url,request_copy_period,rootSession)

    request_get_period[0]["data"][0] = result_id

    response_get_period = post_request(data_url,request_get_period,rootSession)[0]["result"]["data"]

    startDate = response_get_period["BeginDate"]

    data_get_all_period = post_request(data_url, request_get_all_periods, rootSession)

    if isinstance(data_get_all_period, dict) and 'result' in data_get_all_period and 'data' in data_get_all_period[
        'result']:
        markup = InlineKeyboardMarkup(
            row_width=2)  # Устанавливаем row_width=2 для расположения двух кнопок в одной строке
        for item in data_get_all_period['result']["data"]:
            code = item["Code"]
            button = InlineKeyboardButton(text=code, callback_data=f"period_{code}")
            copy_button = InlineKeyboardButton(text='Копировать', callback_data=f"copy_{code}")
            markup.add(button, copy_button)  # Добавляем две кнопки в одну строку
        bot.send_message(call.from_user.id, "Выберите отчетный период:", reply_markup=markup)
    else:
        bot.send_message(call.from_user.id, f'Ошибка получения данных ОП: {data_get_all_period}')

    bot.send_message(call.from_user.id, "message")



@bot.callback_query_handler(func=lambda call: call.data.startswith("period_"))
def handle_period_callback(call):
    '''
    Функция которая выводит список КОП в виде инлайн кнопок при выборе ОП
    :param call:
    :return:
    '''
    global rootSession, result_id, request_get_all_components_period, get_all_kop, request_get_all_periods
    period_code = call.data.split("_")[1]

    data_get_all_period = post_request(data_url, request_get_all_periods, rootSession)
    result_id = None

    for item in data_get_all_period['result']["data"]:
        if item['Code'] == period_code:
            result_id = item['id']
            break

    if result_id:
        bot.send_message(call.message.chat.id, f"The id with Code '{period_code}' is: {result_id}")

        request_get_all_components_period['data'][0]['reportPeriodId'] = result_id

        get_all_kop = post_request(data_url, request_get_all_components_period, rootSession)
        sorted_kops = sorted(get_all_kop['result']['data'], key=lambda x: x['Code'])
        if isinstance(get_all_kop, dict) and 'result' in get_all_kop and 'data' in get_all_kop['result']:
            markup = InlineKeyboardMarkup()
            for item in sorted_kops:
                # icon = '❌' if item['Code'] not in selected_kops else '✅'
                icon = '❌' if item['Disabled'] else '✅'
                button = InlineKeyboardButton(text=f"{icon} {item['Code']}", callback_data=f"kop:{item['Code']}")
                markup.add(button)
            # markup.add(InlineKeyboardButton(text="Открыть", callback_data="action_open"))
            # markup.add(InlineKeyboardButton(text="Закрыть", callback_data="action_close"))
            bot.send_message(call.message.chat.id, "Выберите КОП:", reply_markup=markup)
        else:
            bot.send_message(call.message.chat.id, f'Ошибка получения данных КОП: {get_all_kop}')
    else:
        bot.send_message(call.message.chat.id, f'Не найден элемент с кодом {period_code}')


# @bot.callback_query_handler(func=lambda call: call.data.startswith("kop:"))
# def handle_kop_callback(call):
#     '''
#     Функция для изменения значения Disabled у КОП
#     :param call:
#     :return:
#     '''
#     global selected_kops, get_all_kop
#     kop_code = call.data.split(":")[1]
#     if kop_code in selected_kops:
#         selected_kops.remove(kop_code)
#     else:
#         selected_kops.append(kop_code)
#
#     # Обновляем кнопки с выбранными КОП
#     markup = InlineKeyboardMarkup()
#     for item in get_all_kop['result']['data']:
#         icon = '❌' if item['Code'] not in selected_kops else '✅'
#         button = InlineKeyboardButton(text=f"{icon} {item['Code']}", callback_data=f"kop:{item['Code']}")
#         markup.add(button)
#     markup.add(InlineKeyboardButton(text="Открыть", callback_data="action_open"))
#     markup.add(InlineKeyboardButton(text="Закрыть", callback_data="action_close"))
#
#     bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("kop:"))
def handle_kop_callback(call):
    '''
    Функция для изменения значения Disabled у КОП
    :param call:
    :return:
    '''
    global selected_kops, get_all_kop, requests_data_get_kop
    idKOP = None
    kop_code = call.data.split(":")[1]

    for item in get_all_kop['result']['data']:
        if item['Code'] == kop_code:
            idKOP = item['id']

    # В переменной requests_data_get_kop меняем id компонента отчетного периода для последующего использования в методе сохранения КОП
    requests_data_get_kop[0]["data"][0] = idKOP

    # Отправляем запрос для получения тела запроса КОП для последующего использования методе сохранения КОП
    data_root_item_KOP = post_request(data_url, requests_data_get_kop, rootSession)[0]['result']['data']

    # if data_root_item_KOP['Disabled']:
    #     data_root_item_KOP['Disabled'] = False
    # if not data_root_item_KOP['Disabled']:
    #     data_root_item_KOP['Disabled'] = True

    if data_root_item_KOP['Disabled'] == True:
        data_root_item_KOP['Disabled'] = False
    elif data_root_item_KOP['Disabled'] == False:
        data_root_item_KOP['Disabled'] = True

    data_end_json = {"profiles": ["00000000-0000-0000-0000-000000000000"], "DbKey": "",
                     "dicActualityDate": "2024-06-13T15:50:16",
                     "dbKey": "341F6495A79265847066E37F34235FCE392AD1A583640F679B76FD230D08C54", "isReadOnly": False,
                     "currentNode": {"additionalData": {"StoredObjectId": None}}}

    root_data = []
    root_data.append(data_root_item_KOP)
    root_data.append(data_end_json)

    request_data_disable_kop = {"action": "ReportPeriodComponent", "method": "SaveOneModifiedAsync",
                                "data": root_data, "type": "rpc", "tid": 78}

    data_save_kop = post_request(data_url, request_data_disable_kop, rootSession)

    # all_kop = get_all_kop['result']['data']
    get_all_kop = post_request(data_url, request_get_all_components_period, rootSession)
    sorted_kops = sorted(get_all_kop['result']['data'], key=lambda x: x['Code'])

    # Обновляем кнопки с выбранными КОП
    markup = InlineKeyboardMarkup()
    for item in sorted_kops:
        # icon = '❌' if item['Code'] not in selected_kops else '✅'
        icon = '❌' if item['Disabled'] else '✅'
        button = InlineKeyboardButton(text=f"{icon} {item['Code']}", callback_data=f"kop:{item['Code']}")
        markup.add(button)
    # markup.add(InlineKeyboardButton(text="Открыть", callback_data="action_open"))
    # markup.add(InlineKeyboardButton(text="Закрыть", callback_data="action_close"))

    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("action_"))
def handle_action_callback(call):
    global selected_kops
    action = call.data.split("_")[1]
    if action == "open":
        bot.send_message(call.message.chat.id, f"Вы выбрали открыть: {', '.join(selected_kops)}")
    elif action == "close":
        bot.send_message(call.message.chat.id, f"Вы выбрали закрыть: {', '.join(selected_kops)}")
    selected_kops.clear()  # Очистить список выбранных КОП


bot.polling()
