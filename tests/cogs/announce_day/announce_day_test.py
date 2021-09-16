import datetime
from unittest import mock

import pytest

from duckbot.cogs.announce_day import AnnounceDay
from tests.duckmock.datetime import patch_now


@pytest.fixture
@mock.patch("duckbot.cogs.dogs.DogPhotos")
def dog_photos(d):
    return d


@pytest.mark.asyncio
async def test_before_loop_waits_for_bot(bot, dog_photos):
    clazz = AnnounceDay(bot, dog_photos)
    await clazz.before_loop()
    bot.wait_until_ready.assert_called()


@pytest.mark.asyncio
async def test_cog_unload_cancels_task(bot, dog_photos):
    clazz = AnnounceDay(bot, dog_photos)
    clazz.cog_unload()
    clazz.on_hour_loop.cancel.assert_called()


@pytest.mark.asyncio
@mock.patch("random.random", return_value=0.5)
@mock.patch("random.choice", side_effect=["today", "tomorrow", "yesterday", "{today} {tomorrow} {yesterday}"])
async def test_on_hour_7am_eastern_special_day(random, choice, bot, dog_photos, general_channel):
    with patch_now(datetime.datetime(2002, 1, 1, hour=7)):
        clazz = AnnounceDay(bot, dog_photos)
        await clazz.on_hour()
        general_channel.send.assert_called_once_with("today tomorrow yesterday\nIt is also New Year's Day.")


@pytest.mark.asyncio
@mock.patch("random.random", return_value=0.5)
@mock.patch("random.choice", side_effect=["today", "tomorrow", "yesterday", "{today} {tomorrow} {yesterday}"])
async def test_on_hour_7am_eastern_not_special_day(random, choice, bot, dog_photos, general_channel):
    with patch_now(datetime.datetime(2002, 1, 21, hour=7)):
        clazz = AnnounceDay(bot, dog_photos)
        await clazz.on_hour()
        general_channel.send.assert_called_once_with("today tomorrow yesterday")


@pytest.mark.asyncio
@mock.patch("random.random", side_effect=[0.09, 0.1])
async def test_on_hour_7am_eastern_send_dog_photo(random, bot, dog_photos, general_channel):
    with patch_now(datetime.datetime(2002, 1, 21, hour=7)):
        clazz = AnnounceDay(bot, dog_photos)
        await clazz.on_hour()
        assert general_channel.send.call_count == 2
        dog_photos.get_dog_image.assert_called()


@pytest.mark.asyncio
@mock.patch("random.random", side_effect=[0.09, 0.1])
async def test_on_hour_7am_eastern_send_dog_photo_failure(random, bot, dog_photos, general_channel):
    dog_photos.get_dog_image.side_effect = RuntimeError("ded")
    with patch_now(datetime.datetime(2002, 1, 21, hour=7)):
        clazz = AnnounceDay(bot, dog_photos)
        await clazz.on_hour()
        general_channel.send.assert_called()
        dog_photos.get_dog_image.assert_called()


@pytest.mark.asyncio
@mock.patch("random.random", side_effect=[0.1, 0.09])
async def test_on_hour_7am_eastern_send_gif(random, bot, dog_photos, general_channel):
    with patch_now(datetime.datetime(2002, 1, 25, hour=7)):
        clazz = AnnounceDay(bot, dog_photos)
        await clazz.on_hour()
        assert general_channel.send.call_count == 2
        dog_photos.get_dog_image.assert_not_called()


@pytest.mark.asyncio
@mock.patch("duckbot.cogs.announce_day.announce_day.days")
@mock.patch("random.random", side_effect=[0.1, 0.09])
async def test_on_hour_7am_eastern_no_gifs_to_send(random, days, bot, dog_photos, general_channel):
    days.__getitem__.return_value = {"names": ["name"], "templates": [], "gifs": []}
    with patch_now(datetime.datetime(2002, 1, 25, hour=7)):
        clazz = AnnounceDay(bot, dog_photos)
        await clazz.on_hour()
        general_channel.send.assert_called_once()
        dog_photos.get_dog_image.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("hour", [h for h in range(0, 24) if h != 7])
async def test_on_hour_not_7am(bot, dog_photos, hour):
    with patch_now(datetime.datetime(2002, 1, 1, hour=hour)):
        clazz = AnnounceDay(bot, dog_photos)
        await clazz.on_hour()
        bot.get_all_channels.assert_not_called()
