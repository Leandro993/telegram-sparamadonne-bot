from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
import requests

TOKEN = '7114806273:AAHgtfAfV391U0LgrWFy554-RkVcUb57l18'
GOOGLE_API_KEY = 'AIzaSyDn5KBLfwN3U9Fp9i084plI_Hzb5G8_XCo'
GOOGLE_CX = '4766ab6c805714436'

async def fetch_image_urls(query: str):
    image_urls = []
    max_results = 50
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

async def send_images_from_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    chat_id = update.effective_chat.id
    print(f"Received search query: {query}")  # Debug

    image_urls = await fetch_image_urls(query)

    if not image_urls:
        await update.message.reply_text("Nessuna immagine trovata.")
        return

    print(f"Found {len(image_urls)} images for query '{query}'")  # Debug

    for url in image_urls:
        try:
            await context.bot.send_photo(chat_id=chat_id, photo=url)
            await asyncio.sleep(3)  # Optional pause to avoid overloading
        except Exception as e:
            print(f"Error sending image {url}: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Benvenuto! Invia una parola chiave per cercare immagini su Google.')

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_images_from_search))

    application.run_polling()

if __name__ == '__main__':
    main()