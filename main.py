import os
import logging
import asyncio
from flask import Flask
from telegraph import upload_file, Telegraph
from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask
app = Flask(__name__)

# Initialize Telegraph
telegraph = Telegraph()
telegraph_account = telegraph.create_account(short_name="bot")
logger.info("Telegraph account created!")

# Initialize Pyrogram Bot
bot = Client(
    "telegraph_bot",
    bot_token=Config.BOT_TOKEN,
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
)

@app.route("/")
def home():
    return "Telegram Telegraph Uploader Bot is Running!"

@bot.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    await message.reply("Hello! Send me a photo or text to upload to Telegraph.")

@bot.on_message(filters.photo & filters.private)
async def photo_handler(client: Client, message: Message):
    msg = await message.reply_text("Processing...", quote=True)
    try:
        file_path = await message.download()
        media_upload = upload_file(file_path)  # Upload to Telegraph
        telegraph_link = f"https://telegra.ph{media_upload[0]}"
        await msg.edit(f"Uploaded! [View Here]({telegraph_link})")
        os.remove(file_path)
    except Exception as e:
        logger.error(f"Error uploading image: {e}")
        await msg.edit(f"Error: {e}")

@bot.on_message(filters.text & filters.private)
async def text_handler(client: Client, message: Message):
    msg = await message.reply_text("Processing...", quote=True)
    try:
        title = message.text.split("\n")[0] or "Untitled"
        content = message.text.replace("\n", "<br>")
        response = telegraph.create_page(title, html_content=content)
        await msg.edit(f"Uploaded! [View Here](https://telegra.ph/{response['path']})")
    except Exception as e:
        logger.error(f"Error uploading text: {e}")
        await msg.edit(f"Error: {e}")

async def main():
    await bot.start()
    logger.info("Bot started!")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

if __name__ == "__main__":
    asyncio.run(main())  # Run bot and Flask server
