import datetime
from unittest import mock

from duckbot.cogs.messages.touch_grass import TouchGrass

MONDAY_NOON = datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)  # Mon, work hours
SATURDAY_NOON = datetime.datetime(2024, 1, 6, 12, 0, 0, tzinfo=datetime.timezone.utc)  # Sat, off hours


@mock.patch("duckbot.cogs.messages.touch_grass.utcnow")
async def test_bot_messages_are_ignored(mock_utcnow, bot, message):
    """Bot's own messages should not be tracked."""
    message.author = bot.user
    base_time = datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
    mock_utcnow.return_value = base_time

    clazz = TouchGrass(bot)
    await clazz.on_message_activity(message)

    # Should not have tracked anything
    assert len(clazz.activity) == 0
    message.channel.send.assert_not_called()


@mock.patch("duckbot.cogs.messages.touch_grass.utcnow")
async def test_tracks_user_messages(mock_utcnow, bot, message):
    """User messages should be tracked with timestamps."""
    base_time = datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
    mock_utcnow.return_value = base_time

    clazz = TouchGrass(bot)
    await clazz.track_activity(message)
    await clazz.track_activity(message)
    await clazz.track_activity(message)

    # Should have tracked 3 messages
    assert len(clazz.activity[message.author.id]["messages"]) == 3
    assert all(ts == base_time for ts in clazz.activity[message.author.id]["messages"])


@mock.patch("duckbot.cogs.messages.touch_grass.utcnow")
async def test_threshold_not_reached_no_notification(mock_utcnow, bot, message):
    """Sending 39 messages should not trigger notification."""
    base_time = datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
    mock_utcnow.return_value = base_time

    clazz = TouchGrass(bot)

    # Send 39 messages
    for i in range(39):
        mock_utcnow.return_value = base_time + datetime.timedelta(seconds=i * 90)
        await clazz.track_activity(message)

    # Should not have notified
    message.channel.send.assert_not_called()


@mock.patch("duckbot.cogs.messages.touch_grass.utcnow")
async def test_threshold_reached_sends_notification(mock_utcnow, bot, message):
    """Sending 40 messages should trigger notification."""
    base_time = datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
    mock_utcnow.return_value = base_time
    message.author.display_name = "TestUser"

    clazz = TouchGrass(bot)

    # Send 40 messages
    for i in range(40):
        mock_utcnow.return_value = base_time + datetime.timedelta(seconds=i * 88)
        await clazz.track_activity(message)

    # Should have notified exactly once
    assert message.channel.send.call_count == 1
    # Verify message contains count
    call_args = message.channel.send.call_args[0][0]
    assert "40" in call_args
    assert "TestUser" in call_args


@mock.patch("duckbot.cogs.messages.touch_grass.utcnow")
async def test_cooldown_prevents_duplicate_notifications(mock_utcnow, bot, message):
    """Cooldown should prevent multiple notifications within 1 hour."""
    base_time = datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
    mock_utcnow.return_value = base_time

    clazz = TouchGrass(bot)

    # Send 40 messages to trigger first notification
    for i in range(40):
        mock_utcnow.return_value = base_time + datetime.timedelta(seconds=i * 88)
        await clazz.track_activity(message)

    # 30 minutes later, send more messages (still within cooldown)
    mock_utcnow.return_value = base_time + datetime.timedelta(minutes=30)
    for i in range(20):
        await clazz.track_activity(message)

    # Should only have notified once (cooldown active)
    assert message.channel.send.call_count == 1


@mock.patch("duckbot.cogs.messages.touch_grass.utcnow")
async def test_cooldown_expires_allows_new_notification(mock_utcnow, bot, message):
    """After 1 hour cooldown, should be able to notify again."""
    base_time = datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
    mock_utcnow.return_value = base_time

    clazz = TouchGrass(bot)

    # Send 40 messages at T=0 to trigger first notification
    for i in range(40):
        await clazz.track_activity(message)

    # 121 minutes later (cooldown expired and all old messages cleaned up)
    mock_utcnow.return_value = base_time + datetime.timedelta(minutes=121)

    # Send another 40 messages
    for i in range(40):
        await clazz.track_activity(message)

    # Should have notified twice
    assert message.channel.send.call_count == 2


