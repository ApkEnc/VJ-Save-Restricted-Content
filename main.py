import pyrogram
from pyrogram import Client, filters
from pyrogram.errors import UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import threading
import os
import time
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

# download status
def downstatus(statusfile, message):
    while True:
        if os.path.exists(statusfile):
            break
        time.sleep(3)

    while os.path.exists(statusfile):
        with open(statusfile, "r") as downread:
            txt = downread.read()
        try:
            bot.edit_message_text(message.chat.id, message.message_id, f"__Downloaded__ : **{txt}**")
            time.sleep(10)
        except pyrogram.errors.exceptions.bad_request_400.MessageEmpty:
            pass
        except Exception as e:
            print(f"Error editing message: {e}")
        time.sleep(5)

# upload status
def upstatus(statusfile, message):
    while True:
        if os.path.exists(statusfile):
            break
        time.sleep(3)

    while os.path.exists(statusfile):
        with open(statusfile, "r") as upread:
            txt = upread.read()
        try:
            bot.edit_message_text(message.chat.id, message.message_id, f"__Uploaded__ : **{txt}**")
            time.sleep(10)
        except pyrogram.errors.exceptions.bad_request_400.MessageEmpty:
            pass
        except Exception as e:
            print(f"Error editing message: {e}")
        time.sleep(5)

# progress writer
def progress(current, total, message, type):
    with open(f'{message.message_id}{type}status.txt', "w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")

# start command
@bot.on_message(filters.command(["start"]))
def send_start(client, message):
    bot.send_message(
        message.chat.id,
        f"**👋 Hi {message.from_user.mention}, I am Save Restricted Bot.**\n\n{USAGE}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🌐 Update Channel", url="https://t.me/shivam_afk_pfps")]
        ]),
        reply_to_message_id=message.message_id
    )

@bot.on_message(filters.text)
def save(client, message):
    try:
        if message.text.strip() == "":
            return  # Skip empty messages
        
        datas = message.text.split("/")
        temp = datas[-1].replace("?single", "").split("-")
        fromID = int(temp[0].strip())
        try:
            toID = int(temp[1].strip())
        except:
            toID = fromID

        for msgid in range(fromID, toID + 1):
            if message.text.strip() == "":
                continue  # Skip empty messages
            
            # Private chat handling
            if "https://t.me/c/" in message.text:
                chatid = int("-100" + datas[4])
                if acc is None:
                    bot.send_message(message.chat.id, "**String Session is not Set**", reply_to_message_id=message.message_id)
                    return
                handle_private(message, chatid, msgid)

            # Bot chat handling
            elif "https://t.me/b/" in message.text:
                username = datas[4]
                if acc is None:
                    bot.send_message(message.chat.id, "**String Session is not Set**", reply_to_message_id=message.message_id)
                    return
                try:
                    handle_private(message, username, msgid)
                except Exception as e:
                    bot.send_message(message.chat.id, f"**Error**: __{e}__", reply_to_message_id=message.message_id)

            # Public chat handling
            else:
                username = datas[3]
                try:
                    msg = bot.get_messages(username, msgid)
                    bot.copy_message(message.chat.id, msg.chat.id, msg.message_id, reply_to_message_id=message.message_id)
                except UsernameNotOccupied:
                    bot.send_message(message.chat.id, "**The username is not occupied by anyone**", reply_to_message_id=message.message_id)
                    return
                except Exception as e:
                    if acc is None:
                        bot.send_message(message.chat.id, "**String Session is not Set**", reply_to_message_id=message.message_id)
                        return
                    try:
                        handle_private(message, username, msgid)
                    except Exception as e:
                        bot.send_message(message.chat.id, f"**Error**: __{e}__", reply_to_message_id=message.message_id)

            time.sleep(3)  # Wait time between messages

    except Exception as e:
        print(f"Error handling message: {e}")

