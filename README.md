# Gemini Telegram Bot

A Telegram bot powered by Google Gemini and Gmail integration.  
Supports file listing/search, photo organization, and email summarization and chatting.

## Features

- **Gemini Chat**: Ask questions, get AI responses.
- **File Tools**:  
    - `list files <path>`: List files in a directory.  
    - `search file <keyword> <path>`: Search for files by keyword recursively.
    - `organize photos`: Move `.jpg` files in `Photos/` to `Photos/Sorted/`.
- **Gmail Summarization**:  
    - `summarize emails`: Get snippets of your 5 most recent emails.

## Setup

1. **Clone the repo**  
     ```bash
     git clone <repo-url>
     cd telegram_bot
     ```

2. **Install dependencies**  
     ```bash
     pip install python-dotenv google-generativeai google-api-python-client google-auth-httplib2 google-auth-oauthlib python-telegram-bot
     ```

3. **Create `.env` file**  
     ```
     GEMINI_API_KEY=<your_gemini_api_key>
     TELEGRAM_BOT_TOKEN=<your_telegram_bot_token>
     TELEGRAM_USER_ID=<your_telegram_user_id>
     ```

4. **Google Gmail API setup**  
     - Enable Gmail API in Google Cloud Console.
     - Download `credentials.json` and place in project root.

## Usage

- Start the bot:
    ```bash
    python3 agent.py
    ```
- Send commands to your Telegram bot:
    - `list files /path/to/dir`
    - `search file <keyword> /path/to/dir`
    - `organize photos`
    - `summarize emails`
    - Or chat with Gemini!

## Notes

- Gmail summarization requires OAuth setup (`credentials.json`).
- Large replies are split automatically.

## License

MIT
