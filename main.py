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
    for i in range(10):
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

def teste(chat_id):
    # Mensagem melhorada para a escolha de 5 XMR
    try:
        price = get_xmr()
    except Exception:
        price = None

    amount = 5
    if price:
        total = round(price * amount, 2)
        text = (
            f"Você escolheu *{amount} XMR*\n"
            f"Preço unitário: *{price} BRL*\n"
            f"Valor total: *{total} BRL*\n\n"
            "Confirme para receber instruções de pagamento ou cancele para voltar ao menu."
        )
    else:
        text = (
            "Você escolheu *5 XMR*\n"
            "Não foi possível obter o preço agora. Tente novamente mais tarde."
        )

    teclado = types.InlineKeyboardMarkup(row_width=2)
    teclado.add(
        types.InlineKeyboardButton("✅ Confirmar Compra", callback_data="confirm_XMR_5"),
        types.InlineKeyboardButton("❌ Cancelar", callback_data="cancel_XMR_5"),
    )

    bot.send_message(chat_id, text, reply_markup=teclado, parse_mode="Markdown")


def confirmar_compra_xmr_5(call):
    chat_id = call.message.chat.id
    try:
        price = get_xmr()
    except Exception:
        price = None

    amount = 5
    if price:
        total = round(price * amount, 2)
        text = (
            f"✅ *Pedido Confirmado*\n"
            f"Quantidade: *{amount} XMR*\n"
            f"Total: *{total} BRL*\n\n"
            "Envie o comprovante de pagamento neste chat para finalizar.\n"
            "Após conferência, liberaremos as chaves/transferência."
        )
    else:
        text = "✅ Pedido confirmado. Em breve enviaremos instruções de pagamento."

    bot.send_message(chat_id, text, parse_mode="Markdown")


def cancelar_compra_xmr_5(call):
    chat_id = call.message.chat.id
    bot.send_message(chat_id, "❌ Operação cancelada. Use /start para voltar ao menu.")


@bot.callback_query_handler(func=lambda c: True)
def callback_query(call):
    chat_id = call.message.chat.id

    if call.data == "xmr":
        menu_xmr(chat_id)
    elif call.data == "usdt":
        menu_usdt(chat_id)
    elif call.data == "moeda_XMR_5":
        teste(chat_id)
    elif call.data == "moeda_XMR_10":
        teste(chat_id)
    elif call.data == "confirm_XMR_5":
        confirmar_compra_xmr_5(call)
    elif call.data == "cancel_XMR_5":
        cancelar_compra_xmr_5(call)
        
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
