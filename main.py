import telebot
from flask import Flask, request
import os

# Отримуємо змінні з налаштувань Render
TOKEN = os.environ.get('TOKEN')
URL = os.environ.get('RENDER_EXTERNAL_URL')

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Обробник команди /start (для перевірки)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Бот працює і готовий приймати заявки! ✅")

# ОСНОВНИЙ ОБРОБНИК ЗАЯВОК НА ВСТУП
@bot.chat_join_request_handler()
def handle_join_request(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_name = message.from_user.first_name

    text = f"Привіт, {user_name}! Щоб вступити до групи, ознайомтесь з правилами."
    
    # Створюємо кнопку
    markup = telebot.types.InlineKeyboardMarkup()
    btn = telebot.types.InlineKeyboardButton("✅ Я згоден з правилами", callback_data=f"approve_{chat_id}_{user_id}")
    markup.add(btn)

    # Надсилаємо правила (важливо: картинки мають лежати в тій же папці на GitHub)
    try:
        # Спробуємо надіслати фото
        if os.path.exists('rules.jpg'):
            with open('rules.jpg', 'rb') as photo:
                bot.send_photo(user_id, photo, caption=text, reply_markup=markup)
        else:
            bot.send_message(user_id, text, reply_markup=markup)
    except Exception as e:
        print(f"Помилка відправки: {e}")

# Обробка натискання кнопки
@bot.callback_query_handler(func=lambda call: call.data.startswith('approve_'))
def approve_request(call):
    data = call.data.split('_')
    chat_id = int(data[1])
    user_id = int(data[2])
    
    try:
        bot.approve_chat_join_request(chat_id, user_id)
        bot.answer_callback_query(call.id, "Заявку схвалено!")
        bot.edit_message_text("Ви прийняті до групи! 🎉", call.message.chat.id, call.message.message_id)
    except Exception as e:
        bot.answer_callback_query(call.id, "Сталася помилка, спробуйте ще раз.")
        print(f"Помилка схвалення: {e}")

# Вебхук для Flask
@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "OK", 200

@app.route('/')
def index():
    bot.remove_webhook()
    bot.set_webhook(url=URL + '/' + TOKEN)
    return "Бот активний!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
