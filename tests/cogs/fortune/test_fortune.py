import mock
from subprocess import CompletedProcess
from duckbot.cogs.fortune import Fortune


@mock.patch("subprocess.run")
def test_get_fortune_short(run, bot):
    run.return_value = CompletedProcess([], 0, b"fortune")
    clazz = Fortune(bot)
    message = clazz.get_fortune()
    assert message == "```fortune```"


@mock.patch("subprocess.run")
def test_get_fortune_first_is_long(run, bot):
    long_message = "f" * 1951
    short_message = "f"
    run.side_effect = [CompletedProcess([], 0, long_message.encode()), CompletedProcess([], 0, short_message.encode())]
    clazz = Fortune(bot)
    message = clazz.get_fortune()
    assert message == "```f```"