@mock.patch("duckbot.cogs.messages.touch_grass.utcnow")
async def test_sliding_window_removes_old_messages(mock_utcnow, bot, message):
    """Messages older than 60 minutes should be removed from tracking."""
    base_time = datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
    mock_utcnow.return_value = base_time

    clazz = TouchGrass(bot)

    # Send 20 messages at T=0
    for i in range(20):
        await clazz.track_activity(message)

    # 61 minutes later (outside window)
    mock_utcnow.return_value = base_time + datetime.timedelta(minutes=61)
    await clazz.track_activity(message)

    # Old messages should be cleaned up, only 1 message in window
    assert len(clazz.activity[message.author.id]["messages"]) == 1
    # Should not have triggered notification (only 1 message in window)
    message.channel.send.assert_not_called()


@mock.patch("duckbot.cogs.messages.touch_grass.utcnow")
async def test_multiple_users_tracked_separately(mock_utcnow, bot, message):
    """Different users should have separate tracking."""
    base_time = datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
    mock_utcnow.return_value = base_time

    clazz = TouchGrass(bot)

    # User 1 sends 40 messages
    message.author.id = 12345
    for i in range(40):
        await clazz.track_activity(message)

    # User 2 sends 5 messages
    message.author.id = 67890
    for i in range(5):
        await clazz.track_activity(message)

    # User 1 should have 40 messages tracked
    assert len(clazz.activity[12345]["messages"]) == 40
    # User 2 should have 5 messages tracked
    assert len(clazz.activity[67890]["messages"]) == 5
    # Only user 1 should have been notified
    assert message.channel.send.call_count == 1


@mock.patch("duckbot.cogs.messages.touch_grass.utcnow")
async def test_clean_old_messages_preserves_recent(mock_utcnow, bot, message):
    """Cleanup should only remove old messages, not recent ones."""
    base_time = datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
    mock_utcnow.return_value = base_time

    clazz = TouchGrass(bot)

    # Send 20 messages at T=0
    for i in range(20):
        await clazz.track_activity(message)

    # Send 20 messages at T=30min
    mock_utcnow.return_value = base_time + datetime.timedelta(minutes=30)
    for i in range(20):
        await clazz.track_activity(message)

    # At T=61min, clean up
    mock_utcnow.return_value = base_time + datetime.timedelta(minutes=61)
    await clazz.track_activity(message)

    # Should only have messages from T=30min and T=61min (21 total)
    assert len(clazz.activity[message.author.id]["messages"]) == 21


@mock.patch("duckbot.cogs.messages.touch_grass.utcnow")
async def test_should_notify_returns_true_for_new_user(mock_utcnow, bot, message):
    """First notification for a user should be allowed."""
    base_time = datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
    mock_utcnow.return_value = base_time

    clazz = TouchGrass(bot)
    clazz.activity[message.author.id] = {"messages": [], "last_notification": None}

    assert clazz.should_notify(message.author.id, base_time) is True


@mock.patch("duckbot.cogs.messages.touch_grass.utcnow")
async def test_should_notify_returns_false_within_cooldown(mock_utcnow, bot, message):
    """Notification within cooldown period should be blocked."""
    base_time = datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
    last_notification = base_time - datetime.timedelta(minutes=30)

    clazz = TouchGrass(bot)
    clazz.activity[message.author.id] = {"messages": [], "last_notification": last_notification}

    assert clazz.should_notify(message.author.id, base_time) is False


@mock.patch("duckbot.cogs.messages.touch_grass.utcnow")
async def test_should_notify_returns_true_after_cooldown(mock_utcnow, bot, message):
    """Notification after cooldown expires should be allowed."""
    base_time = datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
    last_notification = base_time - datetime.timedelta(hours=1, minutes=1)

    clazz = TouchGrass(bot)
    clazz.activity[message.author.id] = {"messages": [], "last_notification": last_notification}

    assert clazz.should_notify(message.author.id, base_time) is True


