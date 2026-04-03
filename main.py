import os
import logging
import sys
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def validate_env_vars():
    """Validate that all required environment variables are set."""
    required_vars = ['API_ID', 'API_HASH', 'SOURCE_CHAT', 'DESTINATION_CHAT']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these variables in Railway environment settings.")
        return False
    
    return True

async def main():
    """Main function to run the Telegram forwarder."""
    try:
        # Validate environment variables
        if not validate_env_vars():
            logger.error("Environment validation failed. Exiting.")
            sys.exit(1)
        
        # Get environment variables
        api_id = int(os.getenv('API_ID'))
        api_hash = os.getenv('API_HASH')
        source_chat = int(os.getenv('SOURCE_CHAT'))
        destination_chat = int(os.getenv('DESTINATION_CHAT'))
        
        logger.info("Starting Telegram Autoforwarder...")
        logger.info(f"Source Chat: {source_chat}, Destination Chat: {destination_chat}")
        
        # Initialize Telegram client
        client = TelegramClient('session', api_id, api_hash)
        
        try:
            await client.start()
            logger.info("Successfully connected to Telegram")
        except SessionPasswordNeededError:
            logger.error("Session password needed. Please authenticate manually.")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Failed to connect to Telegram: {e}")
            sys.exit(1)
        
        # Set up message forwarding
        @client.on(events.NewMessage(chats=source_chat))
        async def handler(event):
            try:
                logger.info(f"Forwarding message from {source_chat} to {destination_chat}")
                await client.forward_messages(destination_chat, event.message)
                logger.info("Message forwarded successfully")
            except Exception as e:
                logger.error(f"Error forwarding message: {e}")
        
        logger.info("Listening for messages... (Press Ctrl+C to stop)")
        await client.run_until_disconnected()
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal. Shutting down gracefully...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        if 'client' in locals():
            await client.disconnect()
            logger.info("Disconnected from Telegram")

if __name__ == '__main__':
    import asyncio
    from telethon import events
    
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
