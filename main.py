import telebot
import os
from flask import Flask, request

# 1. Налаштування
TOKEN = os.environ.get('TOKEN')
URL = os.environ.get('RENDER_EXTERNAL_URL') # Render сам підставить сюди твій лінк
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# 2. Обробка команд в ЛС
@bot.message_handler(commands=['start'])
def start_msg(message):
    bot.send_message(message.chat.id, "Бот активований! Я бачу твої повідомлення.")

# 3. Обробка запитів на вступ (Join Request)
@bot.chat_join_request_handler()
def join_request(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    # Відправляємо правила в ЛС
    bot.send_message(user_id, "Вітаю! Щоб потрапити в групу, прочитай правила:")
    
    # Кнопка схвалення
    markup = telebot.types.InlineKeyboardMarkup()
    btn = telebot.types.InlineKeyboardButton("✅ Прийняти правила", callback_data=f"accept_{chat_id}_{user_id}")
    markup.add(btn)
    bot.send_message(user_id, "Ось правила: [Твій текст правил]", reply_markup=markup)

# 4. Обробка натискання кнопки
@bot.callback_query_handler(func=lambda call: call.data.startswith('accept_'))
def accept_rules(call):
    chat_id = int(call.data.split('_')[1])
    user_id = int(call.data.split('_')[2])
    bot.approve_chat_join_request(chat_id, user_id)
    bot.answer_callback_query(call.id, "Заявку схвалено!")

# 5. Вебхук
@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "OK", 200

# 6. Встановлення вебхуку при запуску
@app.route('/')
def index():
    bot.remove_webhook()
    bot.set_webhook(url=f"{URL}/{TOKEN}")
    return "Webhook set!", 200

if __name__ == "__main__":
    # ВАЖЛИВО: Обов'язково зайти за посиланням / після деплою
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
