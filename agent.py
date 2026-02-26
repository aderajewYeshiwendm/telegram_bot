import os
from dotenv import load_dotenv
import pickle
from google import genai
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
load_dotenv()

# =========================
# CONFIG
# =========================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_USER_ID = int(os.getenv("TELEGRAM_USER_ID"))



SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# =========================
# FILE TOOLS
# =========================

def list_files(path):
    """List files in the given directory (non-recursive, limited to 50 files)."""
    if not os.path.exists(path):
        return f"Path does not exist: {path}"
    
    if not os.path.isdir(path):
        return f"Not a directory: {path}"

    files = os.listdir(path)
    if not files:
        return "No files found."

    MAX_FILES = 50
    out = []
    for i, f in enumerate(files):
        if i >= MAX_FILES:
            out.append(f"...and more ({len(files)-MAX_FILES} files hidden)")
            break
        out.append(f)
    
    return "\n".join(out)

def search_files(keyword, path):
    """Search for files containing 'keyword' in any folder recursively."""
    if not os.path.exists(path):
        return f"Path does not exist: {path}"

    matches = []
    MAX_MATCHES = 50

    for root, dirs, files in os.walk(path):
        for file in files:
            if keyword in file:
                matches.append(os.path.join(root, file))
                if len(matches) >= MAX_MATCHES:
                    matches.append(f"...and more matches hidden")
                    return "\n".join(matches)
    
    return "\n".join(matches) if matches else "No matching files."

def organize_photos():
    os.system("mkdir -p Photos/Sorted")
    os.system("mv Photos/*.jpg Photos/Sorted/ 2>/dev/null")
    return "Photos organized."

# =========================
# GMAIL TOOL
# =========================
def get_gmail_service():
    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)

def summarize_emails():
    service = get_gmail_service()
    results = service.users().messages().list(
        userId='me', maxResults=5).execute()
    messages = results.get('messages', [])

    summaries = []
    for msg in messages:
        message = service.users().messages().get(
            userId='me', id=msg['id']).execute()
        snippet = message.get('snippet')
        summaries.append(snippet)

    return "\n\n".join(summaries) if summaries else "No recent emails."

# =========================
# GEMINI CHAT
# =========================
client = genai.Client(api_key=GEMINI_API_KEY)

def ask_gemini(prompt):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return response.text

# =========================
# TELEGRAM HANDLER
# =========================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("Unauthorized.")
        return

    text = update.message.text

    if text.startswith("list files"):
        parts = text.split(maxsplit=2)  # e.g., "list files /home/aderajew/dev"
        path = parts[2] if len(parts) > 2 else "."  # default to current dir
        reply = list_files(path)

    # -------- SEARCH FILES --------
    elif text.startswith("search file"):
        # e.g., "search file agent /home/aderajew/dev"
        parts = text.split(maxsplit=3)
        if len(parts) < 2:
            reply = "Please provide a keyword to search."
        else:
            keyword = parts[2]
            path = parts[3] if len(parts) > 3 else "."
            reply = search_files(keyword, path)

    

    elif "organize photos" in text:
        reply = organize_photos()
    elif "summarize emails" in text:
        try:
            reply = summarize_emails()
        except Exception as e:
            reply = "Gmail integration is currently disabled due to OAuth issue."

    else:
        reply = ask_gemini(text)

    MAX_LENGTH = 4000

    if len(reply) > MAX_LENGTH:
        for i in range(0, len(reply), MAX_LENGTH):
            await update.message.reply_text(reply[i:i+MAX_LENGTH])
    else:
        await update.message.reply_text(reply)

# =========================
# RUN
# =========================
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Gemini Agent running...")
app.run_polling()