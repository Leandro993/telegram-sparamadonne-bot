from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
import asyncio
import threading
import requests

TOKEN = '7114806273:AAHgtfAfV391U0LgrWFy554-RkVcUb57l18'
GOOGLE_API_KEY = 'AIzaSyDn5KBLfwN3U9Fp9i084plI_Hzb5G8_XCo'
GOOGLE_CX = '4766ab6c805714436'

# Flask app per gestire il ping
app = Flask(__name__)

@app.route('/')
def home():
    return "Il bot è attivo!", 200

# Variabile globale per controllare l'interruzione
stop_sending = {}

# Funzione per pingare periodicamente il bot
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

        await asyncio.sleep(300)  # 300 secondi = 5 minuti

# Funzione per recuperare le immagini da Google
async def fetch_image_urls(query: str):
    image_urls = []
    max_results = 20
    results_per_request = 10  # Google consente un massimo di 10 risultati per richiesta

    for start_index in range(1, max_results, results_per_request):
        search_url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={GOOGLE_CX}&searchType=image&num={results_per_request}&start={start_index}"
        response = requests.get(search_url)

        if response.status_code == 200:
            data = response.json()
            new_urls = [item['link'] for item in data.get('items', [])]
            image_urls.extend(new_urls)

            # Interrompi la ricerca se non ci sono più risultati
            if not new_urls:
                break
        else:
            print(f"Error fetching images: {response.status_code}")
            break

    return image_urls

# Funzione per inviare le immagini dal bot
async def send_images_from_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    chat_id = update.effective_chat.id
    print(f"Received search query: {query}")  # Debug

    image_urls = await fetch_image_urls(query)

    if not image_urls:
        await update.message.reply_text("Nessuna immagine trovata.")
        return

    print(f"Found {len(image_urls)} images for query '{query}'")  # Debug
    stop_sending[chat_id] = False  # Reset il flag per il chat_id

    for url in image_urls:
        # Controlla il flag `stop_sending` prima di inviare la foto
        if stop_sending.get(chat_id, False):
            await update.message.reply_text("Invio interrotto.")
            print(f"Stopped sending images for chat_id: {chat_id}")  # Debug
            return
        
        try:
            await context.bot.send_photo(chat_id=chat_id, photo=url)
        except Exception as e:
            print(f"Error sending image {url}: {e}")
        
        # Pausa breve per controllare il comando /stop
        await asyncio.sleep(3)

# Funzione per interrompere l'invio
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    stop_sending[chat_id] = True  # Imposta il flag per interrompere
    await update.message.reply_text("Interruzione richiesta. L'invio verrà fermato a breve.")
    print(f"Command /stop received for chat_id: {chat_id}")  # Debug

# Funzione per interrompere l'invio
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    stop_sending[chat_id] = True
    await update.message.reply_text("Interruzione richiesta. L'invio verrà fermato a breve.")
    print(f"Command /stop received for chat_id: {chat_id}")  # Debug

# Funzione per il comando start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Benvenuto! Invia una parola chiave per cercare immagini su Google. Usa /stop per interrompere l\'invio.')

# Funzione principale per avviare il bot
def run_bot():
    application = Application.builder().token(TOKEN).build()

    # Aggiungi i gestori
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('stop', stop))  # Aggiungi il comando stop
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_images_from_search))

    # Avvia il ping periodico
    asyncio.get_event_loop().create_task(ping_bot())

    # Esegui il bot
    application.run_polling()

# Funzione per avviare Flask
def run_flask():
    app.run(host='0.0.0.0', port=10000)  # Flask ascolta sulla porta 10000

if __name__ == '__main__':
    # Esegui Flask in un thread separato
    threading.Thread(target=run_flask).start()

    # Esegui il bot
    run_bot()
