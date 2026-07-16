import datetime
from unittest import mock

import discord
import pytest

from duckbot.cogs.games import EpicGames
from duckbot.cogs.games.epic_games import FREE_GAMES_URL
from tests.discord_test_ext import bind_commands

END_DATE = "2026-07-23T15:00:00.000Z"
END_EPOCH = 1784818800
THURSDAY = datetime.datetime(2026, 7, 23, hour=12)
FRIDAY = datetime.datetime(2026, 7, 24, hour=12)


@pytest.fixture
def clazz(bot) -> EpicGames:
    return bind_commands(EpicGames(bot))


@pytest.fixture
def games_channel(bot, guild, text_channel) -> discord.TextChannel:
    bot.get_all_channels.return_value = [text_channel]
    guild.name = "Friends Chat"
    text_channel.guild = guild
    text_channel.name = "games"
    return text_channel


def game(title, discount_price=0, discount_percentage=0, current_promo=True):
    offer = {"startDate": "2026-07-16T15:00:00.000Z", "endDate": END_DATE, "discountSetting": {"discountType": "PERCENTAGE", "discountPercentage": discount_percentage}}
    promotions = {"promotionalOffers": [{"promotionalOffers": [offer]}] if current_promo else [], "upcomingPromotionalOffers": [] if current_promo else [{"promotionalOffers": [offer]}]}
    return {
        "title": title,
        "description": f"{title} is a video game.",
        "keyImages": [{"type": "OfferImageWide", "url": f"https://cdn1.epicgames.com/{title}-wide.jpg"}, {"type": "Thumbnail", "url": f"https://cdn1.epicgames.com/{title}-thumb.jpg"}],
        "productSlug": None,
        "offerMappings": [{"pageSlug": f"{title}-slug", "pageType": "productHome"}],
        "catalogNs": {"mappings": []},
        "price": {"totalPrice": {"discountPrice": discount_price, "fmtPrice": {"originalPrice": "$25.99 CAD"}}},
        "promotions": promotions,
    }


def payload(*games):
    return {"data": {"Catalog": {"searchStore": {"elements": list(games)}}}}


def expected_embed(title):
    embed = discord.Embed(title=title, url=f"https://store.epicgames.com/en-CA/p/{title}-slug", description=f"{title} is a video game.")
    embed.set_image(url=f"https://cdn1.epicgames.com/{title}-wide.jpg")
    embed.add_field(name="Free until", value=f"<t:{END_EPOCH}:R>")
    embed.add_field(name="Original price", value="$25.99 CAD")
    return embed


async def test_before_loop_waits_for_bot(bot, clazz):
    await clazz.before_loop()
    bot.wait_until_ready.assert_called()


def test_cog_unload_cancels_task(clazz):
    clazz.cog_unload()
    clazz.free_games_loop.cancel.assert_called()


def test_get_free_games_filters_free_games(clazz, responses):
    free = game("Luto")
    discounted = game("Foretales", discount_price=299, discount_percentage=15)
    upcoming = game("LISA", discount_price=2499, current_promo=False)
    no_promotions = game("Monument Valley", discount_price=799) | {"promotions": None}
    responses.add(responses.GET, FREE_GAMES_URL, json=payload(free, discounted, upcoming, no_promotions))
    assert clazz.get_free_games() == [expected_embed("Luto")]


async def test_epic_sends_free_game_embeds(clazz, context, responses):
    responses.add(responses.GET, FREE_GAMES_URL, json=payload(game("Luto"), game("Echo Generation")))
    await clazz.epic(context)
    context.send.assert_called_once_with(embeds=[expected_embed("Luto"), expected_embed("Echo Generation")])


async def test_epic_no_free_games(clazz, context, responses):
    responses.add(responses.GET, FREE_GAMES_URL, json=payload())
    await clazz.epic(context)
    context.send.assert_called_once_with("no free games right now, somehow")


@mock.patch("duckbot.cogs.games.epic_games.now", return_value=THURSDAY)
async def test_announce_free_games_thursday(now, clazz, games_channel, responses):
    responses.add(responses.GET, FREE_GAMES_URL, json=payload(game("Luto")))
    await clazz.announce_free_games()
    games_channel.send.assert_called_once_with(embeds=[expected_embed("Luto")])


@mock.patch("duckbot.cogs.games.epic_games.now", return_value=THURSDAY)
async def test_announce_free_games_thursday_no_free_games(now, clazz, games_channel, responses):
    responses.add(responses.GET, FREE_GAMES_URL, json=payload())
    await clazz.announce_free_games()
    games_channel.send.assert_not_called()


@mock.patch("duckbot.cogs.games.epic_games.now", return_value=FRIDAY)
async def test_announce_free_games_not_thursday(now, clazz, games_channel):
    await clazz.announce_free_games()
    games_channel.send.assert_not_called()
