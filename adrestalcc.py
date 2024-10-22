import os
import asyncio
from telethon import TelegramClient, events
from dotenv import load_dotenv
from telethon.tl.types import PeerChannel

# Load environment variables from .env file
load_dotenv()

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')

# Chat ID or username to send the detected messages
target_chat_id = os.getenv('TARGET_CHAT_ID')
monitor_channel = os.getenv('MONITOR_CHANNEL')

# Initialize TelegramClient with your personal session
client = TelegramClient('user_session', api_id, api_hash)

# ANSI escape codes for color
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_RED = "\033[91m"
COLOR_RESET = "\033[0m"

# Function to forward the message along with the sender's name or channel title
async def handle_new_message(event):
    message_text = event.message.message  # Get the message text
    sender = await event.get_sender()  # Get the sender of the message

    if message_text and sender:
        # Check if the sender is a user or a channel
        if hasattr(sender, 'first_name'):  # If it's a user
            sender_name = sender.first_name
            if sender.username:
                sender_name += f" (@{sender.username})"
        elif hasattr(sender, 'title'):  # If it's a channel
            sender_name = sender.title  # Use the channel title
        else:
            sender_name = "Unknown Sender"

        # Print message for debugging
        print(f"{COLOR_YELLOW}New message from {sender_name}: {message_text}{COLOR_RESET}")

        # Compose the message to forward (including the sender's name)
        forward_message = f"Message from {sender_name}:\n\n{message_text}"

        try:
            # Resolve the target chat/user entity using get_entity
            target_entity = await client.get_entity(target_chat_id)
            
            # Forward the message along with the sender's name
            await client.send_message(target_entity, forward_message)
            
            print(f"{COLOR_GREEN}Message from {sender_name} forwarded successfully to {target_chat_id}{COLOR_RESET}")
        except Exception as e:
            print(f"{COLOR_RED}Failed to forward message from {sender_name}: {e}{COLOR_RESET}")
    else:
        # Log if there is no text in the message (e.g., media, stickers, etc.)
        print(f"{COLOR_YELLOW}Received a message with no text or sender information.{COLOR_RESET}")

# Function to fetch the channel ID based on the username
async def fetch_channel_id():
    channel_identifier = monitor_channel  # Can be username, invite link, or channel ID
    try:
        # Check if channel_identifier is numeric (indicating a raw channel ID)
        if channel_identifier.isdigit():
            entity = PeerChannel(int(channel_identifier))
            print(f"Monitoring messages from channel ID: {channel_identifier}")
        else:
            # Fetch the entity using the username or invite link
            entity = await client.get_entity(channel_identifier)
            print(f"Monitoring messages from channel: {entity.title} (ID: {entity.id})")
        return entity  # Return the channel entity
    except Exception as e:
        print(f"{COLOR_RED}Error: Unable to fetch channel using identifier {channel_identifier}. Details: {e}{COLOR_RESET}")
        return None

# Run the bot using the current event loop
async def main():
    # Fetch channel ID from username input
    channel_id = await fetch_channel_id()
    
    if not channel_id:
        print(f"{COLOR_RED}Could not fetch channel ID. Exiting.{COLOR_RESET}")
        return
    
    # Modify the NewMessage listener to listen to this channel
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

