import asyncio
import os
from telethon import TelegramClient, events
from telethon.tl.types import MessageEntityTextUrl

# API credentials from .env
API_ID = int(os.getenv("API_ID"))  # Convert to integer
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
DESTINATION_GROUP_ID = int(os.getenv("DESTINATION_GROUP_ID"))
SOURCE_CHANNEL_ID = int(os.getenv("SOURCE_CHANNEL_ID"))

# Initialize a client
client = TelegramClient('user', API_ID, API_HASH)

# Initialize the bot client
bot_client = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@client.on(events.NewMessage(chats=SOURCE_CHANNEL_ID))  # Source group or channel ID
async def handler(event):
    try:
        media = event.message.media
        message_text = event.message.message or ""
        entities = event.message.entities

        print('*************************************')
        print(f"Received message: {message_text}")
        print(f"Media: {media}")
        print('*************************************')

        # Prepare formatted message
        formatted_message = message_text

        # Extract hyperlinks from entities
        if entities:
            for entity in entities:
                if isinstance(entity, MessageEntityTextUrl):
                    # Get the URL and inner text
                    url = entity.url
                    inner_text = message_text[entity.offset: entity.offset + entity.length]
                    # Replace the inner text in the formatted message
                    formatted_message = formatted_message.replace(inner_text, f'<a href="{url}">{inner_text}</a>', 1)

        # Send media or text as a new message
        if media:
            print("Sending media to group...")
            try:
                # Download and send media
                file_path = await client.download_media(media)
                await bot_client.send_file(
                    DESTINATION_GROUP_ID,
                    file_path,
                    caption=formatted_message,
                    parse_mode='html'  # Use HTML parsing to allow clickable links
                )
                print(f"Sent media to group from {file_path}.")
            except Exception as e:
                print(f"Error downloading or sending media: {e}")
            finally:
                # Clean up the downloaded file
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Deleted temporary file: {file_path}")
        else:
            print("Sending text to group...")
            await bot_client.send_message(
                DESTINATION_GROUP_ID,
                formatted_message,
                parse_mode='html'  # Use HTML parsing to allow clickable links
            )
            print(f"Sent message to group: {formatted_message}")

    except Exception as e:
        print(f"Error sending message: {e}")

async def main():
    print("Monitoring source channel for new messages...")
    await client.run_until_disconnected()

# Start the client
with client:
    client.loop.run_until_complete(main())
