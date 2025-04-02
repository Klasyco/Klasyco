Updated Code: Multiplayer Tactical Shooter Game

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# Global variables to manage the game
players = {}
roles = {
    "Sniper": {"ammo": 5, "damage": 50},
    "Assaulter": {"ammo": 10, "damage": 25},
    "Medic": {"ammo": 2, "damage": 10, "heal": 30},
}

# Command to start the bot
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Welcome to the Tactical Shooter Game Bot!\n"
        "Use /join to join the game and /help for commands."
    )

# Command to join the game
def join(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    user_name = update.effective_user.username or update.effective_user.first_name

    if user_id in players:
        update.message.reply_text("You're already in the game!")
    else:
        players[user_id] = {"name": user_name, "role": None, "ammo": 0, "health": 100}
        update.message.reply_text(
            f"{user_name} joined the game! Use /choose_role to select your role."
        )

# Command to choose a role
def choose_role(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Sniper", callback_data="role_Sniper")],
        [InlineKeyboardButton("Assaulter", callback_data="role_Assaulter")],
        [InlineKeyboardButton("Medic", callback_data="role_Medic")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Choose your role:", reply_markup=reply_markup)

# Handle role selection
def handle_role_selection(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    user_id = query.from_user.id
    role_key = query.data.split("_")[1]

    if user_id in players:
        players[user_id]["role"] = role_key
        players[user_id]["ammo"] = roles[role_key]["ammo"]
        query.edit_message_text(
            text=f"You selected {role_key}! Ammo: {roles[role_key]['ammo']}, Damage: {roles[role_key]['damage']}."
        )
    else:
        query.edit_message_text(text="Please join the game first using /join.")

# Command to attack a player
def attack(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if user_id not in players:
        update.message.reply_text("You need to join the game first! Use /join.")
        return

    if len(context.args) == 0:
        update.message.reply_text("Please specify a target username. Example: /attack @username")
        return

    target_username = context.args[0].replace("@", "")  # Remove "@" if included
    attacker = players[user_id]

    # Find target by username
    target = next((p for p in players.values() if p["name"] == target_username), None)
    if not target:
        update.message.reply_text("Target not found. Ensure they have joined the game.")
        return

    if attacker["ammo"] <= 0:
        update.message.reply_text("You're out of ammo! Reload using /reload.")
        return

    # Calculate damage
    damage = roles[attacker["role"]]["damage"]
    target["health"] -= damage
    attacker["ammo"] -= 1

    # Send response messages
    update.message.reply_text(
        f"You attacked {target['name']} for {damage} damage. Their health is now {target['health']}."
    )
    if target["health"] <= 0:
        update.message.reply_text(f"{target['name']} has been eliminated!")
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"{target['name']}, you were attacked by {attacker['name']}! Your health is now {target['health']}.",
        )

# Command to reload
def reload(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id

    if user_id not in players:
        update.message.reply_text("You need to join the game first! Use /join.")
        return

    role = players[user_id]["role"]
    players[user_id]["ammo"] = roles[role]["ammo"]
    update.message.reply_text(f"You reloaded! Ammo: {players[user_id]['ammo']}.")

# Command to check stats
def stats(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id

    if user_id not in players:
        update.message.reply_text("You need to join the game first! Use /join.")
        return

    player = players[user_id]
    update.message.reply_text(
        f"Name: {player['name']}\nRole: {player['role']}\nHealth: {player['health']}\nAmmo: {player['ammo']}"
    )

# Command to list all players
def list_players(update: Update, context: CallbackContext) -> None:
    if not players:
        update.message.reply_text("No players have joined the game yet!")
        return

    player_list = "\n".join(
        [f"{p['name']} - Role: {p['role']}, Health: {p['health']}, Ammo: {p['ammo']}" for p in players.values()]
    )
    update.message.reply_text(f"Current players:\n{player_list}")

# Main function
def main():
    # Replace '7795367513:AAFz0yHQgL6d6NBl16_-91P7CQdJxhzmqgI' with your Telegram bot token
    updater = Updater("7795367513:AAFz0yHQgL6d6NBl16_-91P7CQdJxhzmqgI")
    dispatcher = updater.dispatcher

    # Register commands
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("join", join))
    dispatcher.add_handler(CommandHandler("choose_role", choose_role))
    dispatcher.add_handler(CommandHandler("attack", attack))
    dispatcher.add_handler(CommandHandler("reload", reload))
    dispatcher.add_handler(CommandHandler("stats", stats))
    dispatcher.add_handler(CommandHandler("list_players", list_players))
    dispatcher.add_handler(CallbackQueryHandler(handle_role_selection))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