# Handle private messages
def handle_private(message, chatid, msgid):
    try:
        msg = acc.get_messages(chatid, msgid)
        msg_type = get_message_type(msg)

        if msg_type == "Text":
            bot.send_message(message.chat.id, msg.text, entities=msg.entities, reply_to_message_id=message.message_id)
            return

        smsg = bot.send_message(message.chat.id, '__Downloading__', reply_to_message_id=message.message_id)
        dosta = threading.Thread(target=lambda: downstatus(f'{message.message_id}downstatus.txt', smsg), daemon=True)
        dosta.start()
        file = acc.download_media(msg, progress=progress, progress_args=[message, "down"])
        os.remove(f'{message.message_id}downstatus.txt')

        upsta = threading.Thread(target=lambda: upstatus(f'{message.message_id}upstatus.txt', smsg), daemon=True)
        upsta.start()

        if msg_type == "Document":
            try:
                thumb = acc.download_media(msg.document.thumbs[0].file_id)
            except:
                thumb = None

            bot.send_document(message.chat.id, file, thumb=thumb, caption=msg.caption, caption_entities=msg.caption_entities,
                              reply_to_message_id=message.message_id, progress=progress, progress_args=[message, "up"])
            if thumb is not None:
                os.remove(thumb)

        elif msg_type == "Video":
            try:
                thumb = acc.download_media(msg.video.thumbs[0].file_id)
            except:
                thumb = None

            bot.send_video(message.chat.id, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height,
                           thumb=thumb, caption=msg.caption, caption_entities=msg.caption_entities, reply_to_message_id=message.message_id,
                           progress=progress, progress_args=[message, "up"])
            if thumb is not None:
                os.remove(thumb)

        elif msg_type == "Animation":
            bot.send_animation(message.chat.id, file, reply_to_message_id=message.message_id)

        elif msg_type == "Sticker":
            bot.send_sticker(message.chat.id, file, reply_to_message_id=message.message_id)

        elif msg_type == "Voice":
            bot.send_voice(message.chat.id, file, caption=msg.caption, thumb=thumb, caption_entities=msg.caption_entities,
                           reply_to_message_id=message.message_id, progress=progress, progress_args=[message, "up"])

        elif msg_type == "Audio":
            try:
                thumb = acc.download_media(msg.audio.thumbs[0].file_id)
            except:
                thumb = None

            bot.send_audio(message.chat.id, file, caption=msg.caption, caption_entities=msg.caption_entities,
                           reply_to_message_id=message.message_id, progress=progress, progress_args=[message, "up"])
            if thumb is not None:
                os.remove(thumb)

        elif msg_type == "Photo":
            bot.send_photo(message.chat.id, file, caption=msg.caption, caption_entities=msg.caption_entities,
                           reply_to_message_id=message.message_id)

        os.remove(file)
        if os.path.exists(f'{message.message_id}upstatus.txt'):
            os.remove(f'{message.message_id}upstatus.txt')
        bot.delete_messages(message.chat.id, [smsg.message_id])

    except Exception as e:
        print(f"Error handling private message: {e}")

# Get the type of message
def get_message_type(msg):
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

USAGE = """
**Instructions:**

1. Send posts link to save messages for forwarding.

2. To forward saved messages, use `/fr` command.

3. Use `/forward_even` or `/forward_odd` followed by the post range to forward even or odd messages.
"""

# Command to forward even messages
@bot.on_message(filters.command(["forward_even"]))
def forward_even_messages(client, message):
    try:
        command_parts = message.text.split()
        if len(command_parts) != 3:
            bot.send_message(message.chat.id, "Invalid command format. Correct format: /forward_even from_id to_id")
            return
        
        from_id = int(command_parts[1])
        to_id = int(command_parts[2])
        
        if from_id > to_id:
            bot.send_message(message.chat.id, "Invalid range. 'from_id' should be less than or equal to 'to_id'.")
            return
        
        for msg_id in range(from_id, to_id + 1):
            try:
                msg = bot.get_messages(message.chat.id, msg_id)
                msg_type = get_message_type(msg)
                
                # Forward only even messages
                if msg_id % 2 == 0:
                    bot.forward_messages(message.chat.id, message.chat.id, [msg_id])
                    time.sleep(1)  # Delay between each message forward
                
            except Exception as e:
                print(f"Error forwarding message {msg_id}: {e}")
                continue
        
        bot.send_message(message.chat.id, "Forwarding of even messages completed successfully.")

    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}")

# Command to forward odd messages
@bot.on_message(filters.command(["forward_odd"]))
def forward_odd_messages(client, message):
    try:
        command_parts = message.text.split()
        if len(command_parts) != 3:
            bot.send_message(message.chat.id, "Invalid command format. Correct format: /forward_odd from_id to_id")
            return
        
        from_id = int(command_parts[1])
        to_id = int(command_parts[2])
        
        if from_id > to_id:
            bot.send_message(message.chat.id, "Invalid range. 'from_id' should be less than or equal to 'to_id'.")
            return
        
        for msg_id in range(from_id, to_id + 1):
            try:
                msg = bot.get_messages(message.chat.id, msg_id)
                msg_type = get_message_type(msg)
                
                # Forward only odd messages
                if msg_id % 2 != 0:
                    bot.forward_messages(message.chat.id, message.chat.id, [msg_id])
                    time.sleep(1)  # Delay between each message forward
                
            except Exception as e:
                print(f"Error forwarding message {msg_id}: {e}")
                continue
        
        bot.send_message(message.chat.id, "Forwarding of odd messages completed successfully.")

    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}")

# Start the bot
USAGE = """
**Instructions:**

1. Send posts link to save messages for forwarding.

2. To forward saved messages, use `/fr` command.

3. Use `/forward_even` or `/forward_odd` followed by the post range to forward even or odd messages.
"""

bot.run()
