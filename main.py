import telebot
import sqlite3
import os.path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "surveys.db")

db_connection = sqlite3.connect(db_path, check_same_thread=False)
cursor = db_connection.cursor()
# bot = telebot.TeleBot('5191014419:AAEVfQQbMc5SzkTQvghRkvMb9tjUnn5IpNc')
bot = telebot.TeleBot('5329387829:AAHdtHf3uf1J5lH8mTALsnm6NQznRUUYnOM')

quest = ''
ans = []
uid = 0
check = 0
adm_ans = 0
user_ans = 0
count_quest = 0
reg = False
all_users = []
admin = 431846556


def table_val(userid: int, firstname: str, lastname: str, username: str, age: int):
    cursor.execute('INSERT INTO users VALUES (?, ?, ?, ?, ?)', (userid, firstname, lastname, username, age))
    db_connection.commit()


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, message.from_user.username)
    cursor.execute("SELECT * FROM users WHERE username = ?", message.from_user.username)
    users_found = cursor.fetchall()
    print(users_found)
    if not users_found:
        bot.send_message(message.chat.id,
                         f'<b>Приветствую! {message.from_user.first_name} {message.from_user.last_name}</b>',
                         parse_mode='html')
        bot.send_message(message.chat.id, "Укажите ваш возраст:")
        bot.register_next_step_handler(message, get_age)
    else:
        bot.send_message(message.chat.id, "Вы уже зарегистрированы")


@bot.message_handler(content_types=['text'])
def get_age(message):
    age = 0
    if age == 0:
        try:
             age = int(message.text)
        # except age < 0:
        #      bot.send_message(message.from_user.id, 'О, так Вы из будущего!\nНо давайте без шуток');
        #      bot.register_next_step_handler(message, get_age);
        except Exception:
             bot.send_message(message.from_user.id, 'Цифрами, пожалуйста')
             bot.register_next_step_handler(message, get_age)
    us_id = message.from_user.id
    us_name = message.from_user.first_name
    us_sname = message.from_user.last_name
    username = message.from_user.username
    table_val(userid=us_id, firstname=us_name, lastname=us_sname, username=username, age=age)
    bot.send_message(message.from_user.id, 'Регистрация прошла успешно')


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
    adm_ans=message.text
    if adm_ans=='стоп':
        bot.send_message(admin, 'Вы хотите разослать опрос?')
        bot.register_next_step_handler(message, send_quest)
    else:
        ans.append(adm_ans)
        bot.register_next_step_handler(message, get_ans)


def send_quest(message):
    global check
    k=1
    if message.text == 'Да' or message.text == 'да':
        bot.send_message(message.chat.id, quest)
        for i in ans:
           bot.send_message(message.chat.id, str(k)+'. '+str(i))
           k += 1
        check = 1


def answer(message):
    db_connection.execute("SELECT * FROM questions;")
    questions = cursor.fetchall()
    bot.send_message(message.from_user.id, questions[count_quest][1])
    for i in range(10+2):
        if questions[count_quest][i] != "NULL":
            bot.send_message(message.from_user.id, questions[count_quest][i])
        else:
            break
    bot.send_message(admin, message.text)


bot.polling(none_stop=True)
