from telebot import TeleBot, types
from dotenv import load_dotenv
import os
import dataentery
import re
import flask
from flask import request

load_dotenv()
bot_token = os.getenv('Bot_Token')

bot = TeleBot(bot_token, threaded=False)

app = flask.Flask(__name__)

user_state = {}


admins = ["185913378h"]
@bot.message_handler(commands=['start'])
def handle_start(message):
    # user_id = str(message.from_user.id)
    # username = message.from_user.username
    first_name = message.from_user.first_name
    # last_name = message.from_user.last_name

    bot.send_message(message.chat.id, f'Welcome {first_name} \n لطفا شماره تلفن خود را مانند الگوی زیر وارد کنید. \n 09132051960')


PHONE_REGEX = re.compile(r"^09\d{9}$")

@bot.message_handler(func=lambda message: PHONE_REGEX.match(message.text or ""))
def save_phone(message):
    uid = message.from_user.id
    phone = message.text.strip()
    user_state.setdefault(uid, {})  # اگر وجود ندارد بساز
    user_state[uid]['phone'] = phone
    bot.send_message(message.chat.id, f'لطفاً تاریخ تولد خود را بصورت الگوی زیر کنید. \n  1368-07-05 \n yyyy-mm-dd')


DATE_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}$")

@bot.message_handler(func=lambda message: DATE_REGEX.match(message.text or ""))
def save_password(message):
    uid = message.from_user.id
    if uid not in user_state or 'phone' not in user_state[uid]:
        bot.send_message(message.chat.id, 'ابتدا شماره تلفن را وارد کنید.')
        return

    password = ''.join(message.text.split('-'))
    user_state[uid]['password'] = password

    phone = user_state[uid]['phone']
    user, result = dataentery.select_user(phone, password)
    
    
    user_name = message.from_user.first_name if user[1] == None or user[1] == '' else user[1]
    user_family = message.from_user.last_name if user[2] == None or user[2] == '' else user[2]
    
    user_state[uid]['user_name'] = user_name
    user_state[uid]['user_family'] = user_family

    inline_key = types.InlineKeyboardMarkup()
    for entry_date, result_id in result:
        date_str = entry_date.strftime("%Y-%m-%d")   # خروجی مثل 1404-04-30
    # تبدیل datetime میلادی به جلالی
        # jalali_date = jdatetime.date.fromgregorian(date=entry_date.date())
        # jalali_str = jalali_date.strftime("%Y-%m-%d")   # یا هر فرمتی که می‌خواهی
        inline_key.add(types.InlineKeyboardButton(date_str, callback_data=f'resultID_{result_id}'))
  
    bot.send_message(message.chat.id, 'ایتم مورد نظر را انتخاب کنید.', reply_markup=inline_key)


@bot.callback_query_handler(func=lambda call: call.data.startswith('resultID_'))
def show_result(call):
    uid = call.from_user.id
    result_id = int(call.data.split('_')[1])
    

    # اطمینان از وجود state
    if uid not in user_state or 'phone' not in user_state[uid]:
        bot.answer_callback_query(call.id, 'ابتدا شماره تلفن را وارد کنید.')
        bot.send_message(call.message.chat.id, 'لطفاً دوباره شماره تلفن را وارد کنید.')
        return

    phone = user_state[uid]['phone']
    user_state[uid]['result_id'] = result_id
    first_name = user_state[uid]['user_name']
    last_name = user_state[uid]['user_family']

    data = dataentery.select_result(phone, result_id)
    row = data[0]

    bot.send_message(call.message.chat.id, f"""
                     {first_name} {last_name}
                    \n شاخص های شما به شرح زیر است:
        شماره تماس شما: {row[2]} \n
       حداکثر درصد چربی بدن %: {row[27]} \n
        حداقل درصد چربی بدن %: {row[26]} \n
        توده بدون چربی بدنی kg: {row[23]} \n
        BMI: {row[4]} \n
        WHR: {row[6]} \n
        حداکثر نیاز روزانه به پروتئین gr: {row[12]} \n
""")



@app.route(f"/{bot_token}", methods=["POST"])
def webhook():
    raw = request.get_data().decode("utf-8")
    print(f"📦 Raw update: {raw}")  # Log the full payload
    update = types.Update.de_json(raw)
    print(f"✅ Parsed update: {update}")  # Log the parsed object
    bot.process_new_updates([update])
    return "OK", 200


@app.route("/")
def index():
    return "Bot is running!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
