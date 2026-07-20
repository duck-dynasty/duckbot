import datetime
from unittest import mock

import discord
import pytest
from discord import Forbidden
from discord.ext import commands

from duckbot.cogs.messages import FriendFacts
from duckbot.cogs.messages.friend_facts import UserStats
from tests.async_mock_ext import list_as_async_generator
from tests.discord_test_ext import bind_commands


@pytest.fixture
def clazz(bot) -> FriendFacts:
    return bind_commands(FriendFacts(bot))


def make_message(content="hi", author_id=1, is_bot=False, created_at=datetime.datetime(2026, 6, 15, 18, 30, tzinfo=datetime.timezone.utc), mentions=[], reference=None, attachments=[]):
    message = mock.Mock()
    message.author.id = author_id
    message.author.bot = is_bot
    message.content = content
    message.created_at = created_at
    message.mentions = mentions
    message.reference = reference
    message.interaction = None
    message.attachments = attachments
    return message


def make_user(user_id):
    user = mock.Mock()
    user.id = user_id
    return user


def make_reply_to(author_id):
    replied = mock.Mock(spec=discord.Message)
    replied.author.id = author_id
    reference = mock.Mock()
    reference.resolved = replied
    return reference


def readable(channel, messages):
    channel.permissions_for.return_value.read_message_history = True
    channel.history.return_value = list_as_async_generator(messages)
    return channel


async def test_before_loop_waits_for_bot(clazz, bot):
    await clazz.before_loop()
    bot.wait_until_ready.assert_called()


def test_cog_unload_cancels_task(clazz):
    clazz.cog_unload()
    clazz.friend_facts_loop.cancel.assert_called()


@mock.patch("duckbot.util.datetime.now", return_value=datetime.datetime(2026, 7, 1, hour=9))
async def test_on_month_start_first_of_month_sends_report(now, clazz, guild, general_channel):
    guild.text_channels = []
    await clazz.on_month_start()
    general_channel.send.assert_called_once()


@mock.patch("duckbot.util.datetime.now", return_value=datetime.datetime(2026, 7, 2, hour=9))
async def test_on_month_start_not_first_of_month_does_nothing(now, clazz, bot):
    await clazz.on_month_start()
    bot.get_all_channels.assert_not_called()


@mock.patch("duckbot.util.datetime.now", return_value=datetime.datetime(2026, 7, 1, hour=9))
async def test_friend_facts_command_sends_report_to_invoking_channel(now, clazz, guild, text_channel, context):
    guild.text_channels = []
    text_channel.guild = guild
    context.channel = text_channel
    await clazz.friend_facts(context)
    text_channel.send.assert_called_once()


async def test_friend_facts_command_is_rejected_outside_a_guild(clazz, context):
    context.guild = None
    with pytest.raises(commands.NoPrivateMessage):
        any(check(context) for check in clazz.friend_facts.checks)


@pytest.mark.parametrize(
    "today, expected_start, expected_end",
    [
        (datetime.datetime(2026, 7, 10, hour=13), datetime.datetime(2026, 6, 1), datetime.datetime(2026, 7, 1)),
        (datetime.datetime(2026, 1, 1, hour=9), datetime.datetime(2025, 12, 1), datetime.datetime(2026, 1, 1)),
        (datetime.datetime(2026, 3, 31, hour=23), datetime.datetime(2026, 2, 1), datetime.datetime(2026, 3, 1)),
    ],
)
@mock.patch("duckbot.util.datetime.now")
def test_prior_month_range(now, clazz, today, expected_start, expected_end):
    now.return_value = today
    start, end = clazz.prior_month_range()
    assert start == expected_start
    assert end == expected_end


async def test_gather_stats_streams_counters(clazz, guild, text_channel):
    guild.text_channels = [readable(text_channel, [make_message("Hello there friend"), make_message("are you ok?", author_id=2)])]
    stats, hours, days, channels = await clazz.gather_stats(guild, None, None)
    assert stats[1] == UserStats(messages=1, words=3, capital_starts=1)
    assert stats[2] == UserStats(messages=1, words=3, questions=1)
    assert sum(hours) == 2 and sum(days) == 2
    assert channels == 1


async def test_gather_stats_skips_bot_messages(clazz, guild, text_channel):
    guild.text_channels = [readable(text_channel, [make_message(is_bot=True)])]
    stats, _, _, _ = await clazz.gather_stats(guild, None, None)
    assert stats == {}


async def test_gather_stats_credits_slash_weather_to_invoker(clazz, guild, text_channel):
    invocation = make_message(is_bot=True)
    invocation.interaction = mock.Mock()
    invocation.interaction.name = "weather get"
    invocation.interaction.user.id = 5
    other = make_message(is_bot=True)
    other.interaction = mock.Mock()
    other.interaction.name = "market bet"
    guild.text_channels = [readable(text_channel, [invocation, other])]
    stats, _, _, _ = await clazz.gather_stats(guild, None, None)
    assert stats == {5: UserStats(weather=1)}


