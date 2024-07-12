import logging
import re
import requests
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

# Set your Telegram API ID, API Hash, and Bot Token
api_id = 24232038
api_hash = "6b55079d2ba17ccc133881d67df066a9"
bot_token = "7356825607:AAFrCmn2zfstPspsp2agDBdvaGj2GM0LpmE"

# Initialize Pyrogram Client
app = Client("tirrexcr_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Function to load cookies from a Netscape format file
def load_cookies(file_path):
    cookies = {}
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if not line or line.startswith('#') or line.startswith('\n'):
                continue
            parts = line.strip().split('\t')
            if len(parts) == 7:
                cookies[parts[5]] = parts[6]
    return cookies

# Load cookies
cookies = load_cookies('cookies.txt')

# Function to extract necessary information from the response
def extract_information(response_json):
    document = response_json.get('document', {})
    title = document.get('title', 'Not Available')
    download_url = document.get('download_url', 'Not Available')
    author = document.get('author', {})
    author_name = author.get('name', 'Not Available')

    return {
        "title": title,
        "download_url": download_url,
        "author_name": author_name
    }

@app.on_message(filters.command("freepik"))  # You can change the command to anything
async def process_freepik_url(client, message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    # Check if the URL is valid
    url = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else ""
    match = re.search(r'freepik\.com/(.+)', url)
    if not url or not match:
        await message.reply("<b>Please provide a valid Freepik URL after the /freepik command</b>", parse_mode='HTML')
        return

    resource_id = match.group(1)
    first_url = f'https://www.freepik.com/{resource_id}'

    # Send a loading message
    loading_message = await message.reply("<b>Processing your request...</b>", parse_mode='HTML')

    try:
        # First request
        response = requests.get(first_url, cookies=cookies)
        print(response.text)  # Print the response text for debugging

        if response.headers.get('Content-Type') == 'application/json':
            try:
                response_json = response.json()
                info = extract_information(response_json)
                title = info['title']
                author_name = info['author_name']
                download_url = info['download_url']

                if download_url:
                    # Create the message text
                    message_text = (
                        f"<b>Here is the Download Link ✅\n"
                        f"━━━━━━━━━━━━━━━━\n"
                        f"Title: {title}\n"
                        f"Author Name: {author_name}\n"
                        f"Download Link: <a href='{download_url}'>Download Now</a>\n"
                        f"━━━━━━━━━━━━━━━━\n"
                        f"Freepik Downloader By: <a href='https://t.me/YOUR_BOT'>Your Bot</a></b>"
                    )
                    download_button = InlineKeyboardMarkup(
                        [[InlineKeyboardButton("Download Now", url=download_url)]]
                    )

                    # Send the message with the inline button
                    await client.send_message(chat_id, message_text, reply_markup=download_button, parse_mode='HTML')
                else:
                    await message.reply("Failed to get the download URL.", parse_mode='HTML')
            except Exception as e:
                await message.reply("Failed to parse the response JSON.", parse_mode='HTML')
        else:
            await message.reply("The response is not in JSON format.", parse_mode='HTML')

    except Exception as e:
        await message.reply(f"<code>An error occurred: {e}</code>", parse_mode='HTML')

    # After processing is complete, delete the loading message
    try:
        await loading_message.delete()
    except:
        pass  # Message was already deleted

if __name__ == '__main__':
    app.run()
