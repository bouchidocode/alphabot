import os
import requests
import schedule
import time
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ALPHABOT_API_KEY = os.getenv('ALPHABOT_API_KEY')

# Fetch raffles from Alphabot API
async def fetch_raffles():
    headers = {'Authorization': f'Bearer {ALPHABOT_API_KEY}'}
    response = requests.get('https://api.alphabot.app/v1/raffles', headers=headers)
    if response.ok:
        raffles = response.json().get('data', {}).get('raffles', [])
        return raffles
    else:
        print('Failed to fetch raffles.')
        return []

# Register for a raffle using its slug
async def enter_raffle(raffle_slug):
    url = 'https://api.alphabot.app/v1/register'
    headers = {'Authorization': f'Bearer {ALPHABOT_API_KEY}', 'Content-Type': 'application/json'}
    data = {'slug': raffle_slug}

    response = requests.post(url, json=data, headers=headers)
    if response.ok:
        print(f'Successfully entered raffle: {raffle_slug}')
    else:
        print(f'Failed to enter raffle: {raffle_slug}')

# Function to automatically enter all active raffles
async def automatic_raffle_entry():
    raffles = await fetch_raffles()
    for raffle in raffles:
        if raffle['status'] == 'active':
            await enter_raffle(raffle['slug'])

# Scheduled task runner for entering raffles
def run_scheduled_raffle_entry():
    asyncio.run(automatic_raffle_entry())

# Start command triggered by Telegram
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Bot is running and will automatically enter raffles every 2 hours.')

# Main function to initialize and run the bot
async def main():
    # Initialize the Application
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add a command handler for '/start'
    application.add_handler(CommandHandler("start", start))
    
    # Schedule raffle entry task every 2 hours
    schedule.every(2).hours.do(run_scheduled_raffle_entry)

    # Start the polling loop
    await application.initialize()  # Make sure initialization is explicitly called
    await application.start()
    await application.updater.start_polling()

    # Continuously check the schedule
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

    await application.stop()

# Execute the main function
if __name__ == '__main__':
    asyncio.run(main())
