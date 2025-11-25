import telebot
from telebot import types
from utils import Teste
from dotenv import load_dotenv
import os
from time import sleep
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from utils import gerar_qrcode_pix,gerar_payload_pix

# ==================================================
#  SERVIDOR FAKE PARA MANTER O RENDER ATIVO
# ==================================================

class ManipuladorWeb(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Servico ativo (Render Web Service OK)")


def iniciar_servidor_fake():
    porta = int(os.getenv("PORT", 10000))
    servidor = HTTPServer(("0.0.0.0", porta), ManipuladorWeb)
    print(f"[SERVIDOR FAKE] Ativo na porta {porta}")
    servidor.serve_forever()


# ==========================
#     BOT TELEGRAM
# ==========================

load_dotenv()
TOKEN = os.getenv("API_KEY_TELEGRAM")
bot = telebot.TeleBot(TOKEN)

# ==================================================
#   FUNÇÕES PARA OBTER PREÇO
# ==================================================

def obter_preco(moeda):
    return Teste(moeda, "BRL").requesicao()

# ==================================================
#   Função para apagar mensagens antigas
# ==================================================

def apagar_mensagens(chat_id, ultima_msg):
    for i in range(10):
        try:
            bot.delete_message(chat_id, ultima_msg - i)
        except:
            pass

# ==================================================
#  MENUS PARA ESCOLHA DE MOEDA
# ==================================================

def exibir_menu_usdt(chat_id):
    preco = obter_preco("USDT")
    cinco = round(preco * 5, 2)
    dez = round(preco * 10, 2)

    teclado = types.InlineKeyboardMarkup(row_width=1)
    teclado.add(
        types.InlineKeyboardButton(f"🟢 5 USDT | {cinco} BRL", callback_data="usdt_5"),
        types.InlineKeyboardButton(f"🟢 10 USDT | {dez} BRL", callback_data="usdt_10"),
    )

    bot.send_message(
        chat_id,
        "Selecione a quantidade desejada:",
        reply_markup=teclado,
        parse_mode="Markdown"
    )


def exibir_menu_xmr(chat_id):
    preco = obter_preco("XMR")
    cinco = round(preco * 5, 2)
    dez = round(preco * 10, 2)

    teclado = types.InlineKeyboardMarkup(row_width=1)
    teclado.add(
        types.InlineKeyboardButton(f"🟠 5 XMR | {cinco} BRL", callback_data="xmr_5"),
        types.InlineKeyboardButton(f"🟠 10 XMR | {dez} BRL", callback_data="xmr_10"),
    )

    bot.send_message(
        chat_id,
        "Selecione a quantidade desejada:",
        reply_markup=teclado,
        parse_mode="Markdown"
    )


# ==================================================
#   MENU PRINCIPAL (/start)
# ==================================================

@bot.message_handler(["start"])
def exibir_menu_principal(msg):
    chat_id = msg.chat.id
    apagar_mensagens(chat_id, msg.message_id)

    preco_xmr = obter_preco("XMR")
    preco_usdt = obter_preco("USDT")

    teclado = types.InlineKeyboardMarkup(row_width=1)

    teclado.add(
        types.InlineKeyboardButton(f"🟠 XMR | {preco_xmr} BRL", callback_data="menu_xmr"),
        types.InlineKeyboardButton(f"🟢 USDT | {preco_usdt} BRL", callback_data="menu_usdt"),
    )

    bot.send_message(
        chat_id,
        "🔄 *Cotações Atualizadas*\nEscolha uma moeda:",
        reply_markup=teclado,
        parse_mode="Markdown"
    )

# ==================================================
#   CONFIRMAR OU CANCELAR
# ==================================================

def exibir_confirmacao_moeda(chat_id, moeda, quantidade):
    try:
        preco = obter_preco(moeda)
    except:
        preco = None

    if preco:
        total = round(preco * quantidade, 2)
        mensagem = (
            f"Você selecionou *{quantidade} {moeda}*\n"
            f"Preço unitário: *{preco} BRL*\n"
            f"Valor total: *{total} BRL*\n\n"
            "Deseja confirmar a compra?"
        )
    else:
        mensagem = "Erro ao obter o preço da moeda. Tente novamente."

    teclado = types.InlineKeyboardMarkup(row_width=2)
    teclado.add(
        types.InlineKeyboardButton(
            "✅ Confirmar Compra", callback_data=f"confirmar_{moeda}_{quantidade}"
        ),
        types.InlineKeyboardButton(
            "❌ Cancelar", callback_data="cancelar"
        )
    )

    bot.send_message(chat_id, mensagem, parse_mode="Markdown", reply_markup=teclado)


def confirmar_compra(call, moeda, quantidade):
    chat_id = call.message.chat.id

    try:
        preco = obter_preco(moeda)
    except:
        preco = None

    if preco:
        total = round(preco * quantidade, 2)

        chave_pix = "487.495.628-94"  # <<< ALTERE AQUI SUA CHAVE PIX

        payload = gerar_payload_pix(total, chave_pix)
        caminho_qr = gerar_qrcode_pix(payload)

        mensagem = (
            f"✅ *Compra Confirmada!*\n"
            f"Moeda: *{moeda}*\n"
            f"Quantidade: *{quantidade}*\n"
            f"Total: *{total} BRL*\n\n"
            "🔶 *Escaneie o QR CODE abaixo para pagar via PIX*\n"
            "Ou copie e cole o código PIX:\n\n"
            f"```\n{payload}\n```"
        )

        with open(caminho_qr, "rb") as img:
            bot.send_photo(chat_id, img, caption=mensagem, parse_mode="Markdown")

    else:
        bot.send_message(chat_id, "Erro ao confirmar compra.", parse_mode="Markdown")



def cancelar_operacao(chat_id):
 
    bot.send_message(chat_id, "Use /start para voltar ao menu.",parse_mode="Markdown")

# ==================================================
#   CALLBACKS
# ==================================================

@bot.callback_query_handler(func=lambda c: True)
def tratar_callback(call):
    chat_id = call.message.chat.id
    dados = call.data

    # Menus principais
    if dados == "menu_xmr":
        exibir_menu_xmr(chat_id)

    elif dados == "menu_usdt":
        exibir_menu_usdt(chat_id)

    # Seleção de quantidades XMR
    elif dados.startswith("xmr_"):
        quantidade = int(dados.split("_")[1])
        exibir_confirmacao_moeda(chat_id, "XMR", quantidade)

    # Seleção de quantidades USDT
    elif dados.startswith("usdt_"):
        quantidade = int(dados.split("_")[1])
        exibir_confirmacao_moeda(chat_id, "USDT", quantidade)

    # Confirmações gerais
    elif dados.startswith("confirmar_"):
        _, moeda, quantidade = dados.split("_")
        confirmar_compra(call, moeda, int(quantidade))

    # Cancelamento
    elif dados == "cancelar":
        
        cancelar_operacao(chat_id)

# ==================================================
#   EXECUÇÃO DO BOT
# ==================================================

if __name__ == "__main__":
    threading.Thread(target=iniciar_servidor_fake, daemon=True).start()

    print("Bot executando no Render...")

    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as erro:
            print("Erro no polling:", erro)
            sleep(3)
            
