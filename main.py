import telebot
from telebot import types
import sqlite3
import os.path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "surveys.db")

TOKEN = '5329387829:AAHdtHf3uf1J5lH8mTALsnm6NQznRUUYnOM'
# '5191014419:AAEVfQQbMc5SzkTQvghRkvMb9tjUnn5IpNc'

db_connection = sqlite3.connect(db_path, check_same_thread=False)
cursor = db_connection.cursor()
bot = telebot.TeleBot(TOKEN)


# Взаимодействие с базой данных


def push_users(telegramid: str, firstname: str, lastname: str, age: int):
    cursor.execute('INSERT INTO users VALUES (?, ?, ?, ?)', (telegramid, firstname, lastname, age))
    db_connection.commit()


def register_check(user_id):
    cursor.execute("SELECT * FROM users WHERE telegramid = ?", (user_id,))
    return cursor.fetchall()


def get_user_surveys(user_id):
    cursor.execute("SELECT title FROM surveys WHERE author = ?", (user_id,))
    return cursor.fetchall()


cursor.execute("""SELECT surveyid FROM surveys""")
next_survey_id = len(cursor.fetchall()) + 1
def push_survey(title: str, author: str):
    global next_survey_id
    cursor.execute('INSERT INTO surveys VALUES (?, ?, ?)', (next_survey_id, title, author))
    next_survey_id += 1
    db_connection.commit()
    return next_survey_id - 1


cursor.execute("""SELECT questionid FROM questions""")
next_question_id = len(cursor.fetchall()) + 1
def push_question(task: str, answers: list, surveyid: int):
    global next_question_id
    while len(answers) < 4:
        answers.append(None)
    cursor.execute('INSERT INTO questions VALUES (?, ?, ?, ?, ?, ?, ?)',
                   (next_question_id, task, answers[0], answers[1], answers[2], answers[3], surveyid))
    next_question_id += 1
    db_connection.commit()
    return next_question_id - 1


def get_survey_title(surveyid):
    cursor.execute("""SELECT title FROM surveys WHERE surveyid = ?""", (surveyid,))
    return cursor.fetchall()


def get_survey_questions(surveyid):
    cursor.execute("""SELECT task FROM questions WHERE surveyid = ?""", (surveyid,))
    return cursor.fetchall()


def answer_exist(questionid):
    cursor.execute("""SELECT answer1 FROM questions WHERE questionid = ?""", (questionid,))
    if cursor.fetchall():
        return True
    else:
        return False


def edit_question_task(questionid: int, new_task: str):
    cursor.execute("""UPDATE questions SET task = ? WHERE questionid = ?""", (questionid, new_task))
    db_connection.commit()


### Handlers for everything


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
        return
    menu(message.chat.id)


@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == 'menu':
        bot.edit_message_text("Выберите дальнейшее действие",
                              call.message.chat.id,
                              call.message.id,
                              reply_markup=menu_markup())
    if call.data == 'take_survey':
        select_available_survey(call)
    if call.data == 'create_survey':
        create_survey(call)
    if call.data == 'my_surveys':
        select_user_survey(call)
    call_data = call.data.split()
    if len(call_data) == 2:
        if call_data[0] == 'add_question':
            print('QCreate')
            create_question(call, call_data[1])
        if call_data[0] == 'survey_editor':
            print('QBack')
            survey_editor(call, call_data[1])


@bot.message_handler(commands=['menu'])
def get_to_menu(message):
    menu(message.chat.id)


@bot.message_handler(content_types=['text'])
# Переброс в меню при рандомном вводе
def random_text_received(message):
    bot.send_message(message.chat.id, "Отправляю Вас в меню")
    menu(message.chat.id)


# Menu functions


def menu_markup():
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("Пройти опрос", callback_data='take_survey'),
               types.InlineKeyboardButton("Создать опрос", callback_data='create_survey'))
    markup.row(types.InlineKeyboardButton("Мои опросы", callback_data='my_surveys'))
    return markup


def menu(chatid):
    bot.send_message(chatid, "Выберите дальнейшее действие", reply_markup=menu_markup())


def create_survey(call):
    new_survey_id = push_survey(title='Новый опрос', author=f'{call.message.from_user.id}')
    print(new_survey_id, '||')
    survey_editor(call, new_survey_id)