@mock.patch("random.choice")
@mock.patch("duckbot.cogs.messages.touch_grass.utcnow")
async def test_send_notification_uses_random_grass_phrase_off_hours(mock_utcnow, mock_random, bot, message):
    """Off-hours notification should select from touch grass phrases."""
    mock_random.return_value = "Test message with {name} and {count}"
    mock_utcnow.return_value = SATURDAY_NOON
    message.author.display_name = "TestUser"

    clazz = TouchGrass(bot)
    await clazz.send_notification(message, 42, work_hours=False)

    message.channel.send.assert_called_once()
    call_args = message.channel.send.call_args[0][0]
    assert "TestUser" in call_args
    assert "42" in call_args


@mock.patch("random.choice")
@mock.patch("duckbot.cogs.messages.touch_grass.utcnow")
async def test_send_notification_uses_work_phrase_during_work_hours(mock_utcnow, mock_random, bot, message):
    """Work-hours notification should select from work phrases."""
    mock_random.return_value = "Get back to work {name}! {count} messages."
    mock_utcnow.return_value = MONDAY_NOON
    message.author.display_name = "TestUser"

    clazz = TouchGrass(bot)
    await clazz.send_notification(message, 42, work_hours=True)

    from duckbot.cogs.messages.touch_grass_phrases import work_phrases

    mock_random.assert_called_once_with(work_phrases)
    call_args = message.channel.send.call_args[0][0]
    assert "TestUser" in call_args
    assert "42" in call_args


@mock.patch("duckbot.cogs.messages.touch_grass.utcnow")
async def test_show_activity_stats_no_activity(mock_utcnow, bot, context):
    """Stats command shows message when no recent activity."""
    base_time = datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
    mock_utcnow.return_value = base_time

    clazz = TouchGrass(bot)
    await clazz.show_activity_stats(context)

    context.send.assert_called_once_with("https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExMmU1Mm0wZ2UxMW45MjR0M3I0dzVpaDVkajRpNDRyc2txd2xnZW13dSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3OzmcOUXM3Kw0/giphy.gif")


@mock.patch("duckbot.cogs.messages.touch_grass.utcnow")
async def test_show_activity_stats_with_activity(mock_utcnow, bot, context, message, guild):
    """Stats command shows leaderboard with user activity."""
    base_time = datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
    mock_utcnow.return_value = base_time

    clazz = TouchGrass(bot)

    # Simulate activity for two users
    message.author.id = 123
    for i in range(5):
        await clazz.track_activity(message)

    message.author.id = 456
    for i in range(10):
        await clazz.track_activity(message)

    # Setup guild
    context.guild = guild

    def get_member_side_effect(user_id):
        member = mock.Mock()
        if user_id == 123:
            member.display_name = "User1"
        elif user_id == 456:
            member.display_name = "User2"
        else:
            return None
        return member

    guild.get_member.side_effect = get_member_side_effect

    await clazz.show_activity_stats(context)

    context.send.assert_called_once()
    call_args = context.send.call_args[0][0]
    assert "Activity Leaderboard" in call_args
    assert "User1" in call_args or "User2" in call_args
    assert "5" in call_args
    assert "10" in call_args


