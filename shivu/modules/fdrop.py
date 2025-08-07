import random
from telegram.constants import ParseMode

async def fdrop(update: Update, context: CallbackContext) -> None:
    if str(update.effective_user.id) not in sudo_users:
        await update.message.reply_text("You're not allowed to use this command.")
        return

    try:
        characters = await collection.aggregate([{"$sample": {"size": 1}}]).to_list(length=1)
        if not characters:
            await update.message.reply_text("No characters in the database.")
            return

        character = characters[0]
        await update.message.reply_photo(
            photo=character["img_url"],
            caption=f"<b>Character Name:</b> {character['name']}\n"
                    f"<b>Anime Name:</b> {character['anime']}\n"
                    f"<b>Rarity:</b> {character['rarity']}\n"
                    f"<b>ID:</b> {character['id']}",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        await update.message.reply_text(f"Error while dropping: {e}")

FDROP_HANDLER = CommandHandler('fdrop', fdrop, block=False)
application.add_handler(FDROP_HANDLER)