from typing import Iterable, List

from discord.app_commands import Choice


def choices(pool: Iterable[str], needle: str, min_characters: int = 3, in_order: bool = True) -> List[Choice[str]]:
    """Returns autocomplete choices from the pool matching the needle, case insensitively.
    In order matching allows gaps between the needle's letters, otherwise the needle must appear whole."""

    def match(needle: str, haystack: str) -> bool:
        if in_order:
            it = iter(haystack)
            return all(any(letter == ch for letter in it) for ch in needle)
        else:
            return needle in haystack

    if len(needle) < min_characters:
        return []
    else:
        return [Choice(name=i, value=i) for i in pool if match(needle.lower(), i.lower())][:25]  # discord caps options at 25
