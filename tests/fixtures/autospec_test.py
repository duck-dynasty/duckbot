import discord
import pytest


def test_mock_is_instance_of_spec(autospec):
    message = autospec.of(discord.Message)
    assert isinstance(message, discord.Message)


def test_nonexistent_attribute_raises(autospec):
    message = autospec.of(discord.Message)
    with pytest.raises(AttributeError):
        message.no_such_attribute


def test_nonexistent_method_call_raises(autospec):
    message = autospec.of(discord.Message)
    with pytest.raises(AttributeError):
        message.no_such_method()


def test_sync_method_wrong_signature_raises(autospec):
    embed = autospec.of(discord.Embed)
    with pytest.raises(TypeError):
        embed.add_field()  # requires name and value


def test_sync_method_valid_call(autospec):
    embed = autospec.of(discord.Embed)
    embed.add_field(name="n", value="v")
    embed.add_field.assert_called_once_with(name="n", value="v")


async def test_async_method_wrong_signature_raises(autospec):
    message = autospec.of(discord.Message)
    with pytest.raises(TypeError):
        await message.add_reaction()  # requires emoji


async def test_async_method_valid_call(autospec):
    message = autospec.of(discord.Message)
    await message.add_reaction("emoji")
    message.add_reaction.assert_awaited_once_with("emoji")


def test_method_return_value_is_configurable(autospec):
    embed = autospec.of(discord.Embed)
    embed.add_field.return_value = "stub"
    assert embed.add_field(name="n", value="v") == "stub"


def test_no_state_bleed_between_mocks_of_same_class(autospec):
    first = autospec.of(discord.Message)
    second = autospec.of(discord.Message)
    assert first is not second
    first.id = 123
    await_none = first.add_reaction("emoji")
    await_none.close()  # suppress un-awaited warning
    assert second.id != 123
    second.add_reaction.assert_not_called()


def test_no_return_value_bleed_between_mocks_of_same_class(autospec):
    first = autospec.of(discord.Embed)
    first.add_field.return_value = "stub"
    second = autospec.of(discord.Embed)
    assert second.add_field(name="n", value="v") != "stub"


def test_mock_equality_is_identity(autospec):
    first = autospec.of(discord.Emoji)
    second = autospec.of(discord.Emoji)
    assert first == first
    assert first != second
