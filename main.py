import telebot 
from telebot import types
from utils import *
from dotenv import load_dotenv
import os

USDT = Teste("USDT","BRL").requesicao()
XMR = Teste("XMR","BRL").requesicao()

load_dotenv()

BOT_TOKEN = os.getenv("API_KEY_TELEGRAM")


token = BOT_TOKEN

bot = telebot.TeleBot(token)

def apagar(chat_id, last_msg):
       for i in range(3):
        try:
            bot.delete_message(chat_id, last_msg - i)
        except:
            pass
    
def menu_usdt(chat_id):
 
        
    cindo_moeda = round(USDT * 5,2)
    dez_moeda = round(USDT * 10,2)
    
    teclado = types.InlineKeyboardMarkup(row_width=1)

    teclado.add(
        types.InlineKeyboardButton(f"🟢 Cinco Moedas | {cindo_moeda}", callback_data="moeda_XMR"),
        types.InlineKeyboardButton(f"🟢 Dez Moeda |{dez_moeda}", callback_data="moeda_USDT"),
        
        )

    bot.send_message(
        chat_id,
        "Selecione a quantidae para ver mais detalhes:",
        reply_markup=teclado,
        parse_mode="Markdown"
    )
    
def menu_xrm(chat_id):
    cindo_moeda = round(XMR * 5,2)
    dez_moeda = round(XMR * 10,2)
    
    teclado = types.InlineKeyboardMarkup(row_width=1)

    teclado.add(
        types.InlineKeyboardButton(f"🟠 Cinco Moedas | {cindo_moeda}", callback_data="moeda_XMR"),
        types.InlineKeyboardButton(f"🟠 Dez Moeda |{dez_moeda}", callback_data="moeda_USDT"),
        
        )

    bot.send_message(
        chat_id,
        "Selecione a quantidae para ver mais detalhes:",
        reply_markup=teclado,
        parse_mode="Markdown"
    )

@bot.message_handler(["start"])
def menu(msg):
    chat_id = msg.chat.id
    last_msg = msg.message_id
    apagar(chat_id,last_msg)
    teclado = types.InlineKeyboardMarkup(row_width=1)
    botao1 = types.InlineKeyboardButton(f"🟠 XMR | {XMR}", callback_data="xrm")
    botao2 = types.InlineKeyboardButton(f"🟢 USDT| {USDT}", callback_data="usdt")
    teclado.add(botao1,botao2)
    
    bot.send_message(
    msg.chat.id,
    "🔄 *Cotações Atualizadas*\n"
    "Selecione a moeda abaixo para ver detalhes:",
    reply_markup=teclado,
    parse_mode="Markdown"
)



@bot.callback_query_handler(func=lambda c: True)
def call_back(callback):
    data = callback.data
    chat_id = callback.message.chat.id
    msg_id = callback.message.message_id

    bot.answer_callback_query(callback.id)

    if data == "xrm":
        bot.edit_message_text(
            "👇 Escolha a quantidade de moeda:",
            chat_id,
            msg_id,
            menu_xrm(chat_id)
        )
        return
    elif data == "usdt":
        bot.edit_message_text(
            "👇 Escolha a quantidade de moeda:",
            chat_id,
            msg_id,
            menu_usdt(chat_id)
        )
        return


bot.infinity_polling()