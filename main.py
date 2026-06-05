import telebot
from flask import Flask, request
import os

TOKEN = os.environ.get('TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Обробка ВСІХ вхідних повідомлень (включаючи /start)
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    if message.text == '/start':
        bot.reply_to(message, "Бот працює! Спробуй подати запит на вступ до групи.")
    else:
        bot.reply_to(message, "Я отримав твоє повідомлення!")

# Обробка запитів на вступ
@bot.chat_join_request_handler()
def handle_join_request(message):
    bot.approve_chat_join_request(message.chat.id, message.from_user.id)
    bot.send_message(message.from_user.id, "Ласкаво просимо! Ось наші правила...")

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
