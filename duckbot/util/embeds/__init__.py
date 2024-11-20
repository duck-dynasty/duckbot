from typing import List

from discord import Embed

# https://discord.com/developers/docs/resources/channel#embed-limits
MAX_EMBED_LENGTH = 6000
MAX_TITLE_LENGTH = 256
MAX_DESCRIPTION_LENGTH = 4096
MAX_FIELDS = 25
MAX_FIELD_NAME_LENGTH = 256
MAX_FIELD_VALUE_LENGTH = 1024
MAX_FOOTER_LENGTH = 2048
MAX_AUTHOR_NAME_LENGTH = 256


def group_by_max_length(embeds: List[Embed]) -> List[List[Embed]]:
    """Returns groups of embeds which will fit into a single discord message.
    Will still fail if any single embed is itself bigger than the limit."""
    total, group, groups = 0, [], []
    for embed in embeds:
        length = len(embed)
        if total + length < MAX_EMBED_LENGTH:
            total += length
            group.append(embed)
        else:
            total = 0
            groups.append(group)
    return groups + [group] if group else groups
