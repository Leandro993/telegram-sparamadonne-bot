import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
import threading
import os
import requests

TOKEN = '7114806273:AAHgtfAfV391U0LgrWFy554-RkVcUb57l18'
GOOGLE_API_KEY = 'AIzaSyDn5KBLfwN3U9Fp9i084plI_Hzb5G8_XCo'
GOOGLE_CX = '4766ab6c805714436'

# Funzione per pingare periodicamente il bot ogni 5 minuti
async def ping_bot():
    while True:
        try:
            response = requests.get('https://telegram-sparamadonne-bot.onrender.com')  # Modifica con l'URL del tuo bot
            if response.status_code == 200:
                print("Ping success!")
            else:
                print(f"Ping failed with status: {response.status_code}")
        except Exception as e:
            print(f"Error while pinging: {e}")
        await asyncio.sleep(300)

# Funzione per il comando start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Benvenuto! Invia una parola chiave per cercare immagini su Google.')

# Funzione per inviare immagini dal bot (semplificata)
async def send_images_from_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Funzionalità di ricerca immagini non implementata in questo esempio.")

# Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

# Funzione per avviare il bot
async def run_bot():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_images_from_search))

    # Aggiungi il task per il ping periodico
    asyncio.create_task(ping_bot())

    # Avvia il polling del bot
    await application.run_polling()

# Funzione per avviare Flask in un thread separato
def run_flask():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    # Avvia Flask in un thread separato
    threading.Thread(target=run_flask).start()

    # Esegui il bot nel ciclo di eventi corrente
    asyncio.run(run_bot())
