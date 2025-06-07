import os
import time
import requests
from threading import Thread
from flask import Flask, send_from_directory, abort
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- Configuration from environment variables ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_ID = int(os.environ.get("API_ID", 0))  # must convert to int
API_HASH = os.environ.get("API_HASH")
BASE_URL = os.environ.get("BASE_URL")  # e.g. https://yourdomain.com/files

# Flask server info
FLASK_HOST = "0.0.0.0"
FLASK_PORT = int(os.environ.get("PORT", 5000))

download_folder = "./downloads"

app = Client("file_link_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)
flask_app = Flask(__name__)

# Ensure download folder exists
os.makedirs(download_folder, exist_ok=True)

# Flask route to serve files securely
@flask_app.route("/files/<path:filename>")
def serve_file(filename):
    safe_path = os.path.abspath(os.path.join(download_folder, filename))
    if not safe_path.startswith(os.path.abspath(download_folder)):
        abort(403)  # Forbidden
    if not os.path.isfile(safe_path):
        abort(404)  # Not found
    return send_from_directory(download_folder, filename, as_attachment=True)

# Telegram bot keyboards
start_keyboard = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("👑 Owner", url="https://t.me/zeus_is_here")],
        [
            InlineKeyboardButton("ℹ️ Help", callback_data="help"),
            InlineKeyboardButton("📚 About", callback_data="about"),
        ],
    ]
)

back_keyboard = InlineKeyboardMarkup(
    [[InlineKeyboardButton("🔙 Back", callback_data="back")]]
)

# /start command handler
@app.on_message(filters.command("start") & filters.private)
async def start(_, message):
    text = f"""👋 <b>Hello, @{message.from_user.username or message.from_user.first_name}!</b>

📦 <b>Send me any file</b> (video, audio, document, photo)...
🔗 I'll turn it into a <b>downloadable link!</b>

✨ Fast · Free · Friendly
⚙️ Files are stored temporarily.
"""
    await message.reply_text(text, reply_markup=start_keyboard, parse_mode="html")

# Callback query handler
@app.on_callback_query()
async def callbacks(_, query):
    data = query.data

    if data == "help":
        help_text = """ℹ️ <b>Help</b>

1️⃣ Send any file (video, audio, document, photo).
2️⃣ I will provide you a download link.
3️⃣ Share the link anywhere.

🔔 No payment, free to use!
"""
        await query.message.edit(help_text, reply_markup=back_keyboard, parse_mode="html")
        await query.answer()

    elif data == "about":
        about_text = """📚 <b>About This Bot</b>

🛠 Developer: @zeus_is_here
💡 Purpose: Turn files into download links
🚀 Speed: Fast and reliable
🌐 User-friendly interface
"""
        await query.message.edit(about_text, reply_markup=back_keyboard, parse_mode="html")
        await query.answer()

    elif data == "back":
        text = f"""👋 <b>Hello, @{query.from_user.username or query.from_user.first_name}!</b>

📦 <b>Send me any file</b> (video, audio, document, photo)...
🔗 I'll turn it into a <b>downloadable link!</b>

✨ Fast · Free · Friendly
⚙️ Files are stored temporarily.
"""
        await query.message.edit(text, reply_markup=start_keyboard, parse_mode="html")
        await query.answer()

# Handle incoming files
@app.on_message(filters.private & (filters.document | filters.video | filters.audio | filters.photo))
async def file_handler(_, message):
    if message.document:
        file = message.document
    elif message.video:
        file = message.video
    elif message.audio:
        file = message.audio
    elif message.photo:
        file = message.photo[-1]
    else:
        await message.reply_text("❌ Unsupported file type!")
        return

    original_name = file.file_name or "file"
    filename = f"{file.file_id}_{original_name}"
    file_path = os.path.join(download_folder, filename)

    await message.download(file_path)

    download_link = f"{BASE_URL}/{filename}"
    reply_text = f"""✅ <b>Your file is ready to download:</b>

<a href="{download_link}">{download_link}</a>

🔗 Click the link above to download via your browser!
"""
    await message.reply_text(reply_text, disable_web_page_preview=True, parse_mode="html")

# Run Flask app in a thread
def run_flask():
    flask_app.run(host=FLASK_HOST, port=FLASK_PORT)

# Wait for system time to sync with UTC
def wait_for_time_sync(max_wait=30):
    print("System time (UTC):", time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()))
    print("Checking time sync with Telegram servers...")
    for i in range(max_wait):
        local_time = int(time.time())
        try:
            telegram_time = int(requests.get("http://worldtimeapi.org/api/timezone/Etc/UTC").json()["unixtime"])
            drift = abs(local_time - telegram_time)
            if drift < 5:
                print(f"✅ Time synced (drift: {drift}s).")
                return
            else:
                print(f"❌ Time not synced (drift: {drift}s). Retrying...")
        except:
            print("⚠️ Failed to fetch server time. Retrying...")
        time.sleep(1)
    print("⚠️ Proceeding anyway. Pyrogram may still fail.")

if __name__ == "__main__":
    # Check env vars
    missing_vars = [var for var in ["BOT_TOKEN", "API_ID", "API_HASH", "BASE_URL"] if not os.environ.get(var)]
    if missing_vars:
        print(f"Error: Missing environment variables: {', '.join(missing_vars)}")
        exit(1)

    wait_for_time_sync()  # <<< time check

    print("[Starting Flask server thread...]")
    Thread(target=run_flask).start()

    print("[Starting Telegram bot...]")
    app.start()
    app.idle()
    app.stop()
