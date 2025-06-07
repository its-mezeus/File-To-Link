import time
print("System time (UTC):", time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()))

import os
from threading import Thread
from flask import Flask, send_from_directory, abort
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- Configuration ---
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
API_ID = YOUR_API_ID  # Replace with your actual API ID (integer)
API_HASH = "YOUR_API_HASH_HERE"

# Replace with your actual public URL (no trailing slash)
BASE_URL = "https://yourdomain.com/files"

# Flask server info
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000

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

    # Download the file
    await message.download(file_path)

    # Create the download link using BASE_URL
    download_link = f"{BASE_URL}/{filename}"

    reply_text = f"""✅ <b>Your file is ready to download:</b>

<a href="{download_link}">{download_link}</a>

🔗 Click the link above to download via your browser!
"""
    await message.reply_text(reply_text, disable_web_page_preview=True, parse_mode="html")

# Run Flask app in a thread
def run_flask():
    flask_app.run(host=FLASK_HOST, port=FLASK_PORT)

if __name__ == "__main__":
    print("Starting Flask server...")
    Thread(target=run_flask).start()
    print("Starting Telegram bot...")
    app.run()
