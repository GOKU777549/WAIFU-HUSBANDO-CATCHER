import urllib.request
from pymongo import ReturnDocument
import random
from telegram.constants import ParseMode

from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

from shivu import application, sudo_users, collection, db, CHARA_CHANNEL_ID, SUPPORT_CHAT

WRONG_FORMAT_TEXT = """Wrong ❌️ format...  eg. /upload Img_url muzan-kibutsuji Demon-slayer 3

img_url character-name anime-name rarity-number

use rarity number accordingly rarity Map

rarity_map = 1 (⚪️ Common), 2 (🟣 Rare) , 3 (🟡 Legendary), 4 (🟢 Medium)"""



async def get_next_sequence_number(sequence_name):
    sequence_collection = db.sequences
    sequence_document = await sequence_collection.find_one_and_update(
        {'_id': sequence_name}, 
        {'$inc': {'sequence_value': 1}}, 
        return_document=ReturnDocument.AFTER
    )
    if not sequence_document:
        await sequence_collection.insert_one({'_id': sequence_name, 'sequence_value': 0})
        return 0
    return sequence_document['sequence_value']

async def upload(update: Update, context: CallbackContext) -> None:
    if str(update.effective_user.id) not in sudo_users:
        await update.message.reply_text('Ask My Owner...')
        return

    try:
        args = context.args
        reply = update.message.reply_to_message

        # Photo reply ke sath command: /upload muzan-kibutsuji demon-slayer 3
        # URL ke sath command: /upload <image_url> muzan-kibutsuji demon-slayer 3

        if (reply and reply.photo and len(args) == 3):
            img_url = reply.photo[-1].file_id
            character_name = args[0].replace('-', ' ').title()
            anime = args[1].replace('-', ' ').title()
            rarity_input = args[2]
        elif (not reply and len(args) == 4):
            img_url = args[0]
            character_name = args[1].replace('-', ' ').title()
            anime = args[2].replace('-', ' ').title()
            rarity_input = args[3]
            try:
                urllib.request.urlopen(img_url)
            except:
                await update.message.reply_text('Invalid URL.')
                return
        else:
            await update.message.reply_text(WRONG_FORMAT_TEXT)
            return

        # Rarity map
        rarity_map = {
            1: "⚪ Common",
            2: "🟣 Rare",
            3: "🟡 Legendary",
            4: "🟢 Medium"
        }

        try:
            rarity = rarity_map[int(rarity_input)]
        except KeyError:
            await update.message.reply_text('Invalid rarity. Please use 1, 2, 3, or 4.')
            return

        # ID generate
        id = str(await get_next_sequence_number('character_id')).zfill(2)

        character = {
            'img_url': img_url,
            'name': character_name,
            'anime': anime,
            'rarity': rarity,
            'id': id
        }

        # Send to channel
        try:
            message = await context.bot.send_photo(
                chat_id=CHARA_CHANNEL_ID,
                photo=img_url,
                caption=(
                    f'<b>Character Name:</b> {character_name}\n'
                    f'<b>Anime Name:</b> {anime}\n'
                    f'<b>Rarity:</b> {rarity}\n'
                    f'<b>ID:</b> {id}\n'
                    f'Added by <a href="tg://user?id={update.effective_user.id}">'
                    f'{update.effective_user.first_name}</a>'
                ),
                parse_mode='HTML'
            )
            character['message_id'] = message.message_id
            await collection.insert_one(character)
            await update.message.reply_text('✅ CHARACTER ADDED SUCCESSFULLY')
        except Exception as e:
            await collection.insert_one(character)
            await update.message.reply_text(
                f"Character Added to DB but couldn't send to channel.\nError: {e}"
            )

    except Exception as e:
        await update.message.reply_text(
            f'Character Upload Unsuccessful. Error: {str(e)}\nIf you think this is a source error, contact: {SUPPORT_CHAT}'
        )

async def delete(update: Update, context: CallbackContext) -> None:
    if str(update.effective_user.id) not in sudo_users:
        await update.message.reply_text('Ask my Owner to use this Command...')
        return

    try:
        args = context.args
        if len(args) != 1:
            await update.message.reply_text('Incorrect format... Please use: /delete ID')
            return

        
        character = await collection.find_one_and_delete({'id': args[0]})

        if character:
            
            await context.bot.delete_message(chat_id=CHARA_CHANNEL_ID, message_id=character['message_id'])
            await update.message.reply_text('DONE')
        else:
            await update.message.reply_text('Deleted Successfully from db, but character not found In Channel')
    except Exception as e:
        await update.message.reply_text(f'{str(e)}')

