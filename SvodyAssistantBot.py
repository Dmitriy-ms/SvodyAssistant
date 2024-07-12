import telebot
import config

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

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

# Запрос данных для получения списка отчетных периодов (тело запроса)
request_data = {
    "action": "ReportPeriod",
    "method": "GetPageAsync",
    "data": [
        {
            "context": {
                "profiles": ["00000000-0000-0000-0000-000000000000"],
                "DbKey": "",
                "dicActualityDate": "2024-06-11T12:23:31",
                "dbKey": "341F6495A79265847066E37F34235FCE392AD1A583640F679B76FD230D08C54",
                "isReadOnly": False,
                "currentNode": {
                    "additionalData": {
                        "AdditionalProperties": {}
                    }
                }
            },
            "page": 1,
            "start": 0,
            "limit": 100
        }
    ],
    "type": "rpc",
    "tid": 26
}

# Запрос данных для получения списка КОП (тело запроса)
request_period_data = {
    "action": "ReportPeriod",
    "method": "GetReportPeriodComponentsPage",
    "data": [{
        "context": {
            "profiles": ["00000000-0000-0000-0000-000000000000"],
            "DbKey": "",
            "dicActualityDate": "2024-06-13T15:50:16",
            "dbKey": "341F6495A79265847066E37F34235FCE392AD1A583640F679B76FD230D08C54",
            "isReadOnly": False,
            "currentNode": None
        },
        "reportPeriodId":"",
        "page": 1,
        "start": 0,
        "limit": 25
    }],
    "type": "rpc",
    "tid": 34
}

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
        session.post(login_url, data=login_data, verify=False)  # Отправляем данные в POST, в session записываются наши куки
        rootSession = session
        # Сообщаем пользователю, что сессия создана
        bot.send_message(message.chat.id, 'Сессия создана')

        # # Отправляем информацию о куках
        # cookies_info = "\n".join([f"{k}: {v}" for k, v in session.cookies.items()])
        # bot.send_message(message.chat.id, f'Куки сессии:\n{cookies_info}')

@bot.message_handler(commands=['start'])
def start(message):
    '''
    Получаем список ОП
    :param message:
    :return:
    '''
    global rootSession, request_data
    if rootSession is None:
        bot.send_message(message.chat.id, 'Сначала выполните команду /login')
        return

    data_get_all_period = post_request(data_url, request_data, rootSession)

    if isinstance(data_get_all_period, dict) and 'result' in data_get_all_period and 'data' in data_get_all_period['result']:
        markup = InlineKeyboardMarkup()
        for item in data_get_all_period['result']["data"]:
            button = InlineKeyboardButton(text=item["Code"], callback_data=f"period_{item['Code']}")
            markup.add(button)
        bot.send_message(message.chat.id, "Выберите отчетный период:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, f'Ошибка получения данных ОП: {data_get_all_period}')

@bot.callback_query_handler(func=lambda call: call.data.startswith("period_"))
def handle_period_callback(call):
    global rootSession, result_id, request_period_data, get_all_kop, request_data
    period_code = call.data.split("_")[1]

    data_get_all_period = post_request(data_url, request_data, rootSession)
    result_id = None

    for item in data_get_all_period['result']["data"]:
        if item['Code'] == period_code:
            result_id = item['id']
            break

    if result_id:
        bot.send_message(call.message.chat.id, f"The id with Code '{period_code}' is: {result_id}")

        request_period_data['data'][0]['reportPeriodId'] = result_id

        get_all_kop = post_request(data_url, request_period_data, rootSession)

        if isinstance(get_all_kop, dict) and 'result' in get_all_kop and 'data' in get_all_kop['result']:
            markup = InlineKeyboardMarkup()
            for item in get_all_kop['result']['data']:
                icon = '❌' if item['Code'] not in selected_kops else '✅'
                button = InlineKeyboardButton(text=f"{icon} {item['Code']}", callback_data=f"kop:{item['Code']}")
                markup.add(button)
            markup.add(InlineKeyboardButton(text="Открыть", callback_data="action_open"))
            markup.add(InlineKeyboardButton(text="Закрыть", callback_data="action_close"))
            bot.send_message(call.message.chat.id, "Выберите КОП:", reply_markup=markup)
        else:
            bot.send_message(call.message.chat.id, f'Ошибка получения данных КОП: {get_all_kop}')
    else:
        bot.send_message(call.message.chat.id, f'Не найден элемент с кодом {period_code}')

@bot.callback_query_handler(func=lambda call: call.data.startswith("kop:"))
def handle_kop_callback(call):
    global selected_kops, get_all_kop
    kop_code = call.data.split(":")[1]
    if kop_code in selected_kops:
        selected_kops.remove(kop_code)
    else:
        selected_kops.append(kop_code)

    # Обновляем кнопки с выбранными КОП
    markup = InlineKeyboardMarkup()
    for item in get_all_kop['result']['data']:
        icon = '❌' if item['Code'] not in selected_kops else '✅'
        button = InlineKeyboardButton(text=f"{icon} {item['Code']}", callback_data=f"kop:{item['Code']}")
        markup.add(button)
    markup.add(InlineKeyboardButton(text="Открыть", callback_data="action_open"))
    markup.add(InlineKeyboardButton(text="Закрыть", callback_data="action_close"))

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


