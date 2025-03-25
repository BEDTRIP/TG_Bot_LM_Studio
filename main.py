import telebot
from telebot import types

import requests
import jsons
from Class_ModelResponse import ModelResponse

# Замените 'YOUR_BOT_TOKEN' на ваш токен от BotFather
API_TOKEN = '7016988516:AAFLXECp_n_BffK0anyCQWCF-8Q3HsYp5Bs'
bot = telebot.TeleBot(API_TOKEN)

# Определение команд и их описаний
commands = [
    types.BotCommand("/start", "вывод всех доступных команд"),
    types.BotCommand("/model", "выводит название используемой языковой модели"),
    types.BotCommand("/clear", "отчистить контекст")
]

# Установка команд
bot.set_my_commands(commands)

# Словарь для хранения контекста пользователей
user_contexts = {}

# Команды
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.from_user.id in user_contexts:
        user_contexts.pop(message.from_user.id)
    welcome_text = (
        "Привет! (Это маленький бот и он работает только с английским языком)\n"
        "Доступные команды:\n"
        "/start - вывод всех доступных команд\n"
        "/model - выводит название используемой языковой модели\n"
        "Отправьте любое сообщение, и я отвечу с помощью LLM модели."
    )
    bot.reply_to(message, welcome_text)


@bot.message_handler(commands=['model'])
def send_model_name(message):
    if message.from_user.id in user_contexts:
        user_contexts.pop(message.from_user.id)
    # Отправляем запрос к LM Studio для получения информации о модели
    response = requests.get('http://localhost:1234/v1/models')

    if response.status_code == 200:
        model_info = response.json()
        model_name = model_info['data'][0]['id']
        bot.reply_to(message, f"Используемая модель: {model_name}")
    else:
        bot.reply_to(message, 'Не удалось получить информацию о модели.')

@bot.message_handler(commands=['clear'])
def send_welcome(message):
    if message.from_user.id in user_contexts:
        user_contexts.pop(message.from_user.id)
    bot.reply_to(message, 'Контекст сброшен. Завадавайте вопрос')

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_query = message.text

    user_id = message.from_user.id
    user_query = message.text

    # Обновляем контекст пользователя
    if user_id not in user_contexts:
        user_contexts[user_id] = []
    user_contexts[user_id].append(message.text)

    str = ''
    for msg in user_contexts[user_id]:
        str += msg + '\n\n'

    request = {
        "messages": [
          {
            "role": "user",
            "content": str
          },
    ]
  }
    response = requests.post(
        'http://localhost:1234/v1/chat/completions',
        json=request
    )

    if response.status_code == 200:
        model_response :ModelResponse = jsons.loads(response.text, ModelResponse)
        respons_text = model_response.choices[0].message.content
        user_contexts[user_id].append(respons_text)
        bot.reply_to(message, respons_text)
    else:
        if message.from_user.id in user_contexts:
            user_contexts.pop(message.from_user.id)
        bot.reply_to(message, 'Произошла ошибка при обращении к модели.\nКонтекст сброшен. Завадавайте вопрос')


# Запуск бота
if __name__ == '__main__':
    bot.infinity_polling()