async def update(update: Update, context: CallbackContext) -> None:
    if str(update.effective_user.id) not in sudo_users:
        await update.message.reply_text('You do not have permission to use this command.')
        return

    try:
        args = context.args
        if len(args) != 3:
            await update.message.reply_text('Incorrect format. Please use: /update id field new_value')
            return

        # Get character by ID
        character = await collection.find_one({'id': args[0]})
        if not character:
            await update.message.reply_text('Character not found.')
            return

        # Check if field is valid
        valid_fields = ['img_url', 'name', 'anime', 'rarity']
        if args[1] not in valid_fields:
            await update.message.reply_text(f'Invalid field. Please use one of the following: {", ".join(valid_fields)}')
            return

        # Update field
        if args[1] in ['name', 'anime']:
            new_value = args[2].replace('-', ' ').title()
        elif args[1] == 'rarity':
            rarity_map = {1: "⚪ Common", 2: "🟣 Rare", 3: "🟡 Legendary", 4: "🟢 Medium", 5: "💮 Special edition"}
            try:
                new_value = rarity_map[int(args[2])]
            except KeyError:
                await update.message.reply_text('Invalid rarity. Please use 1, 2, 3, 4, or 5.')
                return
        else:
            new_value = args[2]

        await collection.find_one_and_update({'id': args[0]}, {'$set': {args[1]: new_value}})

        
        if args[1] == 'img_url':
            await context.bot.delete_message(chat_id=CHARA_CHANNEL_ID, message_id=character['message_id'])
            message = await context.bot.send_photo(
                chat_id=CHARA_CHANNEL_ID,
                photo=new_value,
                caption=f'<b>Character Name:</b> {character["name"]}\n<b>Anime Name:</b> {character["anime"]}\n<b>Rarity:</b> {character["rarity"]}\n<b>ID:</b> {character["id"]}\nUpdated by <a href="tg://user?id={update.effective_user.id}">{update.effective_user.first_name}</a>',
                parse_mode='HTML'
            )
            character['message_id'] = message.message_id
            await collection.find_one_and_update({'id': args[0]}, {'$set': {'message_id': message.message_id}})
        else:
            
            await context.bot.edit_message_caption(
                chat_id=CHARA_CHANNEL_ID,
                message_id=character['message_id'],
                caption=f'<b>Character Name:</b> {character["name"]}\n<b>Anime Name:</b> {character["anime"]}\n<b>Rarity:</b> {character["rarity"]}\n<b>ID:</b> {character["id"]}\nUpdated by <a href="tg://user?id={update.effective_user.id}">{update.effective_user.first_name}</a>',
                parse_mode='HTML'
            )

        await update.message.reply_text('Updated Done in Database.... But sometimes it Takes Time to edit Caption in Your Channel..So wait..')
    except Exception as e:
        await update.message.reply_text(f'I guess did not added bot in channel.. or character uploaded Long time ago.. Or character not exits.. orr Wrong id')

import random
from telegram.constants import ParseMode

# Store dropped characters per chat (optional: can be replaced with DB for persistence)
active_drops = {}

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
        chat_id = update.effective_chat.id

        # Save the character for this chat (to be guessed)
        active_drops[chat_id] = {
            "id": character["id"],
            "name": character["name"].lower(),  # case insensitive match
            "img_url": character["img_url"],
            "rarity": character["rarity"],
            "anime": character["anime"]
        }

        # Send the drop message (without name)
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=character["img_url"],
            caption=(
                f"A New {character['rarity']} Character Appeared...\n\n"
                f"Use <code>/guess character name</code> to add it to your harem!"
            ),
            parse_mode=ParseMode.HTML
        )

    except Exception as e:
        await update.message.reply_text(f"Error while dropping: {e}")

async def guess(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user = update.effective_user

    if chat_id not in active_drops:
        await update.message.reply_text("No character is currently dropped in this chat.")
        return

    if not context.args:
        await update.message.reply_text("Please guess the character name. Usage: /guess <name>")
        return

    guess_name = " ".join(context.args).lower()
    character = active_drops[chat_id]

    if guess_name == character["name"]:
        await update.message.reply_text(
            f"🎉 <a href='tg://user?id={user.id}'>{user.first_name}</a> correctly guessed the character!\n"
            f"You added <b>{character['name']}</b> from <b>{character['anime']}</b> to your harem!",
            parse_mode=ParseMode.HTML
        )
        # You could add DB insert here to save the character to user's harem
        del active_drops[chat_id]
    else:
        await update.message.reply_text("❌ Wrong guess! Try again.")

GUESS_HANDLER = CommandHandler('guess', guess, block=False)
application.add_handler(GUESS_HANDLER)
FDROP_HANDLER = CommandHandler('fdrop', fdrop, block=False)
application.add_handler(FDROP_HANDLER)
UPLOAD_HANDLER = CommandHandler('upload', upload, block=False)
application.add_handler(UPLOAD_HANDLER)
DELETE_HANDLER = CommandHandler('delete', delete, block=False)
application.add_handler(DELETE_HANDLER)
UPDATE_HANDLER = CommandHandler('update', update, block=False)
application.add_handler(UPDATE_HANDLER)