@mock.patch("duckbot.cogs.messages.touch_grass.utcnow")
async def test_show_activity_stats_sorts_by_count(mock_utcnow, bot, context, message, guild):
    """Stats command sorts users by message count descending."""
    base_time = datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
    mock_utcnow.return_value = base_time

    clazz = TouchGrass(bot)

    # User 1: 3 messages
    message.author.id = 111
    for i in range(3):
        await clazz.track_activity(message)

    # User 2: 10 messages (most active)
    message.author.id = 222
    for i in range(10):
        await clazz.track_activity(message)

    # User 3: 5 messages
    message.author.id = 333
    for i in range(5):
        await clazz.track_activity(message)

    # Setup guild
    context.guild = guild

    def get_member_side_effect(user_id):
        member = mock.Mock()
        if user_id == 111:
            member.display_name = "UserA"
        elif user_id == 222:
            member.display_name = "UserB"
        elif user_id == 333:
            member.display_name = "UserC"
        return member

    guild.get_member.side_effect = get_member_side_effect

    await clazz.show_activity_stats(context)

    call_args = context.send.call_args[0][0]
    # UserB (10 messages) should appear before UserC (5) and UserA (3)
    user_b_pos = call_args.find("UserB")
    user_c_pos = call_args.find("UserC")
    user_a_pos = call_args.find("UserA")

    assert user_b_pos < user_c_pos < user_a_pos


@mock.patch("duckbot.cogs.messages.touch_grass.utcnow")
async def test_show_activity_stats_excludes_old_messages(mock_utcnow, bot, context, message):
    """Stats command only shows messages within 60-minute window."""
    base_time = datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
    mock_utcnow.return_value = base_time

    clazz = TouchGrass(bot)

    # Send 10 messages at T=0
    message.author.id = 123
    for i in range(10):
        await clazz.track_activity(message)

    # Jump to 61 minutes later (old messages outside window)
    mock_utcnow.return_value = base_time + datetime.timedelta(minutes=61)

    await clazz.show_activity_stats(context)

    # Should show no activity since all messages are too old
    context.send.assert_called_once_with("https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExMmU1Mm0wZ2UxMW45MjR0M3I0dzVpaDVkajRpNDRyc2txd2xnZW13dSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3OzmcOUXM3Kw0/giphy.gif")


@mock.patch("duckbot.cogs.messages.touch_grass.utcnow")
async def test_show_activity_stats_no_guild(mock_utcnow, bot, context, message):
    """Stats command resolves names via bot cache when guild is unavailable."""
    base_time = datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
    mock_utcnow.return_value = base_time

    clazz = TouchGrass(bot)

    message.author.id = 123
    for i in range(5):
        await clazz.track_activity(message)

    context.guild = None
    user = mock.Mock()
    user.display_name = "CachedUser"
    bot.get_user.return_value = user

    await clazz.show_activity_stats(context)

    call_args = context.send.call_args[0][0]
    assert "CachedUser" in call_args
    assert "5" in call_args


@mock.patch("duckbot.cogs.messages.touch_grass.utcnow")
async def test_show_activity_stats_member_not_in_guild(mock_utcnow, bot, context, message, guild):
    """Stats command falls back to bot cache when member is not in guild."""
    base_time = datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
    mock_utcnow.return_value = base_time

    clazz = TouchGrass(bot)

    message.author.id = 999
    for i in range(5):
        await clazz.track_activity(message)

    context.guild = guild
    guild.get_member.return_value = None
    user = mock.Mock()
    user.display_name = "FallbackUser"
    bot.get_user.return_value = user

    await clazz.show_activity_stats(context)

    call_args = context.send.call_args[0][0]
    assert "FallbackUser" in call_args
    assert "5" in call_args


@mock.patch("duckbot.cogs.messages.touch_grass.utcnow")
async def test_show_activity_stats_unknown_user(mock_utcnow, bot, context, message, guild):
    """Stats command shows User-{id} when user is not in guild or bot cache."""
    base_time = datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
    mock_utcnow.return_value = base_time

    clazz = TouchGrass(bot)

    message.author.id = 999
    for i in range(5):
        await clazz.track_activity(message)

    context.guild = guild
    guild.get_member.return_value = None
    bot.get_user.return_value = None

    await clazz.show_activity_stats(context)

    call_args = context.send.call_args[0][0]
    assert "User-999" in call_args
    assert "5" in call_args


