import telebot 
from telebot import types
from utils import *
from dotenv import load_dotenv
import os
from time import sleep
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# ==========================
#  SERVIDOR PARA FINGIR WEB
# ==========================

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Service online (Render Web Service OK)")

def start_fake_webserver():
    port = int(os.getenv("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    print(f"[FAKE WEB] Servidor Web iniciado na porta {port}")
    server.serve_forever()

# ==========================
#     BOT (POLLING)
# ==========================

load_dotenv()
TOKEN = os.getenv("API_KEY_TELEGRAM")
bot = telebot.TeleBot(TOKEN)

def get_usdt():
    return Teste("USDT", "BRL").requesicao()

def get_xmr():
    return Teste("XMR", "BRL").requesicao()

def apagar(chat_id, last_msg):
    for i in range(3):
        try:
            bot.delete_message(chat_id, last_msg - i)
        except:
            pass

def menu_usdt(chat_id):
    USDT = get_usdt()
    cinco = round(USDT * 5, 2)
    dez = round(USDT * 10, 2)

    teclado = types.InlineKeyboardMarkup(row_width=1)
    teclado.add(
        types.InlineKeyboardButton(f"🟢 Cinco Moedas | {cinco}", callback_data="moeda_USDT_5"),
        types.InlineKeyboardButton(f"🟢 Dez Moedas | {dez}", callback_data="moeda_USDT_10"),
    )
    bot.send_message(chat_id, "Selecione a quantidade:", reply_markup=teclado, parse_mode="Markdown")

def menu_xmr(chat_id):
    XMR = get_xmr()
    cinco = round(XMR * 5, 2)
    dez = round(XMR * 10, 2)

    teclado = types.InlineKeyboardMarkup(row_width=1)
    teclado.add(
        types.InlineKeyboardButton(f"🟠 Cinco Moedas | {cinco}", callback_data="moeda_XMR_5"),
        types.InlineKeyboardButton(f"🟠 Dez Moedas | {dez}", callback_data="moeda_XMR_10"),
    )
    bot.send_message(chat_id, "Selecione a quantidade:", reply_markup=teclado, parse_mode="Markdown")

@bot.message_handler(["start"])
def menu(msg):
    chat_id = msg.chat.id
    apagar(chat_id, msg.message_id)

    XMR = get_xmr()
    USDT = get_usdt()

    teclado = types.InlineKeyboardMarkup(row_width=1)
    teclado.add(
        types.InlineKeyboardButton(f"🟠 XMR | {XMR}", callback_data="xmr"),
        types.InlineKeyboardButton(f"🟢 USDT | {USDT}", callback_data="usdt"),
    )

    bot.send_message(chat_id,
        "🔄 *Cotações Atualizadas*\n"
        "Selecione a moeda:",
        reply_markup=teclado,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda c: True)
def callback_query(call):
    chat_id = call.message.chat.id

    if call.data == "xmr":
        menu_xmr(chat_id)
    elif call.data == "usdt":
        menu_usdt(chat_id)
    elif call.data == "moeda_XMR_5":
        menu_usdt(chat_id)
# ==========================
#     EXECUTAR TUDO
# ==========================
if __name__ == "__main__":
    # Inicia o servidor falso em paralelo
    threading.Thread(target=start_fake_webserver, daemon=True).start()

    print("Bot rodando no Render (POLLING + Porta Aberta Fake)")

    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print("Erro no polling:", e)
            sleep(3)