async def test_gather_stats_skips_unreadable_channels(clazz, guild, text_channel):
    text_channel.permissions_for.return_value.read_message_history = False
    guild.text_channels = [text_channel]
    stats, _, _, channels = await clazz.gather_stats(guild, None, None)
    assert stats == {} and channels == 0
    text_channel.history.assert_not_called()


async def test_gather_stats_skips_forbidden_channels(clazz, guild, text_channel):
    text_channel.permissions_for.return_value.read_message_history = True
    text_channel.history.side_effect = Forbidden(mock.Mock(status=403), "no")
    guild.text_channels = [text_channel]
    stats, _, _, channels = await clazz.gather_stats(guild, None, None)
    assert stats == {} and channels == 0


async def test_gather_stats_scans_active_and_archived_threads(clazz, guild, text_channel, thread):
    active_thread = readable(thread, [make_message("from an active thread", author_id=2)])
    active_thread.type = discord.ChannelType.public_thread
    text_channel.threads = [active_thread]

    archived_thread = readable(mock.Mock(spec=discord.Thread), [make_message("from an archived thread", author_id=3)])
    text_channel.archived_threads.return_value = list_as_async_generator([archived_thread])

    text_channel.history.return_value = list_as_async_generator([make_message("in the channel itself")])
    text_channel.permissions_for.return_value.read_message_history = True
    guild.text_channels = [text_channel]

    stats, _, _, channels = await clazz.gather_stats(guild, None, None)
    assert stats.keys() == {1, 2, 3}
    assert channels == 3


async def test_gather_stats_skips_forbidden_archived_threads(clazz, guild, text_channel):
    text_channel.permissions_for.return_value.read_message_history = True
    text_channel.history.return_value = list_as_async_generator([])
    text_channel.threads = []
    text_channel.archived_threads.side_effect = Forbidden(mock.Mock(status=403), "no")
    guild.text_channels = [text_channel]
    stats, _, _, channels = await clazz.gather_stats(guild, None, None)
    assert stats == {} and channels == 1


def test_tally_counts_each_stat(clazz):
    stats, hours, days = {}, [0] * 24, [0] * 7
    clazz.tally(stats, hours, days, make_message("Hello world"))
    clazz.tally(stats, hours, days, make_message("what? "))
    clazz.tally(stats, hours, days, make_message("AAAH!"))
    clazz.tally(stats, hours, days, make_message("see https://example.com"))
    assert stats[1] == UserStats(messages=4, words=6, capital_starts=2, questions=1, shouts=1, links=1)


def test_tally_counts_golf_mentions_case_insensitive(clazz):
    stats, hours, days = {}, [0] * 24, [0] * 7
    clazz.tally(stats, hours, days, make_message("GOLF golf golfing, hole in one"))
    clazz.tally(stats, hours, days, make_message("GULF gulf engulfed"))
    assert stats[1].golf == 6


def test_tally_counts_weather_prefix_command(clazz):
    stats, hours, days = {}, [0] * 24, [0] * 7
    clazz.tally(stats, hours, days, make_message("!weather set london ca 2"))
    clazz.tally(stats, hours, days, make_message("nice weather today"))
    assert stats[1].weather == 1


def test_tally_counts_attachments(clazz):
    stats, hours, days = {}, [0] * 24, [0] * 7
    clazz.tally(stats, hours, days, make_message("look at these", attachments=[mock.Mock(), mock.Mock()]))
    clazz.tally(stats, hours, days, make_message("no photos here"))
    assert stats[1].attachments == 2


def test_tally_counts_mentions_and_replies_distinctly(clazz):
    stats, hours, days = {}, [0] * 24, [0] * 7
    clazz.tally(stats, hours, days, make_message("hi", mentions=[make_user(2), make_user(3)]))
    clazz.tally(stats, hours, days, make_message("hi", reference=make_reply_to(2)))
    clazz.tally(stats, hours, days, make_message("hi", mentions=[make_user(2)], reference=make_reply_to(2)))  # reply ping counts once
    assert stats[1].mentions == 4


def test_tally_mentions_excludes_self_and_deleted_replies(clazz):
    stats, hours, days = {}, [0] * 24, [0] * 7
    deleted = mock.Mock()
    deleted.resolved = mock.Mock(spec=discord.DeletedReferencedMessage)
    clazz.tally(stats, hours, days, make_message("hi", mentions=[make_user(1)]))
    clazz.tally(stats, hours, days, make_message("hi", reference=make_reply_to(1)))
    clazz.tally(stats, hours, days, make_message("hi", reference=deleted))
    assert stats[1].mentions == 0


def test_tally_buckets_hours_and_days_in_eastern_time(clazz):
    stats, hours, days = {}, [0] * 24, [0] * 7
    clazz.tally(stats, hours, days, make_message(created_at=datetime.datetime(2026, 6, 15, 18, 30, tzinfo=datetime.timezone.utc)))  # 2:30pm EDT, a Monday
    assert hours[14] == 1
    assert days[0] == 1


@mock.patch("duckbot.cogs.messages.friend_facts.get_user")
async def test_format_report_empty_month(get_user, clazz, guild):
    report = await clazz.format_report(guild, {}, [0] * 24, [0] * 7, 0, datetime.datetime(2026, 6, 1))
    assert report == "**Friend Facts: June 2026** :bar_chart:\nNobody said anything last month. :duck:"


