import os
import requests
import schedule
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
        return [raffle for raffle in raffles if raffle['status'] == 'active']
    else:
        print('Failed to fetch raffles.')
        return []

# Enter a raffle using its slug
async def enter_raffle(raffle_slug):
    url = 'https://api.alphabot.app/v1/register'
    headers = {'Authorization': f'Bearer {ALPHABOT_API_KEY}', 'Content-Type': 'application/json'}
    data = {'slug': raffle_slug}

    response = requests.post(url, json=data, headers=headers)
    if response.ok:
        print(f'Successfully entered raffle: {raffle_slug}')
    else:
        print(f'Failed to enter raffle: {raffle_slug}')

# Enter all active raffles automatically
async def automatic_raffle_entry():
    raffles = await fetch_raffles()
    for raffle in raffles:
        await enter_raffle(raffle['slug'])

# Schedule the raffle entry
def schedule_raffle_entries():
    asyncio.run(automatic_raffle_entry())

# Command to start the bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Bot is active and will enter raffles every 2 hours.')

# Main function to configure and run the bot
async def main():
    # Initialize the application
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add command for start
    application.add_handler(CommandHandler("start", start))
    
    # Schedule entry every 2 hours
    schedule.every(2).hours.do(schedule_raffle_entries)

    # Start the bot
    await application.initialize()
    await application.start()
    application.updater.start_polling()

    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

    await application.stop()

# Execute the main function
if __name__ == '__main__':
    asyncio.run(main())
