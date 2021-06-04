from discord import Message


async def try_delete(message: Message) -> None:
    """Attempts to delete the message, ignoring permission or other errors."""
    if message:
        await message.delete(delay=0)  # delay != None, the library already ignores errors
