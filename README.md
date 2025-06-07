# Telegram File-to-Link Bot

A Telegram bot that converts files sent by users into downloadable browser links using Pyrogram and Flask.  
Files are served via a Flask web server, enabling easy sharing and downloading through your own hosted URL.

---

## Features

- Accepts files (documents, videos, audio, photos) in Telegram private chat
- Generates a direct downloadable link for the file
- Links are served from your own deployed Flask server
- Simple UI with `/start`, Help and About buttons

---

## Demo

*Send any file to the bot, get a download link that works in any browser.*

---

## Prerequisites

- Telegram Bot Token from [@BotFather](https://t.me/BotFather)
- Telegram API ID and Hash from [my.telegram.org](https://my.telegram.org/apps)
- A server or platform to deploy the bot (we recommend [Render.com](https://render.com))
- Python 3.9+

---

## Setup and Deployment

### 1. Clone or Download the repository

```bash
git clone https://github.com/yourusername/telegram-file-link-bot.git
cd telegram-file-link-bot