async def test_is_work_hours_weekday_within_hours(bot):
    """Mon-Fri 8am-6pm EDT (12pm-10pm UTC) should be work hours."""
    clazz = TouchGrass(bot)
    # Monday 12:00 UTC
    assert clazz.is_work_hours(MONDAY_NOON) is True
    # Monday 12:00 UTC (boundary start)
    assert clazz.is_work_hours(datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)) is True
    # Monday 21:59 UTC (boundary end)
    assert clazz.is_work_hours(datetime.datetime(2024, 1, 1, 21, 59, 0, tzinfo=datetime.timezone.utc)) is True


async def test_is_work_hours_weekday_outside_hours(bot):
    """Before 12pm and at/after 10pm UTC on weekdays should not be work hours."""
    clazz = TouchGrass(bot)
    # Monday 11:59 UTC
    assert clazz.is_work_hours(datetime.datetime(2024, 1, 1, 11, 59, 0, tzinfo=datetime.timezone.utc)) is False
    # Monday 22:00 UTC
    assert clazz.is_work_hours(datetime.datetime(2024, 1, 1, 22, 0, 0, tzinfo=datetime.timezone.utc)) is False
    # Monday 23:00 UTC
    assert clazz.is_work_hours(datetime.datetime(2024, 1, 1, 23, 0, 0, tzinfo=datetime.timezone.utc)) is False


async def test_is_work_hours_weekend(bot):
    """Weekends should not be work hours regardless of time."""
    clazz = TouchGrass(bot)
    # Saturday 12:00 UTC
    assert clazz.is_work_hours(SATURDAY_NOON) is False
    # Sunday 12:00 UTC
    assert clazz.is_work_hours(datetime.datetime(2024, 1, 7, 12, 0, 0, tzinfo=datetime.timezone.utc)) is False


@mock.patch("duckbot.cogs.messages.touch_grass.utcnow")
async def test_off_hours_threshold_119_no_notification(mock_utcnow, bot, message):
    """119 messages outside work hours should not trigger notification."""
    mock_utcnow.return_value = SATURDAY_NOON

    clazz = TouchGrass(bot)

    for i in range(119):
        mock_utcnow.return_value = SATURDAY_NOON + datetime.timedelta(seconds=i * 30)
        await clazz.track_activity(message)

    message.channel.send.assert_not_called()


@mock.patch("duckbot.cogs.messages.touch_grass.utcnow")
async def test_off_hours_threshold_120_sends_notification(mock_utcnow, bot, message):
    """120 messages outside work hours should trigger notification."""
    mock_utcnow.return_value = SATURDAY_NOON
    message.author.display_name = "TestUser"

    clazz = TouchGrass(bot)

    for i in range(120):
        mock_utcnow.return_value = SATURDAY_NOON + datetime.timedelta(seconds=i * 30)
        await clazz.track_activity(message)

    assert message.channel.send.call_count == 1


@mock.patch("duckbot.cogs.messages.touch_grass.utcnow")
async def test_off_hours_40_messages_no_notification(mock_utcnow, bot, message):
    """40 messages outside work hours should not trigger (threshold is 120)."""
    mock_utcnow.return_value = SATURDAY_NOON

    clazz = TouchGrass(bot)

    for i in range(40):
        await clazz.track_activity(message)

    message.channel.send.assert_not_called()


@mock.patch("duckbot.cogs.messages.touch_grass.utcnow")
async def test_leaderboard_unaffected_by_time_of_day(mock_utcnow, bot, context, message, guild):
    """Leaderboard should show all activity regardless of work hours or thresholds."""
    mock_utcnow.return_value = SATURDAY_NOON

    clazz = TouchGrass(bot)

    # Send 10 messages on a Saturday (well below 120 threshold)
    message.author.id = 123
    for i in range(10):
        await clazz.track_activity(message)

    context.guild = guild
    member = mock.Mock()
    member.display_name = "WeekendUser"
    guild.get_member.return_value = member

    await clazz.show_activity_stats(context)

    call_args = context.send.call_args[0][0]
    assert "Activity Leaderboard" in call_args
    assert "WeekendUser" in call_args
    assert "10" in call_args
