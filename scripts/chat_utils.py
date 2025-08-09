import datetime
import os
import json
import random

# ANSI color codes
COLOR_RESET = "\033[0m"
COLOR_RED = "\033[91m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_BLUE = "\033[94m"
COLOR_MAGENTA = "\033[95m"
COLOR_CYAN = "\033[96m"

def wrap_text(text, width):
    lines = []
    words = text.split(' ')
    current_line = ""
    for word in words:
        if len(current_line) + len(word) + 1 > width and current_line:
            lines.append(current_line.strip())
            current_line = word
        else:
            if current_line:
                current_line += " "
            current_line += word
    lines.append(current_line.strip())
    return lines

def display_chat():
    now = datetime.datetime.now()
    time_str = now.strftime("%H:%M")
    hour = now.hour # Get hour for time-based message

    # Determine time-based message
    if (hour >= 22) or (hour < 6):
        cat_msg_time = "Le chat dort... Bonne nuit !"
    elif hour < 9:
        cat_msg_time = "Pret pour la journee ?"
    elif hour < 12:
        cat_msg_time = "Belle matinee !"
    elif hour < 14:
        cat_msg_time = "Bon appetit !"
    elif hour < 18:
        cat_msg_time = "Bon apres-midi !"
    else:
        cat_msg_time = "Bonsoir !"

    # Check for International Cat Day (August 8th)
    if now.month == 8 and now.day == 8:
        try:
            with open(os.path.join(os.path.dirname(__file__), 'chat.json'), 'r') as f:
                anecdotes = json.load(f)
            anecdote = random.choice(anecdotes)
        except (FileNotFoundError, json.JSONDecodeError):
            anecdote = "Une anecdote sur les chats (fichier chat.json manquant ou invalide)."

        colors = [COLOR_RED, COLOR_GREEN, COLOR_YELLOW, COLOR_BLUE, COLOR_MAGENTA, COLOR_CYAN]
        random_color = random.choice(colors)

        cat_msg_line1 = "Aujourd'hui c'est le 8 aout, c'est ma fete !"
        cat_face = "( ^.^ )"

        wrapped_anecdote = wrap_text(anecdote, 68) # Wrap to 68 characters
        anecdote_line1 = wrapped_anecdote[0]
        anecdote_line2 = wrapped_anecdote[1] if len(wrapped_anecdote) > 1 else ""

        cat = f"""
{random_color}
     /\_/\    {cat_msg_line1}
    {cat_face}   {anecdote_line1}
     > ^ <    {anecdote_line2}
              ({time_str}) {cat_msg_time}
{COLOR_RESET}
"""
    else:
        cat_face = "( -.- )" # Default cat face for regular days
        if (hour >= 22) or (hour < 6):
            cat_face = "( -.- ) zZz"

        cat = f"""
     /\_/\    {cat_msg_time}
    {cat_face}   ({time_str})
     > ^ <
"""
    print(cat)