@mock.patch("duckbot.cogs.messages.friend_facts.get_user")
async def test_format_report_leaderboard_and_awards(get_user, clazz, guild):
    get_user.side_effect = lambda bot, user_id, guild: mock.Mock(display_name=f"user{user_id}")
    stats = {
        1: UserStats(messages=50, words=100, capital_starts=40, questions=5, shouts=3, links=7, golf=12, attachments=33),
        2: UserStats(messages=30, words=300, capital_starts=6, questions=15, weather=9, mentions=21),
    }
    hours = [0] * 24
    hours[23] = 42
    days = [0] * 7
    days[5] = 42
    report = await clazz.format_report(guild, stats, hours, days, 4, datetime.datetime(2026, 6, 1))
    assert "**Friend Facts: June 2026**" in report
    assert report.index("user1 ") < report.index("user2 ")
    assert ":pencil: 80 messages across 4 channels" in report
    assert "Grammar Police: user1 — 80% of messages start with a capital" in report
    assert "Wordiest: user2 — 10.0 words per message" in report
    assert "Most Inquisitive: user2 — 50% of messages are questions" in report
    assert "Loudest: user1 — 3 ALL-CAPS messages" in report
    assert "Chief Link Dumper: user1 — 7 links shared" in report
    assert "Golf Fanatic: user1 — 12 golf mentions" in report
    assert "Weather Obsessed: user2 — 9 weather checks" in report
    assert "Name Dropper: user2 — 21 people mentioned" in report
    assert "Paparazzi: user1 — 33 attachments sent" in report
    assert "Busiest hour: 11pm · Busiest day: Saturday" in report


@mock.patch("duckbot.cogs.messages.friend_facts.get_user")
async def test_format_report_truncates_leaderboard_to_top_ten(get_user, clazz, guild):
    get_user.side_effect = lambda bot, user_id, guild: mock.Mock(display_name=f"user{user_id}")
    stats = {i: UserStats(messages=100 - i) for i in range(1, 12)}
    report = await clazz.format_report(guild, stats, [0] * 24, [0] * 7, 1, datetime.datetime(2026, 6, 1))
    assert "user10 " in report
    assert "user11 " not in report


@mock.patch("duckbot.cogs.messages.friend_facts.get_user")
async def test_format_report_truncates_long_names_in_leaderboard(get_user, clazz, guild):
    get_user.side_effect = lambda bot, user_id, guild: mock.Mock(display_name="a" * 32)
    report = await clazz.format_report(guild, {1: UserStats(messages=5)}, [0] * 24, [0] * 7, 1, datetime.datetime(2026, 6, 1))
    assert "a" * 24 + " " in report
    assert "a" * 25 not in report


@mock.patch("duckbot.cogs.messages.friend_facts.get_user")
async def test_format_report_awards_require_minimum_messages(get_user, clazz, guild):
    get_user.side_effect = lambda bot, user_id, guild: mock.Mock(display_name=f"user{user_id}")
    stats = {1: UserStats(messages=1, words=50, capital_starts=1, questions=1), 2: UserStats(messages=25, words=25, capital_starts=5, questions=5)}
    report = await clazz.format_report(guild, stats, [0] * 24, [0] * 7, 1, datetime.datetime(2026, 6, 1))
    assert "Grammar Police: user2" in report
    assert "Wordiest: user2" in report
    assert "Most Inquisitive: user2" in report


@mock.patch("duckbot.cogs.messages.friend_facts.get_user")
async def test_format_report_no_awards_for_zero_counts(get_user, clazz, guild):
    get_user.side_effect = lambda bot, user_id, guild: mock.Mock(display_name=f"user{user_id}")
    stats = {1: UserStats(messages=5, words=10)}
    report = await clazz.format_report(guild, stats, [0] * 24, [0] * 7, 1, datetime.datetime(2026, 6, 1))
    assert "Loudest" not in report
    assert "Chief Link Dumper" not in report
    assert "Golf Fanatic" not in report
    assert "Weather Obsessed" not in report
    assert "Name Dropper" not in report
    assert "Paparazzi" not in report


@mock.patch("duckbot.cogs.messages.friend_facts.get_user", return_value=None)
async def test_display_name_unknown_user(get_user, clazz, guild):
    assert await clazz.display_name(guild, 123) == "User-123"


@mock.patch("duckbot.util.datetime.now", return_value=datetime.datetime(2026, 7, 10, hour=13))
async def test_send_report_posts_to_channel(now, clazz, guild, general_channel):
    guild.text_channels = [readable(general_channel, [make_message("Hello")])]
    with mock.patch("duckbot.cogs.messages.friend_facts.get_user", side_effect=lambda bot, user_id, g: mock.Mock(display_name=f"user{user_id}")):
        await clazz.send_report(general_channel)
    general_channel.send.assert_called_once()
    report = general_channel.send.call_args.args[0]
    assert "**Friend Facts: June 2026**" in report
    assert "user1 " in report
