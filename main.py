import config
import telebot.types
from telebot import types
import mysql.connector
from mysql.connector import errorcode

bot = telebot.TeleBot(config.api_token, parse_mode=None)
db = mysql.connector.connect(host=config.host, user=config.user, password=config.password, database=config.database)
cursor = db.cursor()

user_data = {}

class User:
    def __init__(self, name):
        self.name = name
        self.email = ''
        self.phone = ''
        
@bot.message_handler(commands=['start'])
def start_handler(message):
    menu = types.ReplyKeyboardMarkup(True, False)
    menu.row('/start', '/stop')
    menu.row('/регистрация')
    bot.send_message(message.from_user.id, "Добро пожаловать", reply_markup = menu)

@bot.message_handler(commands=['регистрация'])
def registration(message):
    bot.send_message(message.chat.id, "Процесс регистрации потребует от вас ввода имени, адреса электронной почты и номера телефона")
    msg = bot.send_message(message.chat.id, 'Укажите Ваше имя - Фамилия и Инициалы')
    bot.register_next_step_handler(msg, process_registration_name)
    
def process_registration_name(message):
    user_id = message.from_user.id
    user_data[user_id] = User(message.text)

    msg = bot.send_message(message.chat.id, 'Адрес электронной почты')
    bot.register_next_step_handler(msg, process_registration_finish)

def process_registration_finish(message):
    user_id = message.from_user.id
    email = message.text
    user = user_data[user_id]
    user.email = email
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    button_phone = types.KeyboardButton(text="Отправить номер телефона", request_contact=True)
    keyboard.add(button_phone)
    bot.send_message(message.chat.id, 'Далее необходимо разрешить боту доступ к вашему номеру', reply_markup=keyboard)
     
@bot.message_handler(content_types=['contact'])
def contact(message):
    if message.contact is not None:
        try: 
            print(message.contact)
            user_id = message.from_user.id
            user = user_data[user_id]
            user.phone = message.contact.phone_number
            #bot.send_message(message.chat.id, "ID:" + str(user_id) + " email:" + user.email + " phone:" + user.phone)
            query = "INSERT INTO `Diplom`.`staff` (`name_staff`, `email_staff`, `phone_staff`, `telegram_id`) VALUES (%s, %s, %s, %s);"
            values = (user.name, user.email, user.phone, user_id)
            cursor.execute(query, values)
            db.commit()
            bot.send_message(message.chat.id, "Регистрация прошла успешно.")
        except mysql.connector.Error as err:
            if err.errno == 1062:
                bot.send_message(message.chat.id, "Пользователь с таким почтовым адресом/телефоном уже зарегистрирован в системе.")
                return
            else:
                bot.send_message(message.chat.id, err)
                return



bot.polling(none_stop=True)   