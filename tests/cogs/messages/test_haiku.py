import pytest
from unittest import mock
from discord import Embed, Colour
from duckbot.cogs.messages import Haiku

EMBED_NAME = ":cherry_blossom: **Haiku Detected** :cherry_blossom:"


@pytest.mark.asyncio
@mock.patch("nltk.download")
@mock.patch("nltk.corpus.cmudict.dict", return_value={"a": [["A1"]], "and": [["A1"]], "batman": [["A1", "A1"]]})
async def test_build_syllable_dictionary_builds_table(download, cmu, bot):
    clazz = Haiku(bot)
    await clazz.build_syllable_dictionary()
    assert clazz.syllables == {"a": 1, "and": 1, "batman": 2}


@pytest.mark.asyncio
async def test_detect_haiku_bot_author(bot, message):
    message.author = bot.user
    clazz = Haiku(bot)
    await clazz.detect_haiku(message)
    message.channel.send.assert_not_called()


@pytest.mark.asyncio
async def test_detect_haiku_finds_one_word_per_line_haiku(bot, message):
    message.clean_content = "five seven five"
    clazz = Haiku(bot)
    clazz.syllables = {"five": 5, "seven": 7}
    await clazz.detect_haiku(message)
    embed = Embed(colour=Colour.dark_red()).add_field(name=EMBED_NAME, value="_five\nseven\nfive_")
    message.channel.send.assert_called_once_with(embed=embed)


@pytest.mark.asyncio
async def test_detect_haiku_ignores_punctuation(bot, message):
    message.clean_content = "five, seven.?! five"
    clazz = Haiku(bot)
    clazz.syllables = {"five": 5, "seven": 7}
    await clazz.detect_haiku(message)
    embed = Embed(colour=Colour.dark_red()).add_field(name=EMBED_NAME, value="_five\nseven\nfive_")
    message.channel.send.assert_called_once_with(embed=embed)


@pytest.mark.asyncio
async def test_detect_haiku_finds_case_insensitive_haiku(bot, message):
    message.clean_content = "FiVe SEVEN fIve"
    clazz = Haiku(bot)
    clazz.syllables = {"five": 5, "seven": 7}
    await clazz.detect_haiku(message)
    embed = Embed(colour=Colour.dark_red()).add_field(name=EMBED_NAME, value="_FiVe\nSEVEN\nfIve_")
    message.channel.send.assert_called_once_with(embed=embed)


@pytest.mark.asyncio
async def test_detect_haiku_finds_multiple_word_haiki(bot, message):
    message.clean_content = "two two one three two one one one four"
    clazz = Haiku(bot)
    clazz.syllables = {"one": 1, "two": 2, "three": 3, "four": 4}
    await clazz.detect_haiku(message)
    embed = Embed(colour=Colour.dark_red()).add_field(name=EMBED_NAME, value="_two two one\nthree two one one\none four_")
    message.channel.send.assert_called_once_with(embed=embed)


@pytest.mark.asyncio
async def test_detect_haiku_starts_with_haiku_but_has_extra_words(bot, message):
    message.clean_content = "five seven five and some other stuff"
    clazz = Haiku(bot)
    clazz.syllables = {"five": 5, "seven": 7}
    await clazz.detect_haiku(message)
    message.channel.send.assert_not_called()


@pytest.mark.asyncio
async def test_detect_haiku_no_haiku(bot, message):
    message.clean_content = "four one four one four two one"
    clazz = Haiku(bot)
    clazz.syllables = {"one": 1, "two": 2, "three": 3, "four": 4}
    await clazz.detect_haiku(message)
    message.channel.send.assert_not_called()


@pytest.mark.asyncio
async def test_detect_haiku_unknown_words(bot, message):
    message.clean_content = "haiku me, brother"
    clazz = Haiku(bot)
    clazz.syllables = {}
    await clazz.detect_haiku(message)
    message.channel.send.assert_not_called()
