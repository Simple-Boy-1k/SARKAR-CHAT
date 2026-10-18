import aiosqlite
import os

DB_PATH = "data/deep_emotions.db"

async def init_db():
    os.makedirs("data", exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        # Chat History Table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS history (
                chat_id INTEGER,
                user_id INTEGER,
                role TEXT,
                content TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Long-term Memories Table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                memory TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Group Context Table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS group_context (
                chat_id INTEGER,
                user_id INTEGER,
                username TEXT,
                display_name TEXT,
                content TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()

async def add_message(chat_id, user_id, role, content):
    await init_db()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO history (chat_id, user_id, role, content) VALUES (?, ?, ?, ?)",
            (chat_id, user_id, role, content)
        )
        await db.commit()

async def get_history(chat_id, user_id, limit=20):
    await init_db()
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT role, content FROM history WHERE chat_id = ? AND user_id = ? ORDER BY timestamp DESC LIMIT ?",
            (chat_id, user_id, limit)
        ) as cursor:
            rows = await cursor.fetchall()
            return [{"role": row[0], "parts": [row[1]]} for row in reversed(rows)]

async def clear_history(chat_id, user_id):
    await init_db()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM history WHERE chat_id = ? AND user_id = ?", (chat_id, user_id))
        await db.commit()

async def count_messages(chat_id, user_id):
    await init_db()
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM history WHERE chat_id = ? AND user_id = ?", (chat_id, user_id)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

# Memory Functions
async def add_memory(user_id, memory):
    await init_db()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO memories (user_id, memory) VALUES (?, ?)", (user_id, memory))
        await db.commit()
    return True

async def get_memories(user_id, limit=10):
    await init_db()
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT id, memory FROM memories WHERE user_id = ? ORDER BY id DESC LIMIT ?", (user_id, limit)) as cursor:
            return await cursor.fetchall()

async def delete_memory(user_id, memory_id):
    await init_db()
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("DELETE FROM memories WHERE user_id = ? AND id = ?", (user_id, memory_id))
        await db.commit()
        return cursor.rowcount > 0

async def clear_memories(user_id):
    await init_db()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM memories WHERE user_id = ?", (user_id,))
        await db.commit()

async def count_memories(user_id):
    await init_db()
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM memories WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

# Group Context Functions
async def add_group_message(chat_id, user_id, username, display_name, content):
    await init_db()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO group_context (chat_id, user_id, username, display_name, content) VALUES (?, ?, ?, ?, ?)",
            (chat_id, user_id, username, display_name, content)
        )
        await db.commit()

async def get_group_context(chat_id, limit=15):
    await init_db()
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT user_id, username, display_name, content FROM group_context WHERE chat_id = ? ORDER BY timestamp DESC LIMIT ?",
            (chat_id, limit)
        ) as cursor:
            rows = await cursor.fetchall()
            return list(reversed(rows))

async def clear_group_context(chat_id):
    await init_db()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM group_context WHERE chat_id = ?", (chat_id,))
        await db.commit()

async def count_group_messages(chat_id):
    await init_db()
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM group_context WHERE chat_id = ?", (chat_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0
