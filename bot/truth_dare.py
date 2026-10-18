import random

async def get_truth():
    truths = [
        "What is your biggest secret that nobody knows? 🙈",
        "Who was your first crush in this group? ✨",
        "What is the most embarrassing thing you've ever done? 🤭",
        "If you could swap lives with someone in this group for a day, who would it be? 🌸"
    ]
    return random.choice(truths)

async def get_dare():
    dares = [
        "Send a voice note singing your favorite song right now! 🎶",
        "Change your group nickname to 'Cute Don' for the next 1 hour! 😎",
        "Praise the group owner with a romantic poem right here! ❤️",
        "Send the last saved photo from your gallery! 📸"
    ]
    return random.choice(dares)
