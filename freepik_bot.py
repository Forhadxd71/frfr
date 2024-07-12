import logging
import re
import requests
import json
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.exceptions import MessageToDeleteNotFound

# Initialize bot and dispatcher
bot_token = '7356825607:AAFrCmn2zfstPspsp2agDBdvaGj2GM0LpmE'  # Replace with your bot's token
bot = Bot(token=bot_token)
dp = Dispatcher(bot)

# Function to load cookies from a file
def load_cookies(file_path):
    with open(file_path, 'r') as file:
        cookies_raw = json.load(file)
        if isinstance(cookies_raw, dict):
            return cookies_raw
        elif isinstance(cookies_raw, list):
            cookies = {}
            for cookie in cookies_raw:
                if 'name' in cookie and 'value' in cookie:
                    cookies[cookie['name']] = cookie['value']
            return cookies
        else:
            raise ValueError("Cookies are in an unsupported format.")

# Load cookies
cookies = load_cookies('cookie.json')

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

@dp.message_handler(commands=['freepik'])  # You can change the command to anything
async def process_freepik_url(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    # Check if the URL is valid
    url = message.get_args()
    match = re.search(r'freepik\.com/(.+)', url)
    if not url or not match:
        await message.answer("<b>Please provide a valid Freepik URL after the /freepik command</b>", parse_mode='HTML')
        return

    resource_id = match.group(1)
    first_url = f'https://www.freepik.com/{resource_id}'

    # Send a loading message
    loading_message = await message.answer("<b>Processing your request...</b>", parse_mode='HTML')

    try:
        # First request
        response = requests.get(first_url, cookies=cookies)
        print(response.text)  # Print the response text for debugging
        if response.status_code == 200:
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
                    download_button = types.InlineKeyboardMarkup()
                    download_button.add(types.InlineKeyboardButton(text="Download Now", url=download_url))

                    # Send the message with the inline button
                    await message.answer(message_text, reply_markup=download_button, parse_mode='HTML')
                else:
                    await message.answer("Failed to get the download URL.", parse_mode='HTML')
            except json.JSONDecodeError:
                await message.answer("Failed to parse the response JSON.", parse_mode='HTML')
        else:
            await message.answer(f"First request failed with status code: {response.status_code}", parse_mode='HTML')

    except Exception as e:
        await message.answer(f"<code>An error occurred: {e}</code>", parse_mode='HTML')

    # After processing is complete, delete the loading message
    try:
        await bot.delete_message(chat_id, loading_message.message_id)
    except MessageToDeleteNotFound:
        pass  # Message was already deleted

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
