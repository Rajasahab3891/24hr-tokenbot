import asyncio
from datetime import datetime
from time import time

from pyrogram import Client as Bot, filters
from pyrogram.types import Message, InlineKeyboardMarkup
from pyrogram.errors import (
    FloodWait,
    UserIsBlocked,
    InputUserDeactivated
)

# Globals
ADMINS = [123456789]  # Replace with actual admin IDs
START_TIME = datetime.utcnow()
START_TIME_ISO = START_TIME.isoformat()

# Messages
WAIT_MSG = "<b>Processing ...</b>"
REPLY_ERROR = "<code>Use this command as a reply to any Telegram message without any spaces.</code>"

# Helper Functions
async def full_userbase():
    """Fetch the full user base."""
    # Replace with your actual implementation to retrieve user IDs
    return [11111111, 22222222]  # Example user IDs

async def del_user(user_id):
    """Remove user from the database."""
    # Replace with your actual implementation for user deletion
    print(f"Deleted user: {user_id}")

async def _human_time_duration(seconds):
    """Convert seconds to human-readable duration."""
    mins, secs = divmod(seconds, 60)
    hours, mins = divmod(mins, 60)
    days, hours = divmod(hours, 24)
    return f"{days}d {hours}h {mins}m {secs}s" if days else f"{hours}h {mins}m {secs}s"

# Handlers
@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    msg = await message.reply_text(WAIT_MSG)
    users = await full_userbase()
    await msg.edit(f"<b>{len(users)} users are using this bot</b>")

@Bot.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))
async def send_text(client: Bot, message: Message):
    if not message.reply_to_message:
        msg = await message.reply(REPLY_ERROR)
        await asyncio.sleep(8)
        return await msg.delete()

    query = await full_userbase()
    broadcast_msg = message.reply_to_message
    stats = {"total": 0, "successful": 0, "blocked": 0, "deleted": 0, "unsuccessful": 0}

    pls_wait = await message.reply("<i>Broadcasting Message... This will take some time</i>")
    
    for chat_id in query:
        try:
            await broadcast_msg.copy(chat_id)
            stats["successful"] += 1
        except FloodWait as e:
            await asyncio.sleep(e.x)
            await broadcast_msg.copy(chat_id)
            stats["successful"] += 1
        except UserIsBlocked:
            await del_user(chat_id)
            stats["blocked"] += 1
        except InputUserDeactivated:
            await del_user(chat_id)
            stats["deleted"] += 1
        except Exception as e:
            stats["unsuccessful"] += 1
            print(f"Error for {chat_id}: {e}")
        stats["total"] += 1

    status = (
        f"<b><u>Broadcast Completed</u></b>\n"
        f"Total Users: <code>{stats['total']}</code>\n"
        f"Successful: <code>{stats['successful']}</code>\n"
        f"Blocked Users: <code>{stats['blocked']}</code>\n"
        f"Deleted Accounts: <code>{stats['deleted']}</code>\n"
        f"Unsuccessful: <code>{stats['unsuccessful']}</code>"
    )
    await pls_wait.edit(status)

@Bot.on_message(filters.command("ping"))
async def ping_pong(client: Bot, message: Message):
    start = time()
    uptime_sec = (datetime.utcnow() - START_TIME).total_seconds()
    uptime = await _human_time_duration(int(uptime_sec))
    m_reply = await message.reply_text("Pinging...")
    delta_ping = time() - start
    await m_reply.edit_text(
        f"<b>PONG!! 🏓</b>\n"
        f"<b>• Pinger:</b> <code>{delta_ping * 1000:.3f}ms</code>\n"
        f"<b>• Uptime:</b> <code>{uptime}</code>"
    )

@Bot.on_message(filters.command("uptime"))
async def get_uptime(client: Bot, message: Message):
    uptime_sec = (datetime.utcnow() - START_TIME).total_seconds()
    uptime = await _human_time_duration(int(uptime_sec))
    await message.reply_text(
        "🤖 <b>Bot Status:</b>\n"
        f"• <b>Uptime:</b> <code>{uptime}</code>\n"
        f"• <b>Start Time:</b> <code>{START_TIME_ISO}</code>"
    )
