import os
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()

async def authenticate():
    api_id = int(os.getenv('API_ID'))
    api_hash = os.getenv('API_HASH')
    
    client = TelegramClient('session', api_id, api_hash)
    await client.start()
    print("✅ Authentication successful! session.session file created.")
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(authenticate())
