import telebot
from telebot import types
import sqlite3
import os.path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "surveys.db")

db_connection = sqlite3.connect(db_path, check_same_thread=False)
cursor = db_connection.cursor()
# bot = telebot.TeleBot('5191014419:AAEVfQQbMc5SzkTQvghRkvMb9tjUnn5IpNc')
bot = telebot.TeleBot('5329387829:AAHdtHf3uf1J5lH8mTALsnm6NQznRUUYnOM')


next_user_id = 1
quest = ''
ans = []
check = 0
adm_ans = 0
user_ans = 0
count_quest = 0
reg = False
all_users = []
admin = 431846556


def push_users(telegramid: str, firstname: str, lastname: str, age: int):
    cursor.execute('INSERT INTO users VALUES (?, ?, ?, ?)', (telegramid, firstname, lastname, age))
    db_connection.commit()


def register_check(user_id):
    cursor.execute("SELECT * FROM users WHERE telegramid = ?", (user_id,))
    return cursor.fetchall()


def get_user_surveys(user_id):
    cursor.execute("SELECT title FROM surveys WHERE author = ?", (user_id,))
    return cursor.fetchall()


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                    f'<b>Приветствую! {message.from_user.first_name}</b>',
                    parse_mode='html')
    bot.send_message(message.chat.id,
                     """Данный бот предназначен для создания опросов и их прохождения пользователями
Доступный функционал: 
1. Регистрация в системе
2. Главное меню бота
Планы:
1. Создание опросов всесильной админской рукой
2. Возможность нелинейного прохождения существующих опросов
3. Сохранение результатов пользователей
4. Сбор общей статистики на основе пользовательских данных""")
    if not register_check(message.from_user.id):
        bot.send_message(message.chat.id, "Прежде чем начать, пожалуйста, укажите ваш возраст:")
        bot.register_next_step_handler(message, get_age)
    menu(message.chat.id)


@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == 'menu':
        bot.edit_message_text("Выберите дальнейшее действие",
                              call.message.chat.id,
                              call.message.id,
                              reply_markup=menu_markup())
    if call.data == 'take survey':
        select_available_survey(call)
    if call.data == 'create survey':
        # Pls do something
        pass
    if call.data == 'my surveys':
        select_user_survey(call)



@bot.message_handler(commands=['menu'])
def get_to_menu(message):
    menu(message.chat.id)


def menu_markup():
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("Пройти опрос", callback_data='take survey'),
               types.InlineKeyboardButton("Создать опрос", callback_data='create survey'))
    markup.row(types.InlineKeyboardButton("Мои опросы", callback_data='my surveys'))
    return markup


def menu(chatid):
    bot.send_message(chatid, "Выберите дальнейшее действие", reply_markup=menu_markup())


def select_available_survey(call):
    available_survey_markup = types.InlineKeyboardMarkup()
    # Запилить выбор только непройденных тестов ТУТ
    cursor.execute("SELECT title FROM surveys")
    available_survey_list = cursor.fetchall()
    if available_survey_list:
        for i in range(len(available_survey_list)):
            available_survey_markup.add(types.InlineKeyboardButton(available_survey_list[i], callback_data=available_survey_list[i]))
        reply_text = "Выберите опрос из предложенных"
    else:
        available_survey_markup.add(types.InlineKeyboardButton("Главное меню", callback_data='menu'))
        reply_text = "Нет доступных опросов"
    bot.edit_message_text(reply_text, call.message.chat.id, call.message.id, reply_markup=available_survey_markup)


def select_user_survey(call):
    user_survey_markup = types.InlineKeyboardMarkup(row_width=2)
    user_survey_list = get_user_surveys(call.message.from_user.id)
    button_row = []
    for title in user_survey_list:
        button_row.append(title)
        if len(button_row) == 2:
            user_survey_markup.row(types.InlineKeyboardButton(button_row[0], callback_data=button_row[0]),
                                   types.InlineKeyboardButton(button_row[1], callback_data=button_row[1]))
            button_row = []
    if button_row:
        user_survey_markup.add(types.InlineKeyboardButton(button_row[0], callback_data=button_row[0]))
    user_survey_markup.row(types.InlineKeyboardButton("<< Назад", callback_data='menu'))
    bot.edit_message_text("Ваши опросы:", call.message.chat.id, call.message.id, reply_markup=user_survey_markup)


@bot.message_handler(content_types=['text'])
# Переброс в меню при рандомном вводе
def random_text_received(message):
    bot.send_message(message.chat.id, "Отправляю Вас в меню")
    menu(message.chat.id)


def get_age(message):
    global next_user_id
    age = 0
    if age == 0:
        try:
            age = int(message.text)
            push_users(telegramid=message.from_user.id,
                      firstname=message.from_user.first_name,
                      lastname=message.from_user.last_name,
                      age=age)
            bot.send_message(message.from_user.id, 'Регистрация прошла успешно')
        except ValueError:
            bot.send_message(message.from_user.id, 'Цифрами, пожалуйста')
            bot.register_next_step_handler(message, get_age)
    menu(message.chat.id)


bot.polling(none_stop=True)

while True:
    pass
