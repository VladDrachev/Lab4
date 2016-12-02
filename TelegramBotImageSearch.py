import os
import re
import logging
import telebot
from telebot import types
import requests
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup as bs

bot = telebot.TeleBot('195629794:AAE_sDnGaDmdcVozkKMSn9G88ckR413Rheg')

# Начальные данные
command = 'Search'
size_list = {}
number_list = {}
users = ''

# Команда /start
@bot.message_handler(commands=['start'])
def SendInfo(message):
    bot.send_message(message.chat.id, 'Привет! я твой бот.\nЯ могу найти для тебя изображение.',
                     reply_markup=Keyboard())

# Команда /help
@bot.message_handler(commands=['help'])
def SendHelp(message):
    bot.send_message(message.chat.id, 'Для поиска картинок ввeдите запрос.\n\nСписок доступных команд:\n\n'
                                      '/start - начать работу с ботом\n'
                                      '/about - информация о боте\n'
                                      '/size - настроить размер изображения\n'
                                      '/number - настроить кол-во картинок \n'
                                      '/settings - посмотреть текущие настройки')
# Команда /about
@bot.message_handler(commands=['about'])
def SendHelp(message):
    bot.send_message(message.chat.id, 'Information:'
                                      '\n\n>TelegramBot v.0.02, built on 01.12.2016'
                                      '\n>Developer: Vlad Drachev')
# Команда /size - задаёт размер картинки
@bot.message_handler(commands=['size'])
def Sendnumber(message):
    markup = types.ReplyKeyboardMarkup()
    markup.row('большой', 'средний', 'маленький')
    bot.send_message(message.chat.id, 'Выберите размер изображения.', reply_markup=markup)
    global command
    command = 'size'

# Команда /number - задаёт кол-во картинок
@bot.message_handler(commands=['number'])
def Sendnumber(message):
    markup = types.ReplyKeyboardMarkup()
    markup.row('1', '2', '3', '4')
    markup.row('5', '10', '15', '20')
    bot.send_message(message.chat.id, 'Выберите какое количество изображений вы хотели бы найти.', reply_markup=markup)
    global command
    command = 'number'

# Команда /settings - настройки пользвателя (размер и кол-во изображений)
@bot.message_handler(commands=['settings'])
def SendImages(message):
    global size_list
    global number_list
    global users

    # Формирование данных пользователя в том случае, если его нет в списке
    if users.find(str(message.chat.id)) == -1:
        users = users + str(message.chat.id) + ' '
        size_list[message.chat.id] = '&tbs=isz:m'
        number_list[message.chat.id] = 1

    # Формирование строки
    if (size_list[message.chat.id] == '&tbs=isz:ex,iszw:1920,iszh:1080'):
        text = 'большой'
    if (size_list[message.chat.id] == '&tbs=isz:m'):
        text = 'средний'
    if (size_list[message.chat.id] == '&tbs=isz:s'):
        text = 'маленький'
    bot.send_message(message.chat.id, 'Размер: ' + text + '\n' + 'Количество: ' + str(number_list[message.chat.id]),
                     reply_markup=Keyboard())

# Обработка текста
@bot.message_handler(content_types='text')
def SendCommands(message):
    global command
    global size_list
    global number_list
    global users

    # Формирование данных пользователя в том случае, если его нет в списке
    if users.find(str(message.chat.id)) == -1:
        users = users + str(message.chat.id) + ' '
        size_list[message.chat.id] = '&tbs=isz:m'
        number_list[message.chat.id] = 1

    # Обработка данных команды size
    if (command == 'size'):
        if (message.text == 'большой'):
            size_list[message.chat.id] = '&tbs=isz:ex,iszw:1920,iszh:1080'
        if (message.text == 'средний'):
            size_list[message.chat.id] = '&tbs=isz:m'
        if (message.text == 'маленький'):
            size_list[message.chat.id] = '&tbs=isz:s'
        text = 'OK'

    # Обработка данных команды number
    if (command == 'number'):
        number_list[message.chat.id] = message.text
        text = 'OK'

    # Обработка данных для поиска изображений
    if (command == 'Search'):
        bot.send_message(message.chat.id, "Ожидайте, идёт поиск изображений...")
        images = SearchGoogleImages(message.text, int(number_list[message.chat.id]), size_list[message.chat.id],
                                    message.chat.id)
        # Загрузка изображений чат
        for image in images:
            bot.send_photo(message.chat.id, open(image, 'rb'))
        text = 'Поиск завершён.'
    command = 'Search'
    bot.send_message(message.chat.id, text=text, reply_markup=Keyboard())

# Клавиатура
def Keyboard():
    markup = types.ReplyKeyboardMarkup()
    markup.row('/help', '/about')
    markup.row('/size', '/number')
    markup.row('/settings')
    return markup

# Поиск ссылки на картинку
def SearchSrcImage(s):
    s = str(s)
    begin = s.find('"ou":') + 6
    end = s.find('"ow":') - 2
    return (s[begin:end])

def SearchGoogleImages(query, number, size, id):
    # Создание папки по id пользователя
    # Путь к текущей дериктории (папки с программой)
    path = os.getcwd()
    # Соединение пути данной папки + id пользователя
    path = os.path.join(path, str(id))

    # Создание папки если её не существует
    if not os.path.exists(path):
        os.makedirs(path),

    # Запрос поисковой системе
    # Разделяем строку на элементы по пробелам
    query = query.split()
    # Склеиваем элементы в одну строку
    query = '+'.join(query)
    # Добавляем текст в запрос
    query = 'https://www.google.ru/search?' \
            'q=' + query + \
            '&newwindow=1' \
            '&source=lnms' \
            '&tbm=isch' + size


    # Производим запрос
    req = requests.get(query, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6,1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                                     'Chrome/43.0.2357.134 Safari/537.36'})
    soup = bs(req.content, "html.parser")
    images = soup.find_all('div', {'class': re.compile('rg_meta')})

    # Список с путями к изображениям
    imagePaths = []

    n = 0
    # Перебираем каждую ссылку с изображением
    while n < number:
        n += 1
        tag = images[n]
        try:
            # Код изображения
            data = requests.get(SearchSrcImage(tag))
            # Загрузка изображения
            image = Image.open(BytesIO(data.content))
        except:
            number += 1
            continue
        # Формирование пути к изображению
        imagePath = os.path.join(path, str(n) + '.' + image.format.lower())
        # Сохранеие изображения на диск
        image.save(imagePath)
        # Формирование списка с путями изображений
        imagePaths.append(imagePath)
    return imagePaths

if __name__ == '__main__':
    # Log-файл
    logging.basicConfig(filename='botLog.log',
                        format='%(filename)s[LINE:%(lineno)d]# '
                               '%(levelname)-8s [%(asctime)s]  '
                               '%(message)s',
                        level=logging.DEBUG)

    logging.info('Start the bot. ')

    # В случае возникновения оштбки в Log-файл будет добавлена информация и перезапущен бот
    try:
        # Запуск бота
        bot.polling(none_stop=True)
    except Exception:
        logging.critical('ERROR...')
    finally:
        bot.polling(none_stop=True)