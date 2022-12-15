from typing import Optional

from discord import Message


async def get_message_reference(message: Message) -> Optional[Message]:
    """Returns the message that the given message has replied to, or None if it is not a reply.
    :param message return the message to which this message is a reply"""
    ref = None if message is None else message.reference
    if ref:
        return ref.cached_message if ref.cached_message else await message.channel.fetch_message(ref.message_id)
    else:
        return None
