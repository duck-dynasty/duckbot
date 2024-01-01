import datetime
from unittest import mock

import pytest

from duckbot.cogs.announce_day import AnnounceDay


@pytest.fixture
@mock.patch("duckbot.cogs.dogs.DogPhotos")
def dog_photos(d):
    return d


async def test_before_loop_waits_for_bot(bot, dog_photos):
    clazz = AnnounceDay(bot, dog_photos)
    await clazz.before_loop()
    bot.wait_until_ready.assert_called()


def test_cog_unload_cancels_task(bot, dog_photos):
    clazz = AnnounceDay(bot, dog_photos)
    clazz.cog_unload()
    clazz.on_hour_loop.cancel.assert_called()


@mock.patch("random.choice", side_effect=["today", "tomorrow", "yesterday", "{today} {tomorrow} {yesterday}"])
@mock.patch("random.random", return_value=0.5)
@mock.patch("duckbot.util.datetime.now", return_value=datetime.datetime(2002, 2, 2, hour=7))
async def test_on_hour_7am_eastern_special_day(now, random, choice, bot, dog_photos, general_channel):
    clazz = AnnounceDay(bot, dog_photos)
    await clazz.on_hour()
    general_channel.send.assert_called_once_with("today tomorrow yesterday\nIt is also Groundhog Day.")


@mock.patch("random.choice", side_effect=["today", "tomorrow", "yesterday", "{today} {tomorrow} {yesterday}"])
@mock.patch("random.random", return_value=0.5)
@mock.patch("duckbot.util.datetime.now", return_value=datetime.datetime(2002, 1, 21, hour=7))
async def test_on_hour_7am_eastern_not_special_day(now, random, choice, bot, dog_photos, general_channel):
    clazz = AnnounceDay(bot, dog_photos)
    await clazz.on_hour()
    general_channel.send.assert_called_once_with("today tomorrow yesterday")


@mock.patch("random.random", side_effect=[0.09, 0.1])
@mock.patch("duckbot.util.datetime.now", return_value=datetime.datetime(2002, 1, 21, hour=7))
async def test_on_hour_7am_eastern_send_dog_photo(now, random, bot, dog_photos, general_channel):
    clazz = AnnounceDay(bot, dog_photos)
    await clazz.on_hour()
    assert general_channel.send.call_count == 2
    dog_photos.get_dog_image.assert_called()


@mock.patch("random.random", side_effect=[0.09, 0.1])
@mock.patch("duckbot.util.datetime.now", return_value=datetime.datetime(2002, 1, 21, hour=7))
async def test_on_hour_7am_eastern_send_dog_photo_failure(now, random, bot, dog_photos, general_channel):
    dog_photos.get_dog_image.side_effect = RuntimeError("ded")
    clazz = AnnounceDay(bot, dog_photos)
    await clazz.on_hour()
    general_channel.send.assert_called()
    dog_photos.get_dog_image.assert_called()


@mock.patch("random.random", side_effect=[0.1, 0.09])
@mock.patch("duckbot.util.datetime.now", return_value=datetime.datetime(2002, 1, 25, hour=7))
async def test_on_hour_7am_eastern_send_gif(now, random, bot, dog_photos, general_channel):
    clazz = AnnounceDay(bot, dog_photos)
    await clazz.on_hour()
    assert general_channel.send.call_count == 2
    dog_photos.get_dog_image.assert_not_called()


@mock.patch("random.random", side_effect=[0.1, 0.09])
@mock.patch("duckbot.util.datetime.now", return_value=datetime.datetime(2002, 1, 25, hour=7))
async def test_on_hour_7am_eastern_no_gifs_to_send(now, random, bot, dog_photos, general_channel):
    clazz = AnnounceDay(bot, dog_photos, days={i: {"names": ["name"], "templates": [], "gifs": []} for i in range(7)})
    await clazz.on_hour()
    general_channel.send.assert_called_once()
    dog_photos.get_dog_image.assert_not_called()


@pytest.mark.parametrize("hour", [h for h in range(0, 24) if h != 7])
@mock.patch("duckbot.util.datetime.now")
async def test_on_hour_not_7am(now, bot, dog_photos, hour):
    now.return_value = datetime.datetime(2002, 1, 1, hour=hour)
    clazz = AnnounceDay(bot, dog_photos)
    await clazz.on_hour()
    bot.get_all_channels.assert_not_called()
