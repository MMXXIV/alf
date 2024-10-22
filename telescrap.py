import os
import re
import asyncio
from telethon import TelegramClient, events
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')

# Chat ID or username to send the detected smart contracts
target_chat_id = os.getenv('TARGET_CHAT_ID')
monitor_channel = os.getenv('MONITOR_CHANNEL')

# Regular expression to match any sequence of exactly 44 characters without spaces (for Solana smart contracts)
smart_contract_pattern = re.compile(r'\S{44}')

# Initialize TelegramClient with your personal session
client = TelegramClient('user_session', api_id, api_hash)

# ANSI escape codes for color
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_RED = "\033[91m"
COLOR_RESET = "\033[0m"

# Function to detect smart contract and send it to the target chat
async def handle_new_message(event):
    message_text = event.message.message  # Get the message text

    if message_text:
        # Print message for debugging
        print(f"{COLOR_YELLOW}New message received: {message_text}{COLOR_RESET}")

        # Strip any surrounding whitespace or newlines from the message
        message_text = message_text.strip()

        # Look for any chain of exactly 44 characters without spaces in the message
        smart_contracts = smart_contract_pattern.findall(message_text)
        if smart_contracts:
            for smart_contract in smart_contracts:
                print(f"{COLOR_GREEN}Detected Smart Contract: {smart_contract}{COLOR_RESET}")
                try:
                    # Resolve the target chat/user entity using get_entity
                    target_entity = await client.get_entity(target_chat_id)
                    
                    # Send the smart contract to the resolved entity (if needed)
                    await client.send_message(target_entity, f"{smart_contract}")
                    
                    # Additional: Send the "Buy 1 SOL" command to the bot
                    await asyncio.sleep(0.5)  # Short delay to simulate human interaction
                    # await client.send_message(target_entity, "1 SOL")  # Select 1 SOL
                    
                    print(f"{COLOR_GREEN}Smart contract sent successfully and triggered 'Buy 1 SOL' to {target_chat_id}{COLOR_RESET}")
                except Exception as e:
                    print(f"{COLOR_RED}Failed to send smart contract or execute buy: {e}{COLOR_RESET}")
        else:
            # Log regular messages (in yellow)
            print(f"{COLOR_YELLOW}Regular message received, no smart contract detected.{COLOR_RESET}")

# Function to fetch the channel ID based on the username
async def fetch_channel_id():
    channel_username = monitor_channel
    try:
        entity = await client.get_entity(channel_username)
        print(f"Monitoring messages from channel: {entity.title} (ID: {entity.id})")
        return entity.id  # Return the channel ID
    except Exception as e:
        print(f"{COLOR_RED}Error: Unable to fetch channel ID for {channel_username}. Details: {e}{COLOR_RESET}")
        return None

# Run the bot using the current event loop
async def main():
    # Fetch channel ID from username input
    channel_id = await fetch_channel_id()
    
    if not channel_id:
        print(f"{COLOR_RED}Could not fetch channel ID. Exiting.{COLOR_RESET}")
        return
    
    # Modify the NewMessage listener to only listen to this channel
    @client.on(events.NewMessage(chats=channel_id))
    async def new_message_listener(event):
        await handle_new_message(event)

    # Run the client until it's disconnected
    await client.run_until_disconnected()

if __name__ == "__main__":
    # Start the Telegram client (user session)
    client.start()

    loop = asyncio.get_event_loop()
    if loop is not None and loop.is_running():
        loop.create_task(main())
    else:
        loop.run_until_complete(main())
