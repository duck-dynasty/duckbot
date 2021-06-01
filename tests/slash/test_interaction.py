from unittest import mock

import pytest

from duckbot.slash import Interaction


@pytest.fixture
def dm_data():
    return {
        "id": "123",
        "application_id": "456",
        "token": "token!",
        "channel_id": "10",
        "user": "user",
        "data": "ALL OF IT",
    }


@pytest.fixture
def guild_data():
    return {
        "id": "123",
        "application_id": "456",
        "token": "token!",
        "channel_id": "10",
        "guild_id": "20",
        "member": "member",
        "data": "ALL OF IT",
    }


@pytest.fixture(params=["dm", "guild"])
def data(request, dm_data, guild_data):
    return dm_data if request.param == "dm" else guild_data


def test_id_getter(bot, data):
    assert Interaction(bot=bot, data=data).id == int(data["id"])


def test_application_id_getter(bot, data):
    assert Interaction(bot=bot, data=data).application_id == int(data["application_id"])


def test_token_getter(bot, data):
    assert Interaction(bot=bot, data=data).token == data["token"]


def test_channel_getter(bot, data, channel):
    bot.get_channel.return_value = channel
    assert Interaction(bot=bot, data=data).channel == channel
    bot.get_channel.assert_called_once_with(data["channel_id"])


def test_guild_getter_dm(bot, dm_data):
    assert Interaction(bot=bot, data=dm_data).guild is None
    bot.get_guild.assert_not_called()


def test_guild_getter_guild(bot, guild_data, guild):
    bot.get_guild.return_value = guild
    assert Interaction(bot=bot, data=guild_data).guild == guild
    bot.get_guild.assert_called_once_with(guild_data["guild_id"])


@mock.patch("discord.User")
def test_author_getter_dm(usr, bot, dm_data):
    assert Interaction(bot=bot, data=dm_data).author == usr.return_value
    usr.assert_called_once_with(data=dm_data["user"], state=bot._connection)


@mock.patch("discord.Member")
def test_author_getter_guild(memb, bot, guild_data, guild):
    bot.get_guild.return_value = guild
    assert Interaction(bot=bot, data=guild_data).author == memb.return_value
    bot.get_guild.assert_called_once_with(guild_data["guild_id"])
    memb.assert_called_once_with(data=guild_data["member"], state=bot._connection, guild=guild)


def test_data_getter(bot, data):
    assert Interaction(bot=bot, data=data).data == data["data"]


def test_equals_equal(bot, data):
    a = Interaction(bot=bot, data=data)
    b = Interaction(bot=bot, data=data)
    assert a == b


def test_equals_fields_different(bot, dm_data, guild_data):
    a = Interaction(bot=bot, data=dm_data)
    b = Interaction(bot=bot, data=guild_data)
    assert a != b


def test_equals_different_class(bot, data):
    a = Interaction(bot=bot, data=data)
    b = "str"
    assert a != b


def test_str_is_raw_data_str(bot, data):
    i = Interaction(bot=bot, data=data)
    assert str(i) == str(i.raw_data)


def test_repr_is_raw_data_str(bot, data):
    i = Interaction(bot=bot, data=data)
    assert repr(i) == str(i.raw_data)
