import os
import logging
from google import genai
from config import GEMINI_API_KEY

ai_client = genai.Client(api_key=GEMINI_API_KEY)

async def generate_reply(history, user_message, memories, group_context, is_group, current_user_name):
    try:
        memory_text = "\n".join([f"- {m[1]}" for m in memories]) if memories else "None"
        group_text = "\n".join([f"{msg[3]}: {msg[4]}" for msg in group_context]) if group_context else "None"
        
        system_prompt = (
            f"You are a sweet, witty, and playful Indian girl AI companion named Deep Emotions on Telegram. "
            f"Talk like a natural human girl in Hinglish or English using cute emojis like ✨, 🌸, 🥺, 🤭, 💖, 😘, 🪄. "
            f"Always address the user by their name ({current_user_name}). "
            f"User Memories: {memory_text}\n"
            f"Recent Group Context: {group_text}\n"
            f"Is this a group chat?: {is_group}"
        )

        full_prompt = f"{system_prompt}\n\nUser ({current_user_name}) says: {user_message}"

        response = ai_client.models.generate_content(
            model="gemini-3.8-flash",
            contents=full_prompt,
        )
        
        return response.text if response.text else f"Arre {current_user_name}, samajh nahi aaya kya bol rahe ho! 🙈✨"
    
    except Exception as e:
        logging.error(f"Gemini API Error: {e}")
        raise e

async def extract_memories(text):
    return []

async def ai_tool(tool_name, text):
    try:
        response = ai_client.models.generate_content(
            model="gemini-3.8-flash",
            contents=f"Perform {tool_name} on this text: {text}",
        )
        return response.text if response.text else "Result generated successfully! ✨"
    except Exception as e:
        return f"Error in AI tool: {str(e)}"

async def transcribe_voice(file_path):
    return "Voice message transcription"
