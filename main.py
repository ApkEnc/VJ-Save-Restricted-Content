import pyrogram
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import os
import traceback
from os import environ
import threading

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
    except pyrogram.errors.TelegramError as e:
        print(f"Telegram error occurred: {e}")
        traceback.print_exc()  # Print full traceback for debugging
        # Handle other Telegram errors as needed
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

# Command handler for /start command
@bot.on_message(filters.command(["start"]))
async def send_start(client, message):
    await handle_telegram_errors(bot.send_message, message.chat.id, f"**👋 Hi {message.from_user.mention}**, **I am Save Restricted Bot, I can send you restricted content by its post link**\n\n{USAGE}",
                                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🌐 Update Channel", url="https://t.me/VJ_Botz")]]), reply_to_message_id=message.message_id)

# Message handler for saving content
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
                    msg = await handle_telegram_errors(acc.get_messages, username, msgid)
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

        # Example handling for file types
        # Download and send file based on type
        if msg_type == "Document":
            await handle_document(message, msg)
        elif msg_type == "Video":
            await handle_video(message, msg)
        # Add handling for other types as needed

    except Exception as
 e:
        print(f"Error in handle_private: {e}")
        traceback.print_exc()

# Example function to handle document messages
async def handle_document(message, msg):
    try:
        # Download document
        file_path = await handle_telegram_errors(acc.download_media, msg, file_name="downloaded_file")
        # Send document
        await handle_telegram_errors(bot.send_document, message.chat.id, file_path, reply_to_message_id=message.message_id)
        # Remove temporary file
        os.remove(file_path)
    except Exception as e:
        print(f"Error handling document: {e}")
        traceback.print_exc()

# Example function to handle video messages
async def handle_video(message, msg):
    try:
        # Download video
        file_path = await handle_telegram_errors(acc.download_media, msg, file_name="downloaded_video")
        # Send video
        await handle_telegram_errors(bot.send_video, message.chat.id, file_path, reply_to_message_id=message.message_id)
        # Remove temporary file
        os.remove(file_path)
    except Exception as e:
        print(f"Error handling video: {e}")
        traceback.print_exc()

# Function to determine message type
def get_message_type(msg):
    if msg.text:
        return "Text"
    elif msg.document:
        return "Document"
    elif msg.video:
        return "Video"
    # Add more checks for other message types as needed
    else:
        return "Unknown"

# Function to handle thread initialization
def start_bot():
    bot.run()

# Starting the bot in a separate thread
bot_thread = threading.Thread(target=start_bot)
bot_thread.start()
