import asyncio
import os
from telethon import TelegramClient, events
from telethon.tl.types import MessageEntityTextUrl
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

def apply_entities_to_message(text, entities):
    """
    Reconstructs the message with proper HTML tags for hyperlinks.
    Handles UTF-16 offsets correctly.
    """
    if not entities:
        return text

    # Convert the text to UTF-16 to handle offsets correctly
    utf16_text = text.encode('utf-16-le')
    result = []
    prev_end = 0

    # Sort entities by offset in reverse order to avoid overlapping issues
    sorted_entities = sorted(entities, key=lambda x: x.offset, reverse=True)

    for entity in sorted_entities:
        if isinstance(entity, MessageEntityTextUrl):
            # Calculate start and end positions in UTF-16
            start = entity.offset * 2  # Each UTF-16 character is 2 bytes
            end = start + entity.length * 2

            # Extract the inner text from UTF-16
            inner_text = utf16_text[start:end].decode('utf-16-le')

            # Add the text after the entity to the result
            result.append(utf16_text[end:].decode('utf-16-le'))

            # Add the hyperlink with the inner text
            result.append(f'<a href="{entity.url}">{inner_text}</a>')

            # Update the remaining text
            utf16_text = utf16_text[:start]

    # Add the remaining text before the first entity
    result.append(utf16_text.decode('utf-16-le'))

    # Reverse the result to restore the original order
    return ''.join(reversed(result))

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

        # Reconstruct the message with proper hyperlinks
        formatted_message = apply_entities_to_message(message_text, entities)

        # Send media or text as a new message
        if media:
            try:
                # Download and send media
                file_path = await client.download_media(media)
                await bot_client.send_file(
                    DESTINATION_GROUP_ID,
                    file_path,
                    caption=formatted_message,
                    parse_mode='html'  # Use HTML parsing to allow clickable links
                )
            except Exception as e:
                print(f"Error downloading or sending media: {e}")
            finally:
                # Clean up the downloaded file
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Deleted temporary file: {file_path}")
        else:
            await bot_client.send_message(
                DESTINATION_GROUP_ID,
                formatted_message,
                parse_mode='html'  # Use HTML parsing to allow clickable links
            )

    except Exception as e:
        print(f"Error sending message: {e}")

async def main():
    print("Monitoring source channel for new messages...")
    await client.run_until_disconnected()

# Start the client
with client:
    client.loop.run_until_complete(main())
