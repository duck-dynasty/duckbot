import pytest
import mock
import os
from duckbot.util import Resources


@mock.patch("discord.ext.commands.Bot")
def test_get_resource_exists(bot):
    clazz = Resources(bot)
    path = clazz.get("bruh.mp3")
    expected = os.path.join(os.path.dirname(__file__), "..", "..", "resources", "bruh.mp3")
    assert os.path.abspath(expected) == path


@mock.patch("discord.ext.commands.Bot")
def test_get_resource_exists_path_join(bot):
    clazz = Resources(bot)
    path = clazz.get("tests", "test_resource")
    expected = os.path.join(os.path.dirname(__file__), "..", "..", "resources", "tests", "test_resource")
    assert os.path.abspath(expected) == path


@mock.patch("discord.ext.commands.Bot")
def test_get_resource_not_exists(bot):
    with pytest.raises(FileNotFoundError):
        Resources(bot).get("does not exist")
