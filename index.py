import os
import logging
import asyncio
from telethon import TelegramClient, events
from telethon.tl.types import MessageEntityTextUrl
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),  # Log to a file
        logging.StreamHandler()          # Log to the console
    ]
)
logger = logging.getLogger(__name__)

# API credentials from .env
API_ID = int(os.getenv("API_ID"))  # Convert to integer
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
SOURCE_CHANNEL_ID = int(os.getenv("SOURCE_CHANNEL_ID"))

def get_destination_group_ids():
    """
    Safely retrieves and parses DESTINATION_GROUP_IDS from the environment.
    Returns a list of integers or an empty list if no valid IDs are found.
    """
    destination_ids = os.getenv("DESTINATION_GROUP_IDS")
    if not destination_ids:
        logger.warning("DESTINATION_GROUP_IDS is not set in the .env file.")
        return []

    try:
        # Split the string by commas, strip whitespace, and convert to integers
        ids = [int(id.strip()) for id in destination_ids.split(",") if id.strip()]
        return ids
    except ValueError as e:
        logger.error(f"Invalid group ID in DESTINATION_GROUP_IDS. Details: {e}")
        return []

# Get destination group IDs
DESTINATION_GROUP_IDS = get_destination_group_ids()

# Check if any valid IDs were found
if not DESTINATION_GROUP_IDS:
    logger.error("No valid destination group IDs found. Exiting.")
    exit(1)

logger.info(f"Destination Group IDs: {DESTINATION_GROUP_IDS}")

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

async def send_with_retry(client, dest_id, message, media=None, retries=3, delay=5):
    """
    Sends a message with retry logic in case of failures.
    Removes the downloaded media file after sending or if sending fails.
    """
    file_path = None
    try:
        if media:
            file_path = await client.download_media(media)
            for attempt in range(retries):
                try:
                    await client.send_file(dest_id, file_path, caption=message, parse_mode='html')
                    break  # Success, exit the retry loop
                except Exception as e:
                    logger.error(f"Attempt {attempt + 1} failed for destination {dest_id}: {e}")
                    if attempt < retries - 1:
                        await asyncio.sleep(delay)
                    else:
                        logger.error(f"Failed to send message to {dest_id} after {retries} attempts.")
        else:
            await client.send_message(dest_id, message, parse_mode='html')
    except Exception as e:
        logger.error(f"Error sending message to {dest_id}: {e}")
    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Removed media file: {file_path}")

@client.on(events.NewMessage(chats=SOURCE_CHANNEL_ID))  # Source group or channel ID
async def handler(event):
    try:
        media = event.message.media
        message_text = event.message.message or ""
        entities = event.message.entities

        logger.info('*************************************')
        logger.info(f"Received message: {message_text}")
        logger.info(f"Media: {media}")
        logger.info('*************************************')

        # Reconstruct the message with proper hyperlinks
        formatted_message = apply_entities_to_message(message_text, entities)

        # Send media or text to each destination group
        for dest_id in DESTINATION_GROUP_IDS:
            await send_with_retry(bot_client, dest_id, formatted_message, media)

    except Exception as e:
        logger.error(f"Error handling message: {e}")

async def main():
    logger.info("Monitoring source channel for new messages...")
    await client.run_until_disconnected()

# Start the client
with client:
    client.loop.run_until_complete(main())
