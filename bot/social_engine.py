import random

# Group social engine logic for managing smart interactions
_last_group_reply = {}

def should_reply_group(chat_id, text, mentioned=False, replied_to_bot=False, other_user_mentioned=False):
    # Always reply if mentioned or replied to bot
    if mentioned or replied_to_bot:
        return True
    
    # If directed to someone else, do not reply
    if other_user_mentioned:
        return False
        
    # By default in smart mode, allow natural chat or casual triggers
    return True

def mark_group_reply(chat_id):
    pass

def social_game(game_type):
    truths = [
        "What is your biggest secret that nobody knows? 🙈",
        "Who was your first crush in this group? ✨",
        "What is the most embarrassing thing you've ever done? 🤭",
        "If you could swap lives with someone in this group for a day, who would it be? 🌸"
    ]
    
    dares = [
        "Send a voice note singing your favorite song right now! 🎶",
        "Change your group nickname to 'Cute Don' for the next 1 hour! 😎",
        "Praise the group owner with a romantic poem right here! ❤️",
        "Send the last saved photo from your gallery! 📸"
    ]
    
    wyrs = [
        "Would you rather always be 10 minutes late or 20 minutes early? ⏰",
        "Would you rather be able to fly or read minds? 🪄",
        "Would you rather live without internet for a month or without your phone? 📱",
        "Would you rather speak all languages fluently or play all instruments like a pro? 🎶"
    ]
    
    jokes = [
        "Teacher: Why are you late? \nStudent: Sir, a sign down the road said 'School Ahead, Go Slow'! 😂",
        "Why don't skeletons fight each other? Because they don't have the guts! 💀✨",
        "Boss: 'You are late by 2 hours!' \nEmployee: 'Yes sir, but I worked extra hard yesterday!' \nBoss: 'How?' \nEmployee: 'I came 2 hours early!' 🤭",
        "Why did the math book look sad? Because it had too many problems! 📚😂"
    ]
    
    game_type = game_type.lower()
    if "truth" in game_type:
        return f"🔍 **Truth for you:**\n\n{random.choice(truths)}"
    elif "dare" in game_type:
        return f"🔥 **Dare for you:**\n\n{random.choice(dares)}"
    elif "wyr" in game_type or "would" in game_type:
        return f"⚖️ **Would You Rather:**\n\n{random.choice(wyrs)}"
    else:
        return f"😂 **Joke time:**\n\n{random.choice(jokes)}"
