import os
import requests
import schedule
import time
from telegram import Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ALPHABOT_API_KEY = os.getenv('ALPHABOT_API_KEY')

def fetch_raffles():
    """Fetch the list of raffles to find available ones."""
    headers = {'Authorization': f'Bearer {ALPHABOT_API_KEY}'}
    response = requests.get('https://api.alphabot.app/v1/raffles', headers=headers)
    if response.ok:
        raffles = response.json().get('data', {}).get('raffles', [])
        return raffles
    else:
        print('Failed to fetch raffles.')
        return []

def enter_raffle(raffle_slug):
    """Enter a specific raffle by slug."""
    url = 'https://api.alphabot.app/v1/register'
    headers = {'Authorization': f'Bearer {ALPHABOT_API_KEY}', 'Content-Type': 'application/json'}
    data = {'slug': raffle_slug}
    
    response = requests.post(url, json=data, headers=headers)
    if response.ok:
        print(f'Successfully entered raffle: {raffle_slug}')
    else:
        print(f'Failed to enter raffle: {raffle_slug}')

def automatic_raffle_entry():
    """Automatically enter all available raffles."""
    raffles = fetch_raffles()
    for raffle in raffles:
        if raffle['status'] == 'active':
            enter_raffle(raffle['slug'])

def start(update, context: CallbackContext):
    update.message.reply_text('Bot is running and will automatically enter raffles every 2 hours.')

def run_bot():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))

    # Start the bot
    updater.start_polling()

    # Schedule automatic raffle entries
    schedule.every(2).hours.do(automatic_raffle_entry)

    while True:
        schedule.run_pending()
        time.sleep(1)

    # Keeps bot running
    updater.idle()

if __name__ == '__main__':
    run_bot()
