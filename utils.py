import time
from pyrogram.types import Message

async def progress(current, total, message: Message, start):
    """Progress bar function for file downloads/uploads."""
    elapsed_time = time.time() - start
    percentage = current * 100 / total
    speed = current / elapsed_time if elapsed_time > 0 else 0
    await message.edit(
        f"⏳ Progress: {percentage:.2f}%\n"
        f"📦 Size: {current / 1024:.2f} KB / {total / 1024:.2f} KB\n"
        f"⚡ Speed: {speed / 1024:.2f} KB/s"
    )
