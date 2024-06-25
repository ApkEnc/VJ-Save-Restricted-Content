import pyrogram
from pyrogram import Client, filters
from pyrogram.errors import UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied, FloodWait
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import os
import threading
import traceback
from os import environ

bot_token = environ.get("TOKEN", "")
api_hash = environ.get("HASH", "")
api_id = int(environ.get("ID", ""))
bot = Client("mybot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

ss = environ.get("STRING", "")
if ss is not None:
    acc = Client("myacc", api_id=api_id, api_hash=api_hash, session_string=ss)
    acc.start()
else:
    acc = None

# Function to handle Telegram API errors including FloodWait
async def handle_telegram_errors(func, *args, **kwargs):
    try:
        return await func(*args, **kwargs)
    except FloodWait as e:
        wait_time = e.seconds
        print(f"Telegram flood control: Waiting for {wait_time} seconds...")
        await asyncio.sleep(wait_time)
        return await handle_telegram_errors(func, *args, **kwargs)
    except pyrogram.errors.exceptions.TelegramError as e:
        print(f"Telegram error occurred: {e}")
        traceback.print_exc()  # Print full traceback for debugging
        # Handle other Telegram errors as needed
        # Example: retry after some time or notify admin
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        traceback.print_exc()  # Print full traceback for debugging
        # Handle other unexpected errors

# Function to stop ongoing processes
async def stop_all_processes():
    # Implement logic to stop ongoing tasks
    # For example, stop threads, clear queues, etc.
    pass

# Command handler for /stop command
@bot.on_message(filters.command(["stop"]))
async def stop_command(client, message):
    await handle_telegram_errors(bot.send_message, message.chat.id, "Stopping all ongoing processes...")
    await stop_all_processes()
    await handle_telegram_errors(bot.send_message, message.chat.id, "All ongoing processes stopped.")

# Your existing start command
@bot.on_message(filters.command(["start"]))
async def send_start(client, message):
    await handle_telegram_errors(bot.send_message, message.chat.id, f"**👋 Hi {message.from_user.mention}**, **I am Save Restricted Bot, I can send you restricted content by its post link**\n\n{USAGE}",
                                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🌐 Update Channel", url="https://t.me/VJ_Botz")]]), reply_to_message_id=message.message_id)

# Your existing save function
@bot.on_message(filters.text)
async def save(client, message):
    if message.text.strip() == "":
        await handle_telegram_errors(bot.send_message, message.chat.id, "Error: Message is empty or contains invalid characters.")
        return

    # Process different types of message URLs
    if "https://t.me/+" in message.text or "https://t.me/joinchat/" in message.text:
        if acc is None:
            await handle_telegram_errors(bot.send_message, message.chat.id, f"**String Session is not Set**", reply_to_message_id=message.message_id)
            return

        try:
            try:
                await acc.join_chat(message.text)
            except Exception as e:
                await handle_telegram_errors(bot.send_message, message.chat.id, f"**Error** : __{e}__", reply_to_message_id=message.message_id)
                return
            await handle_telegram_errors(bot.send_message, message.chat.id, "**Chat Joined**", reply_to_message_id=message.message_id)
        except UserAlreadyParticipant:
            await handle_telegram_errors(bot.send_message, message.chat.id, "**Chat already Joined**", reply_to_message_id=message.message_id)
        except InviteHashExpired:
            await handle_telegram_errors(bot.send_message, message.chat.id, "**Invalid Link**", reply_to_message_id=message.message_id)

    elif "https://t.me/" in message.text:
        datas = message.text.split("/")
        temp = datas[-1].replace("?single", "").split("-")
        fromID = int(temp[0].strip())
        try:
            toID = int(temp[1].strip())
        except:
            toID = fromID

        for msgid in range(fromID, toID + 1):
            if "https://t.me/c/" in message.text:
                chatid = int("-100" + datas[4])

                if acc is None:
                    await handle_telegram_errors(bot.send_message, message.chat.id, f"**String Session is not Set**", reply_to_message_id=message.message_id)
                    return

                await handle_private(message, chatid, msgid)

            elif "https://t.me/b/" in message.text:
                username = datas[4]

                if acc is None:
                    await handle_telegram_errors(bot.send_message, message.chat.id, f"**String Session is not Set**", reply_to_message_id=message.message_id)
                    return

                try:
                    await handle_private(message, username, msgid)
                except Exception as e:
                    await handle_telegram_errors(bot.send_message, message.chat.id, f"**Error** : __{e}__", reply_to_message_id=message.message_id)

            else:
                username = datas[3]

                try:
                    msg = await handle_telegram_errors(bot.get_messages, username, msgid)
                except UsernameNotOccupied:
                    await handle_telegram_errors(bot.send_message, message.chat.id, f"**The username is not occupied by anyone**", reply_to_message_id=message.message_id)
                    return

                try:
                    await handle_telegram_errors(bot.copy_message, message.chat.id, msg.chat.id, msg.message_id, reply_to_message_id=message.message_id)
                except:
                    if acc is None:
                        await handle_telegram_errors(bot.send_message, message.chat.id, f"**String Session is not Set**", reply_to_message_id=message.message_id)
                        return

                    try:
                        await handle_private(message, username, msgid)
                    except Exception as e:
                        await handle_telegram_errors(bot.send_message, message.chat.id, f"**Error** : __{e}__", reply_to_message_id=message.message_id)

            # Add a small delay between processing messages
            await asyncio.sleep(3)

# Function to handle private messages
async def handle_private(message, chatid, msgid):
    try:
        msg = await handle_telegram_errors(acc.get_messages, chatid, msgid)
        msg_type = get_message_type(msg)

        if "Text" == msg_type:
            await handle_telegram_errors(bot.send_message, message.chat.id, msg.text, entities=msg.entities, reply_to_message_id=message.message_id)
            return

        smsg = await handle_telegram_errors(bot.send_message, message.chat.id, '__Downloading__', reply_to_message_id=message.message_id)
        dosta = threading.Thread(target=lambda: asyncio.run(downstatus(f'{message.message_id}downstatus.txt', smsg)), daemon=True)
        dosta.start()
        file = await handle_telegram_errors(acc.download_media, msg, progress=progress, progress_args=[message, "down"])
        os.remove(f'{message.message_id}downstatus.txt')

        upsta = threading.Thread(target=lambda: asyncio.run(upstatus(f'{message.message_id}upstatus.txt', smsg)), daemon=True)
        upsta.start()

        if "Document" == msg_type:
            try:
                thumb = await handle_telegram_errors(acc.download_media, msg.document.thumbs[0].file_id)
            except:
                thumb = None

            await handle_telegram_errors(bot.send_document, message.chat.id, file, thumb=thumb, caption=msg.caption, caption_entities=msg.caption_entities, reply_to_message_id=message.message_id, progress=progress, progress_args=[message, "up"])
            if thumb is not None:
                os.remove(thumb)

        elif "Video" == msg_type:
            try:
                thumb = await handle_telegram_errors(acc.download_media, msg.video.thumbs[0].file_id)
            except:
                thumb = None

            await handle_telegram_errors(bot.send_video, message.chat.id, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=thumb, caption=msg.caption, caption_entities=msg.caption_entities, reply_to_message_id=message.message_id, progress=progress, progress_args=[message, "up"])
            if thumb is not None:
                os.remove(thumb)

        elif "Animation" == msg_type:
            await handle_telegram_errors(bot.send_animation, message.chat.id, file, reply_to_message_id=message.message_id)

        elif "Sticker" == msg_type:
            await handle_telegram_errors(bot.send_sticker, message.chat.id, file, reply_to_message_id=message.message_id)

        elif "Voice" == msg_type:
            await handle_telegram_errors(bot.send_voice, message.chat.id, file, caption=msg.caption, thumb=thumb, caption_entities=msg.caption_entities, reply_to_message_id=message.message_id, progress=progress, progress_args=[message, "up"])

        elif "Audio" == msg_type:
            try:
                thumb = await handle_telegram_errors(acc.download_media, msg.audio.thumbs[0].file_id)
            except:
                thumb = None

            await handle_telegram_errors(bot.send_audio, message.chat.id, file, caption=msg.caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])
            if thumb is not None:
                os.remove(thumb)

        elif "Photo" == msg_type:
            await handle_telegram_errors(bot.send_photo, message.chat.id, file, caption=msg.caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id)

        os.remove(file)
        if os.path.exists(f'{message.id}upstatus.txt'):
            os.remove(f'{message.id}upstatus.txt')
        await handle_telegram_errors(bot.delete_messages, message.chat.id, [smsg.id])

    except Exception as e:
        print(f"Error in handle_private: {e}")
        traceback.print_exc()

# get the type of message
def get_message_type(msg: pyrogram.types.messages_and_media.message.Message):
    try:
        msg.document.file_id
        return "Document"
    except:
        pass

    try:
        msg.video.file_id
        return "Video"
    except:
        pass

    try:
        msg.animation.file_id
        return "Animation"
    except:
        pass

    try:
        msg.sticker.file_id
        return "Sticker"
    except:
        pass

    try:
        msg.voice.file_id
        return "Voice"
    except:
        pass

    try:
        msg.audio.file_id
        return "Audio"
    except:
        pass

    try:
        msg.photo.file_id
        return "Photo"
    except:
        pass

    try:
        msg.text
        return "Text"
    except:
        pass

USAGE = """**FOR PUBLIC CHATS**

**__just send post/s link__**

**FOR PRIVATE CHATS**

**__first send invite link of the chat (unnecessary if the account of string session already member of the chat)
then send post/s link__**

**FOR BOT CHATS**

**__send link with** '/b/', **bot's username and message id, you might want to install some unofficial client to get the id like below__**

https://t.me/b/botusername/4321


**MULTI POSTS**

**__send public/private posts link as explained above with format "from - to" to send multiple messages like below__**

https://t.me/xxxx/1001-1010

https://t.me/c/xxxx/101 - 120


**__note that space in between doesn't matter__**
"""

# infinty polling
bot.run()
