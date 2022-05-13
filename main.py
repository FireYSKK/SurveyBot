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

def register_check(message):
    cursor.execute("SELECT * FROM users WHERE telegramid = ?", (message.from_user.id,))
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
Планы:
1. Создание опросов всесильной админской рукой
2. Главное меню бота
3. Возможность нелинейного прохождения существующих опросов
4. Сохранение результатов пользователей
5. Сбор общей статистики на основе пользовательских данных""")
    if not register_check(message):
        bot.send_message(message.chat.id, "Прежде чем начать, пожалуйста, укажите ваш возраст:")
        bot.register_next_step_handler(message, get_age)
    menu(message.chat.id)


@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == 'menu':
        menu(call.message.chat.id)
    if call.data == 'take survey':
        survey_selector(call.message.chat.id)



@bot.message_handler(commands=['menu'])
def get_to_menu(message):
    menu(message.chat.id)


def menu(chatid):
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("Пройти опрос", callback_data='take survey'),
               types.InlineKeyboardButton("Создать опрос", callback_data='create survey'))
    markup.row(types.InlineKeyboardButton("Мои опросы", callback_data='my surveys'))
    bot.send_message(chatid, "Выберите дальнейшее действие", reply_markup=markup)


def survey_selector(chatid):
    survey_markup = types.InlineKeyboardMarkup()
    # Запилить выбор только непройденных тестов ТУТ
    cursor.execute("SELECT title FROM surveys")
    survey_list = cursor.fetchall()
    if survey_list:
        for i in range(len(survey_list)):
            survey_markup.add(types.InlineKeyboardButton(survey_list[i], callback_data=survey_list[i]))
        bot.send_message(chatid, 'Выберите опрос из предложенных', reply_markup=survey_markup)
    else:
        survey_markup.add(types.InlineKeyboardButton("Главное меню", callback_data='menu'))
        bot.send_message(chatid, 'Нет доступных опросов', reply_markup=survey_markup)


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


###########


# def start(message):
#     global reg;
#     global ans;
#     global uid;
#     global adm_ans;
#     global user_ans;
#     global all_users;
#     global count_quest;
#     if not reg:
#         db_connection.execute("SELECT * FROM bot;")
#         all_users = db_connection.fetchall()
#         for user in all_users:
#             if user[1]=='message.from_user.id':
#                 reg = True
#                 count_quest = user[6]
#                 break
#     ans=[]
#     user_ans=0
#     if message.from_user.id == admin:
#         if message.text.lower() == 'опрос':
#             bot.register_next_step_handler(message, get_quest);
#         else:
#             bot.send_message(admin, 'Напишите \"опрос\"');
#     else:
#         if reg:
#             bot.send_message(message.from_user.id, 'Выберите действие\n1.Получить опрос');
#             if message.text == '1':
#                 bot.register_next_step_handler(message, answer);


def get_quest(message):
    global quest
    quest = message.text
    bot.send_message(admin, 'Введите варианты ответа( чтобы закончить ввод напишите \"стоп\"')
    bot.register_next_step_handler(message, get_ans)


def get_ans(message):
    global ans
    global adm_ans
    adm_ans = message.text
    if adm_ans == 'стоп':
        bot.send_message(admin, 'Вы хотите разослать опрос?')
        bot.register_next_step_handler(message, send_quest)
    else:
        ans.append(adm_ans)
        bot.register_next_step_handler(message, get_ans)


def send_quest(message):
    global check
    k = 1
    if message.text == 'Да' or message.text == 'да':
        bot.send_message(message.chat.id, quest)
        for i in ans:
            bot.send_message(message.chat.id, str(k) + '. ' + str(i))
            k += 1
        check = 1


def answer(message):
    db_connection.execute("SELECT * FROM questions;")
    questions = cursor.fetchall()
    bot.send_message(message.from_user.id, questions[count_quest][1])
    for i in range(10 + 2):
        if questions[count_quest][i] != "NULL":
            bot.send_message(message.from_user.id, questions[count_quest][i])
        else:
            break
    bot.send_message(admin, message.text)


bot.polling(none_stop=True)

while True:
    pass
