# Telegram Message Scrapper

A Python-based Telegram bot that listens to messages from a source channel and forwards them (including media and formatted hyperlinks) to a destination group.

## 🚀 Features
- Listens for new messages in a specified Telegram channel
- Supports forwarding both text and media messages
- Preserves hyperlinks in messages using HTML formatting
- Automatically cleans up downloaded media files after sending

## 🛠️ Requirements
- Python 3.7+
- Telegram API credentials
- A bot token
- Environment variables set in a `.env` file

## 📦 Installation

1. Clone the repository:
   ```sh
   git clone git@github.com:bunsalcoder/telegram-message-scrapper.git
   cd telegram-message-scrapper
   ```

2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project directory and add your credentials:
   ```ini
   API_ID=your_api_id
   API_HASH=your_api_hash
   BOT_TOKEN=your_bot_token
   DESTINATION_GROUP_ID=-100xxxxxxxxxx  # Your target group ID
   SOURCE_CHANNEL_ID=-100xxxxxxxxxx  # Your source channel ID
   PHONE_NUMBER=+855xxxxxxx # Phone number with country code
   ```

## 🔧 Usage

Run the bot:
```sh
python3 index.py
```

## 📜 How It Works
1. Connects to Telegram using Telethon.
2. Monitors the specified `SOURCE_CHANNEL_ID` for new messages.
3. If the message contains media, it downloads and forwards it.
4. If the message has hyperlinks, it formats them properly using HTML.
5. Sends the message to `DESTINATION_GROUP_ID`.

## 🛑 Troubleshooting
- If `.env` variables are not loading, try running:
  ```sh
  export $(grep -v '^#' .env | xargs)
  ```
- Ensure your bot is an **admin** in both the source channel and destination group.
- Check that your API credentials are correct.

## 📜 License
This project is open-source and available under the APACHE-2.0 License.

