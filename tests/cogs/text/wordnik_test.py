import discord
import pytest

from duckbot.cogs.text import Wordnik
from duckbot.util.embeds import MAX_FIELD_VALUE_LENGTH
from tests.discord_test_ext import bind_commands

URL = "https://api.wordnik.com/v4/word.json"
ATTRIBUTION = "from The American Heritage® Dictionary of the English Language, 5th Edition."


@pytest.fixture(autouse=True)
def set_wordnik_key_env(monkeypatch):
    monkeypatch.setenv("WORDNIK_KEY", "wordnik-key")


@pytest.fixture
def clazz(bot) -> Wordnik:
    return bind_commands(Wordnik(bot))


async def test_define_inflected_word(clazz, context, responses):
    responses.add(responses.GET, f"{URL}/cows/definitions", json=cow_definitions())
    responses.add(responses.GET, f"{URL}/cow/pronunciations", json=cow_pronunciations())
    await clazz.define(context, word="Cows")
    embed = discord.Embed(title="cow")
    noun_lines = [
        "1. The mature female of cattle of the genus Bos.\n_this is where I'd use cow in a sentence... IF I HAD ONE_",
        "",
        "2. The mature female of certain other large animals, such as elephants, moose, or whales.\n_this is where I'd use cow in a sentence... IF I HAD ONE_",
        "",
    ]
    verb_lines = [
        "1. To frighten or subdue with threats or a show of force.\n_the intellectuals had been cowed into silence_",
        "",
    ]
    embed.add_field(name="noun: **cow**  /kou/", value="\n".join(noun_lines), inline=False)
    embed.add_field(name="transitive verb: **cow**  /kou/", value="\n".join(verb_lines), inline=False)
    embed.set_footer(text=ATTRIBUTION)
    context.send.assert_called_once_with(embed=embed)


async def test_define_unknown_word(clazz, context, responses):
    responses.add(responses.GET, f"{URL}/nothing/definitions", json={"statusCode": 404, "error": "Not Found", "message": "Not found"})
    responses.add(responses.GET, f"{URL}/why/definitions", json=why_definitions())
    responses.add(responses.GET, f"{URL}/why/pronunciations", json=[{"raw": "/hwaɪ/", "rawType": "IPA"}])
    await clazz.define(context, word="nothing")
    embed = discord.Embed(title="why")
    adverb_lines = [
        "1. For what purpose, reason, or cause.\n_why did he do it?_",
        "",
    ]
    embed.add_field(name="adverb: **why**  /hwaɪ/", value="\n".join(adverb_lines), inline=False)
    embed.set_footer(text="from Wiktionary, Creative Commons Attribution/Share-Alike License.")
    context.send.assert_called_once_with(embed=embed)


async def test_define_rate_limited(clazz, context, responses):
    error = {"statusCode": 429, "error": "Too Many Requests", "message": "API rate limit exceeded"}
    responses.add(responses.GET, f"{URL}/nothing/definitions", json=error)
    responses.add(responses.GET, f"{URL}/why/definitions", json=error)
    await clazz.define(context, word="nothing")
    context.send.assert_called_once_with("wordnik is all worded out, give it a minute")


def test_get_pronunciation_no_results(clazz, responses):
    responses.add(responses.GET, f"{URL}/cat/pronunciations", json={"statusCode": 404, "error": "Not Found", "message": "Not found"})
    assert clazz.get_pronunciation("cat") == "screw flanders"


async def test_define_truncates_long_field_value(clazz, context, responses):
    long_text = "a" * 2000
    definitions = [{"sourceDictionary": "ahd-5", "attributionText": ATTRIBUTION, "word": "cow", "partOfSpeech": "noun", "text": long_text, "exampleUses": []}]
    responses.add(responses.GET, f"{URL}/cow/definitions", json=definitions)
    responses.add(responses.GET, f"{URL}/cow/pronunciations", json=cow_pronunciations())
    await clazz.define(context, word="cow")
    sent_embed = context.send.call_args.kwargs["embed"]
    assert len(sent_embed.fields[0].value) == MAX_FIELD_VALUE_LENGTH
    assert sent_embed.fields[0].value.endswith("...")


async def test_define_handles_null_example_uses(clazz, context, responses):
    definitions = [{"sourceDictionary": "ahd-5", "attributionText": ATTRIBUTION, "word": "cow", "partOfSpeech": "noun", "text": "A big animal.", "exampleUses": None}]
    responses.add(responses.GET, f"{URL}/cow/definitions", json=definitions)
    responses.add(responses.GET, f"{URL}/cow/pronunciations", json=cow_pronunciations())
    await clazz.define(context, word="cow")
    embed = discord.Embed(title="cow")
    embed.add_field(name="noun: **cow**  /kou/", value="1. A big animal.\n_this is where I'd use cow in a sentence... IF I HAD ONE_\n", inline=False)
    embed.set_footer(text=ATTRIBUTION)
    context.send.assert_called_once_with(embed=embed)


def cow_definitions():
    ahd = {"sourceDictionary": "ahd-5", "attributionText": ATTRIBUTION, "word": "cow"}
    return [
        dict(ahd, partOfSpeech="noun", text="The mature female of cattle of the genus Bos.", exampleUses=[]),
        dict(ahd, partOfSpeech="noun", text="The mature female of certain other large animals, such as elephants, moose, or whales.", exampleUses=[]),
        dict(ahd, partOfSpeech="noun", exampleUses=[]),  # cross-reference entry with no text
        dict(ahd, partOfSpeech="transitive verb", text="To frighten or subdue with threats or a show of force.", exampleUses=[{"text": "the intellectuals had been cowed into silence"}]),
    ]


def cow_pronunciations():
    return [
        {"raw": "K AW1", "rawType": "arpabet"},
        {"raw": "/kaʊ/", "rawType": "IPA"},
        {"raw": "kou", "rawType": "ahd-5"},
    ]


def why_definitions():
    return [
        {
            "sourceDictionary": "wiktionary",
            "partOfSpeech": "adverb",
            "attributionText": "from Wiktionary, Creative Commons Attribution/Share-Alike License.",
            "text": "For what <xref>purpose</xref>, reason, or cause.",
            "word": "why",
            "exampleUses": [{"text": "<ex>why</ex> did he do it?"}],
        },
    ]
