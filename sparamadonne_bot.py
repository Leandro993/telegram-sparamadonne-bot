from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
import requests
from flask import Flask
import threading
import os

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

# Funzione per recuperare immagini
async def fetch_image_urls(query: str):
    image_urls = []
    max_results = 50
    results_per_request = 10

    for start_index in range(1, max_results, results_per_request):
        search_url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={GOOGLE_CX}&searchType=image&num={results_per_request}&start={start_index}"
        response = requests.get(search_url)
        if response.status_code == 200:
            data = response.json()
            new_urls = [item['link'] for item in data.get('items', [])]
            image_urls.extend(new_urls)
            if not new_urls:
                break
        else:
            print(f"Error fetching images: {response.status_code}")
            break
    return image_urls

# Funzione per inviare immagini dal bot
async def send_images_from_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    chat_id = update.effective_chat.id
    image_urls = await fetch_image_urls(query)

    if not image_urls:
        await update.message.reply_text("Nessuna immagine trovata.")
        return

    for url in image_urls:
        try:
            await context.bot.send_photo(chat_id=chat_id, photo=url)
            await asyncio.sleep(3)
        except Exception as e:
            print(f"Error sending image {url}: {e}")

# Funzione per il comando start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Benvenuto! Invia una parola chiave per cercare immagini su Google.')

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

    asyncio.create_task(ping_bot())
    await application.run_polling()

# Avvia Flask in un thread separato
def run_flask():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

# Main
if __name__ == '__main__':
    # Avvia Flask in un thread separato
    threading.Thread(target=run_flask).start()

    # Usa il ciclo di eventi corrente
    asyncio.run(run_bot())
