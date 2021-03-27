import pytest
import mock
import os
from duckbot.util import Resources


@mock.patch("discord.ext.commands.Bot")
@mock.patch("os.path.exists", return_value=True)
def test_get_resource_exists(bot, exists):
    clazz = Resources(bot)
    path = clazz.get("name")
    expected = os.path.join(os.path.dirname(__file__), "..", "..", "resources", "name")
    assert os.path.abspath(expected) == path


@mock.patch("discord.ext.commands.Bot")
@mock.patch("os.path.exists", return_value=True)
def test_get_resource_exists_path_join(bot, exists):
    clazz = Resources(bot)
    path = clazz.get("dir", "file")
    expected = os.path.join(os.path.dirname(__file__), "..", "..", "resources", "dir", "file")
    assert os.path.abspath(expected) == path


@mock.patch("discord.ext.commands.Bot")
@mock.patch("os.path.exists", return_value=False)
def test_get_resource_not_exists(bot, exists):
    with pytest.raises(FileNotFoundError):
        Resources(bot).get("does not exist")
