import html
import re
import time
import random
from pathlib import Path
from collections import defaultdict, deque

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ChatPermissions,
    MessageEntity,
)

from telegram.constants import ChatAction
from telegram.ext import ContextTypes, ApplicationHandlerStop

from config import (
    OWNER_ID, SUPPORT_CHAT_URL, SUPPORT_CHANNEL_URL, UPDATES_CHANNEL_URL,
    START_IMAGE_URL, OUR_BOTS_URL, OWNER_USERNAME,
)

from bot.social_engine import (
    should_reply_group,
    mark_group_reply,
    social_game,
)

from bot.ai import (
    generate_reply,
    extract_memories,
    ai_tool,
    transcribe_voice,
)

from bot.database import (
    add_message,
    get_history,
    clear_history,
    count_messages,
    add_memory,
    get_memories,
    delete_memory,
    clear_memories,
    count_memories,
    add_group_message,
    get_group_context,
    clear_group_context,
    count_group_messages,
)

# Rate Limiter & State
user_requests = defaultdict(deque)
WINDOW_SECONDS = 20
MAX_REQUESTS = 5
pending_ai_tools = {}

def allowed(user_id):
    now = time.monotonic()
    q = user_requests[user_id]
    while q and now - q[0] > WINDOW_SECONDS:
        q.popleft()
    if len(q) >= MAX_REQUESTS:
        return False
    q.append(now)
    return True

WELCOME_IMAGE_URL = START_IMAGE_URL or "https://raw.githubusercontent.com/AashishTechs/Deep-Emotion/main/Welcome.jpg?v=2"

def _btn(text, *, callback_data=None, url=None, style=None):
    kwargs = {}
    if style:
        kwargs["style"] = style
    return InlineKeyboardButton(text=text, callback_data=callback_data, url=url, **kwargs)

def _welcome_caption(bot_name):
    safe_name = html.escape(bot_name or "Deep Emotions")
    return (
        f"✨ Hii everyone, I'm <b>{safe_name}</b> 💖🌸\n\n"
        "Your friendly AI companion for chat, memory, games and everyday help. 🌸\n\n"
        "Choose an option below and let's get started. 👇"
    )

def main_menu_keyboard(bot_username="deepemotions01", is_owner=False):
    username = (bot_username or "deepemotions01").lstrip("@")
    rows = [
        [_btn("💬 ᴄʜᴀᴛ ᴡɪᴛʜ ᴍᴇ", callback_data="chat", style="danger")],
        [_btn("💗 ʜᴇʟᴘ & ᴄᴏᴍᴍᴀɴᴅs", callback_data="help_main", style="danger")],
    ]
    links = []
    if UPDATES_CHANNEL_URL:
        links.append(_btn("🔔 ᴜᴘᴅᴀᴛᴇs", url=UPDATES_CHANNEL_URL, style="success"))
    if SUPPORT_CHANNEL_URL:
        links.append(_btn("📢 ꜱᴜᴘᴘᴏʀᴛ ᴄʜᴀɴɴᴇʟ", url=SUPPORT_CHANNEL_URL, style="success"))
    if links:
        rows.append(links)
    if SUPPORT_CHAT_URL:
        rows.append([_btn("🛠️ ꜱᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ", url=SUPPORT_CHAT_URL, style="success")])
    if OUR_BOTS_URL:
        rows.append([_btn("🤖 ᴏᴜʀ ʙᴏᴛs", url=OUR_BOTS_URL, style="primary")])
    
    owner_username = (OWNER_USERNAME or "").strip().lstrip("@")
    if owner_username:
        rows.append([_btn("👑 ᴏᴡɴᴇʀ", url=f"https://t.me/{owner_username}", style="primary")])
    
    rows.append([_btn("➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ", url=f"https://t.me/{username}?startgroup=true", style="primary")])
    
    if is_owner:
        rows.append([_btn("👑 ᴏᴡɴᴇʀ ᴘᴀɴᴇʟ", callback_data="owner_panel", style="danger")])
    return InlineKeyboardMarkup(rows)

def help_menu_keyboard():
    return InlineKeyboardMarkup(
        [
            [_btn("💬 ᴄʜᴀᴛ", callback_data="help_chat", style="danger"), _btn("🧠 ᴍᴇᴍᴏʀʏ", callback_data="help_memory", style="danger")],
            [_btn("🎮 ɢᴀᴍᴇs", callback_data="help_games", style="success"), _btn("📊 ꜱᴛᴀᴛs", callback_data="help_stats", style="success")],
            [_btn("🔙 ʙᴀᴄᴋ", callback_data="home", style="danger")],
        ]
    )

HELP_SECTION_TEXT = {
    "help_chat": "💬 **Chat With Me**\n\nGroup mein tag ya reply karke baat karo, ekdum pyari girl vibe ke sath! ✨",
    "help_memory": "🧠 **Memory**\n\n/memory — saved memories\n/forget ID — delete memory",
    "help_games": "🎮 **Games**\n\n/game truth | /game dare | /game wyr | /game joke",
    "help_stats": "📊 **Stats**\n\n/stats se messages aur memories dekho.",
}

# Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    me = await context.bot.get_me()
    user = update.effective_user
    is_owner = bool(user and OWNER_ID != 0 and user.id == OWNER_ID)
    await update.message.reply_photo(
        photo=WELCOME_IMAGE_URL,
        caption=_welcome_caption(me.first_name),
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(me.username, is_owner=is_owner),
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    await update.message.reply_text("💗 **Help & Commands**\n\nChoose a category below 👇", parse_mode="Markdown", reply_markup=help_menu_keyboard())

async def privacy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    await update.message.reply_text("🔒 **Privacy Info**\n\nPersonal memories are safe and secure.", parse_mode="Markdown")

async def game_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    game = (context.args[0] if context.args else "joke").lower()
    await update.message.reply_text(social_game(game))

async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    text = " ".join(context.args).strip()
    if not text:
        await update.message.reply_text("💬 Example: `/ask Python kya hai?`", parse_mode="Markdown")
        return
    await process_ai(update, text, context)

async def clear_memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    await clear_history(update.effective_chat.id, update.effective_user.id)
    await update.message.reply_text("🧹 Conversation history clear kar di gayi hai!")

async def memory_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    memories = await get_memories(update.effective_user.id, limit=10)
    if not memories:
        await update.message.reply_text("🧠 Meri memory mein kuch saved nahi hai.")
        return
    lines = ["🧠 **Tumhari Long-Term Memories**\n"]
    for mid, mem in memories:
        lines.append(f"**{mid}.** {mem}")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

async def forget_memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not context.args:
        await update.message.reply_text("Usage: `/forget <ID>`", parse_mode="Markdown")
        return
    try:
        mid = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Valid memory ID do.")
        return
    deleted = await delete_memory(update.effective_user.id, mid)
    await update.message.reply_text(f"🗑️ Memory #{mid} delete kar di." if deleted else "❌ Memory ID nahi mili.")

async def forget_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    await clear_memories(update.effective_user.id)
    await update.message.reply_text("🧹 Saari long-term memories delete kar di gayi hain.")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    uid = update.effective_user.id
    cid = update.effective_chat.id
    t_msg = await count_messages(cid, uid)
    t_mem = await count_memories(uid)
    await update.message.reply_text(f"📊 **Stats**\n\n💬 Messages: {t_msg}\n🧠 Memories: {t_mem}", parse_mode="Markdown")

# New Member Welcome Handler
async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.new_chat_members:
        return
    for member in update.message.new_chat_members:
        if member.id == context.bot.id:
            continue
        name = member.first_name or "Friend"
        welcome_messages = [
            f"✨ Arey dekho kon aaya! Welcome to the group, {name} ji! 🌸💖 Aaram se baitho aur maza lo!",
            f"Hii {name} ji! 👋 Welcome to our family. Yahan sab mast hain, aap bhi enjoy karo! ✨🌸"
        ]
        await update.message.reply_text(random.choice(welcome_messages))

async def goodbye_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

# Sticker Handler
async def handle_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.sticker:
        return
    user = update.effective_user
    responses = [
        f"Awww {user.first_name}, kitna cute sticker hai! 🥺💖",
        f"Uff {user.first_name}! Aise stickers kahan se laate ho? 🤭✨"
    ]
    await update.message.reply_text(random.choice(responses))

# Chat Message Handler
async def chat_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    text = update.message.text.strip()
    chat = update.effective_chat
    user = update.effective_user
    if not chat or not user:
        return

    if chat.type != "private":
        await add_group_message(chat.id, user.id, f"@{user.username}" if user.username else None, user.full_name or "Unknown", text)

    me = await context.bot.get_me()
    bot_username = (me.username or "").lower()
    is_private = chat.type == "private"
    
    mentioned = f"@{bot_username}" in text.lower() if bot_username else False
    replied_to_bot = (
        update.message.reply_to_message is not None
        and update.message.reply_to_message.from_user is not None
        and update.message.reply_to_message.from_user.id == me.id
    )

    if not is_private and not mentioned and not replied_to_bot:
        return

    if mentioned and bot_username:
        text = re.sub(rf"@{re.escape(bot_username)}", "", text, flags=re.IGNORECASE).strip()

    await process_ai(update, text or "Hi", context)

async def process_ai(update, text, context):
    user = update.effective_user
    chat = update.effective_chat
    if not user or not update.message:
        return

    if not allowed(user.id) and user.id != OWNER_ID:
        await update.message.reply_text("⏳ Thoda slow... bahut requests aa gayi 😅")
        return

    is_group = chat.type in ("group", "supergroup")
    history = await get_history(chat.id, user.id)
    memories = [] if is_group else await get_memories(user.id, limit=10)
    group_context = await get_group_context(chat.id, limit=15) if is_group else []

    try:
        await update.message.chat.send_action(ChatAction.TYPING)
        reply = await generate_reply(history, text, memories, group_context, is_group, user.first_name)
        
        await add_message(chat.id, user.id, "user", text)
        await add_message(chat.id, user.id, "model", reply)
        
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text(f"Arre yaar {user.first_name}, thoda network issue ho gaya hai! 🥺💔")

# Button Handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query or not query.message:
        return
    await query.answer()
    if query.data == "home":
        me = await context.bot.get_me()
        try:
            await query.message.delete()
        except Exception:
            pass
        await context.bot.send_photo(
            chat_id=query.message.chat.id,
            photo=WELCOME_IMAGE_URL,
            caption=_welcome_caption(me.first_name),
            parse_mode="HTML",
            reply_markup=main_menu_keyboard(me.username),
        )

async def voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass
