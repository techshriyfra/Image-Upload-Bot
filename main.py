import os
import re
import time
import logging
import logging.config
from flask import Flask
from telegraph import upload_file, Telegraph
from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config
from utils import progress

try:
    import uvloop
    uvloop.install()
except ImportError:
    pass

logging.config.fileConfig("logging.conf")
logging.getLogger().setLevel(logging.ERROR)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

app = Flask(__name__)
telegraph = Telegraph()
telegraph.create_account(short_name="bot")

bot = Client(
    "telegraph",
    bot_token=Config.BOT_TOKEN,
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
)

@app.route("/")
def home():
    return "Telegram Telegraph Uploader Bot is Running!"

@bot.on_message(filters.command("start") & filters.incoming & filters.private)
async def start_handlers(_: Client, message: Message):
    await message.reply("Hello! Send me a photo or text to upload to Telegraph.")

@bot.on_message(filters.photo & filters.incoming & filters.private)
async def photo_handler(_: Client, message: Message):
    try:
        msg = await message.reply_text("Processing...", quote=True)
        file = await message.download()
        media_upload = upload_file(file)
        telegraph_link = f"https://telegra.ph{media_upload[0]}"
        await msg.edit(telegraph_link)
        os.remove(file)
    except Exception as e:
        logger.error(e)
        await msg.edit(f"Error: {e}")

@bot.on_message(filters.text & filters.incoming & filters.private)
async def text_handler(_: Client, message: Message):
    try:
        msg = await message.reply_text("Processing...", quote=True)
        title = message.text.split("\n")[0]
        content = message.text.replace("\n", "<br>")
        response = telegraph.create_page(title, html_content=content)
        await msg.edit(f"https://telegra.ph/{response['path']}")
    except Exception as e:
        logger.error(e)
        await msg.edit(f"Error: {e}")

if __name__ == "__main__":
    bot.start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
