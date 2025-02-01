from unittest import mock

from duckbot.cogs.tito import Tito


async def test_react_to_tito_with_yugoslavia_no_tito_emoji(bot, message):
    message.content = "josip bro tito, brother"
    clazz = Tito(bot)
    await clazz.react_to_tito_with_yugoslavia(message)
    message.add_reaction.assert_not_called()


async def test_react_to_tito_with_yugoslavia_message_contains_tito_text(bot, message):
    message.content = "josip bro :tito:, brother"
    clazz = Tito(bot)
    await clazz.react_to_tito_with_yugoslavia(message)
    assert_flags_sent(message)


async def test_react_to_tito_with_yugoslavia_message_contains_tito_emoji(bot, message):
    message.content = "josip bro <:tito:780954015285641276>, brother"
    clazz = Tito(bot)
    await clazz.react_to_tito_with_yugoslavia(message)
    assert_flags_sent(message)


@mock.patch("discord.RawReactionActionEvent")
async def test_react_to_tito_reaction_no_tito_emoji(payload, bot):
    payload.emoji.name = "not-tito"
    clazz = Tito(bot)
    await clazz.react_to_tito_reaction(payload)
    bot.fetch_channel.assert_not_called()


@mock.patch("discord.RawReactionActionEvent")
async def test_react_to_tito_reaction_tito_emoji(payload, bot, channel, message):
    payload.channel_id = 123
    payload.message_id = 456
    payload.emoji.name = "tito"
    bot.fetch_channel.return_value = channel
    channel.fetch_message.return_value = message
    clazz = Tito(bot)
    await clazz.react_to_tito_reaction(payload)
    bot.fetch_channel.assert_called_once_with(payload.channel_id)
    channel.fetch_message.assert_called_once_with(payload.message_id)
    assert_flags_sent(message)


def assert_flags_sent(message):
    calls = [
        mock.call("\U0001f1e7\U0001f1e6"),
        mock.call("\U0001f1ed\U0001f1f7"),
        mock.call("\U0001f1fd\U0001f1f0"),
        mock.call("\U0001f1f2\U0001f1ea"),
        mock.call("\U0001f1f2\U0001f1f0"),
        mock.call("\U0001f1f7\U0001f1f8"),
        mock.call("\U0001f1f8\U0001f1ee"),
    ]
    message.add_reaction.assert_has_calls(calls, any_order=True)