def survey_editor(call, surveyid):
    survey_editor_markup = types.InlineKeyboardMarkup()
    survey_editor_markup.add(types.InlineKeyboardButton("Добавить вопрос", callback_data='add_question ' + str(surveyid)))
    survey_editor_markup.add(types.InlineKeyboardButton("Редактировать вопрос", callback_data='edit_question'))
    survey_editor_markup.add(types.InlineKeyboardButton("Удалить вопрос", callback_data='delete_question'))
    survey_editor_markup.add(types.InlineKeyboardButton("Готово", callback_data='menu'))
    title = formatted_title(get_survey_title(surveyid))
    questions = formatted_questions(get_survey_questions(surveyid))
    bot.edit_message_text(f"""
<b>{title[0]}</b>

Вопросы:
{questions}          
                     """, call.message.chat.id, call.message.id, parse_mode='html', reply_markup=survey_editor_markup)


def formatted_title(title):
    output = title[0]
    return output


def formatted_questions(questions):
    output = ""
    for i in range(len(questions)):
        output += str(i + 1) + ". " + questions[i]
    if output == "":
        output = "Нет"
    return output


def create_question(call, surveyid):
    new_question_id = push_question(task='Новый вопрос', answers=[], surveyid=surveyid)
    print(new_question_id, '|\/|')
    question_editor(call, surveyid, new_question_id)


def question_editor(call, surveyid, questionid):
    question_editor_markup = types.InlineKeyboardMarkup()
    question_editor_markup.add(types.InlineKeyboardButton("Изменить формулировку", callback_data='set_task ' + str(questionid)))
    if answer_exist(questionid):
        question_editor_markup.add(types.InlineKeyboardButton("Изменить вариант ответа", callback_data='edit_answer'))
    question_editor_markup.add(types.InlineKeyboardButton("Добавить вариант ответа", callback_data='add_answer'))
    question_editor_markup.add(types.InlineKeyboardButton("Удалить вариант ответа", callback_data='delete_answer'))
    question_editor_markup.add(types.InlineKeyboardButton("Готово", callback_data='survey_editor ' + str(surveyid)))
    bot.edit_message_text("Новый вопрос",
                          call.message.chat.id,
                          call.message.id,
                          reply_markup=question_editor_markup)


def set_task(call, questionid):
    bot.register_next_step_handler(call.message, get_text_input)
    task = input_buff


def select_available_survey(call):
    available_survey_markup = types.InlineKeyboardMarkup()
    # Запилить выбор только непройденных тестов ТУТ
    cursor.execute("SELECT title FROM surveys")
    available_survey_list = cursor.fetchall()
    if available_survey_list:
        for i in range(len(available_survey_list)):
            available_survey_markup.add(types.InlineKeyboardButton(available_survey_list[i][0],
                                                                   callback_data=available_survey_list[i][0]))
        reply_text = "Выберите опрос из предложенных"
    else:
        reply_text = "Нет доступных опросов"
    available_survey_markup.add(types.InlineKeyboardButton("<< Назад", callback_data='menu'))
    bot.edit_message_text(reply_text, call.message.chat.id, call.message.id, reply_markup=available_survey_markup)


def select_user_survey(call):
    user_survey_markup = types.InlineKeyboardMarkup(row_width=2)
    user_survey_list = get_user_surveys(call.message.from_user.id)
    button_row = []
    for title in user_survey_list:
        button_row.append(title[0])
        if len(button_row) == 2:
            user_survey_markup.row(types.InlineKeyboardButton(button_row[0], callback_data=button_row[0]),
                                   types.InlineKeyboardButton(button_row[1], callback_data=button_row[1]))
            button_row = []
    if button_row:
        user_survey_markup.add(types.InlineKeyboardButton(button_row[0], callback_data=button_row[0]))
    user_survey_markup.row(types.InlineKeyboardButton("<< Назад", callback_data='menu'))
    bot.edit_message_text("Ваши опросы:", call.message.chat.id, call.message.id, reply_markup=user_survey_markup)


# User input functions


def get_age(message):
    age = 0
    if age == 0:
        try:
            age = int(message.text)
            push_users(telegramid=message.from_user.id,
                      firstname=message.from_user.first_name,
                      lastname=message.from_user.last_name,
                      age=age)
            bot.send_message(message.from_user.id, 'Регистрация прошла успешно')
            menu(message.chat.id)
        except ValueError:
            bot.send_message(message.from_user.id, 'Цифрами, пожалуйста')
            bot.register_next_step_handler(message, get_age)


input_buff = ""
def get_text_input(message):
    global input_buff
    input_buff = message.text
    return


bot.polling(none_stop=True)

while True:
    pass
