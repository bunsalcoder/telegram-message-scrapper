from telethon import TelegramClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API credential from my.telegram.org
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")  # telegram phone number

# create a client
client = TelegramClient('user', API_ID, API_HASH)

async def main():
    await client.start(PHONE_NUMBER)
    
    print("Client is running...")
    async for dialog in client.iter_dialogs():
        if dialog.is_group:
            print(f"Group: {dialog.title}, ID: {dialog.id}")
        elif dialog.is_channel:
            print(f"Channel: {dialog.title}, ID: {dialog.id}")

# start the client
with client:
    client.loop.run_until_complete(main())