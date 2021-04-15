import pytest
import mock
from pyowm.weatherapi25.location import Location
from pyowm.weatherapi25.one_call import OneCall
from pyowm.weatherapi25.weather import Weather as pyowmWeather
from duckbot.cogs import Weather
from duckbot.cogs.weather import SavedLocation


def make_weather(bot, owm):
    clazz = Weather(bot)
    clazz.owm_client = owm
    return clazz


def make_city(name):
    return Location(name, 1, 1, 1)


@mock.patch("discord.ext.commands.Bot")
@mock.patch("os.getenv", return_value="token")
def test_owm_creates_instance(bot, env):
    clazz = Weather(bot)
    assert clazz.owm() == clazz.owm_client


@mock.patch("discord.ext.commands.Bot")
@mock.patch("pyowm.OWM")
def test_owm_returns_cached_instance(bot, owm):
    clazz = Weather(bot)
    clazz.owm_client = owm
    assert clazz.owm() == owm


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
@mock.patch("pyowm.OWM")
@mock.patch("discord.ext.commands.Context")
async def test_weather_get_failure(bot, owm, context):
    clazz = make_weather(bot, owm)
    owm.weather_manager.side_effect = Exception("ded")
    await clazz.weather(context, "city", None, None)
    context.send.assert_called_once_with("Iunno. Figure it out.\nded")


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
@mock.patch("pyowm.OWM")
@mock.patch("discord.ext.commands.Context")
async def test_search_location_no_args(bot, owm, context):
    clazz = make_weather(bot, owm)
    assert await clazz.search_location(context, None, None, None) is None
    context.send.assert_called_once_with("Not enough arguments to determine weather location, see https://github.com/Chippers255/duckbot/wiki#weather")


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
@mock.patch("pyowm.OWM")
@mock.patch("discord.ext.commands.Context")
@mock.patch("pyowm.commons.cityidregistry.CityIDRegistry")
async def test_search_location_no_matches(bot, owm, context, city_id):
    clazz = make_weather(bot, owm)
    owm.city_id_registry.return_value = city_id
    city_id.locations_for.return_value = []
    assert await clazz.search_location(context, "city", None, None) is None
    context.send.assert_called_once_with("No cities found matching search.")


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
@mock.patch("pyowm.OWM")
@mock.patch("discord.ext.commands.Context")
@mock.patch("pyowm.commons.cityidregistry.CityIDRegistry")
async def test_search_location_single_return_city_only(bot, owm, context, city_id):
    clazz = make_weather(bot, owm)
    owm.city_id_registry.return_value = city_id
    city_id.locations_for.return_value = [make_city("city")]
    city = await clazz.search_location(context, "city", None, None)
    assert city.to_dict() == make_city("city").to_dict()


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
@mock.patch("pyowm.OWM")
@mock.patch("discord.ext.commands.Context")
@mock.patch("pyowm.commons.cityidregistry.CityIDRegistry")
async def test_search_location_single_return_country_arg(bot, owm, context, city_id):
    clazz = make_weather(bot, owm)
    owm.city_id_registry.return_value = city_id
    city_id.locations_for.return_value = [make_city("city")]
    city = await clazz.search_location(context, "city", "US", None)
    assert city.to_dict() == make_city("city").to_dict()


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
@mock.patch("pyowm.OWM")
@mock.patch("discord.ext.commands.Context")
@mock.patch("pyowm.commons.cityidregistry.CityIDRegistry")
async def test_search_location_single_return_invalid_country_code(bot, owm, context, city_id):
    clazz = make_weather(bot, owm)
    owm.city_id_registry.return_value = city_id
    city_id.locations_for.return_value = [make_city("city")]
    city = await clazz.search_location(context, "city", "invalid", None)
    assert city is None
    context.send.assert_called_once_with("Country must be an ISO country code, such as CA for Canada.")


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
@mock.patch("pyowm.OWM")
@mock.patch("discord.ext.commands.Context")
@mock.patch("pyowm.commons.cityidregistry.CityIDRegistry")
async def test_search_location_multiple_matches(bot, owm, context, city_id):
    clazz = make_weather(bot, owm)
    owm.city_id_registry.return_value = city_id
    city_id.locations_for.return_value = [make_city("1"), make_city("2")]
    city = await clazz.search_location(context, "city", None, None)
    assert city is None
    context.send.assert_called()


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
@mock.patch("pyowm.OWM")
@mock.patch("discord.ext.commands.Context")
@mock.patch("pyowm.commons.cityidregistry.CityIDRegistry")
async def test_search_location_multiple_matches_with_index(bot, owm, context, city_id):
    clazz = make_weather(bot, owm)
    owm.city_id_registry.return_value = city_id
    city_id.locations_for.return_value = [make_city("1"), make_city("2")]
    city = await clazz.search_location(context, "city", "US", 1)
    assert city.to_dict() == make_city("1").to_dict()


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
@mock.patch("duckbot.db.Database")
@mock.patch("sqlalchemy.orm.session.Session")
@mock.patch("pyowm.OWM")
@mock.patch("discord.ext.commands.Context")
async def test_set_default_location_location_saved(bot, db, session, owm, context):
    clazz = make_weather(bot, owm)
    bot.get_cog.return_value = db
    db.session.return_value.__enter__.return_value = session

    async def mock_search_location(context, city, country, index):
        return make_city("city")

    city = make_city("city")
    clazz.search_location = mock_search_location
    await clazz.set_default_location(context, None, None, None)
    context.send.assert_called_once_with(f"Location saved! {city.name}, {city.country}, geolocation = ({city.lat}, {city.lon})")
    session.merge.assert_called()


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
@mock.patch("pyowm.OWM")
@mock.patch("discord.ext.commands.Context")
async def test_set_default_location_location_not_saved(bot, owm, context):
    clazz = make_weather(bot, owm)

    async def mock_search_location(context, city, country, index):
        return None

    clazz.search_location = mock_search_location
    await clazz.set_default_location(context, None, None, None)
    bot.get_cog.assert_not_called()


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
@mock.patch("duckbot.db.Database")
@mock.patch("sqlalchemy.orm.session.Session")
@mock.patch("pyowm.OWM")
@mock.patch("discord.ext.commands.Context")
@mock.patch("pyowm.weatherapi25.weather_manager.WeatherManager")
async def test_get_weather_no_default_no_args(bot, db, session, owm, context, weather):
    bot.get_cog.return_value = db
    db.session.return_value.__enter__.return_value = session
    session.get.return_value = None
    clazz = make_weather(bot, owm)
    owm.weather_manager.return_value = weather
    await clazz.get_weather(context, None, None, None)
    context.send.assert_called_once_with("Set a default location using `!weather set city country-code`")


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
@mock.patch("duckbot.db.Database")
@mock.patch("sqlalchemy.orm.session.Session")
@mock.patch("pyowm.OWM")
@mock.patch("discord.ext.commands.Context")
@mock.patch("pyowm.weatherapi25.weather_manager.WeatherManager")
async def test_get_weather_default_location(bot, db, session, owm, context, weather):
    bot.get_cog.return_value = db
    db.session.return_value.__enter__.return_value = session
    session.get.return_value = SavedLocation(id=1, name="city", country="country", city_id=123, latitude=1, longitude=2)
    clazz = make_weather(bot, owm)
    clazz.weather_message = stub_weather_msg
    owm.weather_manager.return_value = weather
    await clazz.get_weather(context, None, None, None)
    context.send.assert_called_once_with("weather")


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
@mock.patch("pyowm.OWM")
@mock.patch("discord.ext.commands.Context")
@mock.patch("pyowm.weatherapi25.weather_manager.WeatherManager")
async def test_get_weather_provided_location(bot, owm, context, weather):
    clazz = make_weather(bot, owm)

    async def mock_search_location(context, *args):
        return make_city("city")

    clazz.search_location = mock_search_location
    clazz.weather_message = stub_weather_msg
    owm.weather_manager.return_value = weather
    await clazz.get_weather(context, "city", None, None)
    context.send.assert_called_once_with("weather")


@mock.patch("discord.ext.commands.Bot")
@mock.patch("pyowm.OWM")
def test_weather_message_no_precipitation(bot, owm):
    clazz = make_weather(bot, owm)
    message = clazz.weather_message(make_city("city"), one_call())
    assert "In city, it is currently 3°C, but feels like 5°C." in message
    assert "Today, you can expect a high of 10°C (feeling like 15°C) and a low of 0°C (feeling like -10°C)." in message


@mock.patch("discord.ext.commands.Bot")
@mock.patch("pyowm.OWM")
def test_weather_message_rainy(bot, owm):
    clazz = make_weather(bot, owm)
    message = clazz.weather_message(make_city("city"), one_call("rainy"))
    assert "In city, it is currently 3°C with rainy, but feels like 5°C." in message
    assert "Today, you can expect a high of 10°C (feeling like 15°C) and a low of 0°C (feeling like -10°C), with a 50% chance of 2mm of rain." in message


@mock.patch("discord.ext.commands.Bot")
@mock.patch("pyowm.OWM")
def test_weather_message_snowy(bot, owm):
    clazz = make_weather(bot, owm)
    message = clazz.weather_message(make_city("city"), one_call("snowy"))
    assert "In city, it is currently 3°C with snowy, but feels like 5°C." in message
    assert "Today, you can expect a high of 10°C (feeling like 15°C) and a low of 0°C (feeling like -10°C), with a 50% chance of 3cm of snow." in message


@mock.patch("discord.ext.commands.Bot")
@mock.patch("pyowm.OWM")
def test_weather_message_umbrella(bot, owm):
    clazz = make_weather(bot, owm)
    message = clazz.weather_message(make_city("city"), one_call("rain", 100))
    assert "Don't forget your umbrella!" in message


@mock.patch("discord.ext.commands.Bot")
@mock.patch("pyowm.OWM")
def test_weather_message_shovel(bot, owm):
    clazz = make_weather(bot, owm)
    message = clazz.weather_message(make_city("city"), one_call("snowy", 100))
    assert "Time to hire the old man down the street to shovel the driveway." in message


@mock.patch("discord.ext.commands.Bot")
@mock.patch("pyowm.OWM")
def test_weather_message_cold(bot, owm):
    clazz = make_weather(bot, owm)
    message = clazz.weather_message(make_city("city"), one_call(max_temp=-11))
    assert "Thankfully, I don't feel the cold." in message


@mock.patch("discord.ext.commands.Bot")
@mock.patch("pyowm.OWM")
def test_weather_message_hot(bot, owm):
    clazz = make_weather(bot, owm)
    message = clazz.weather_message(make_city("city"), one_call(max_temp=40))
    assert "I might need to take a break today, it hot." in message


def stub_weather_msg(city, weather):
    return "weather"


def one_call(status=None, prec_chance=49.9, max_temp=10):
    wea = weather(status, prec_chance, max_temp)
    return OneCall(lat=1, lon=1, timezone="UTC", current=wea, forecast_daily=[wea])


def weather(status, prec_chance, max_temp):
    return pyowmWeather(
        reference_time=0,
        sunset_time=0,
        sunrise_time=0,
        clouds=0,
        rain={"all": 1.9},
        snow={"all": 2.9},
        wind=None,
        humidity=0,
        pressure=None,
        temperature={"temp": 3, "min": 0, "max": max_temp, "feels_like_day": 15, "feels_like_night": -10, "feels_like": 5},
        status=status,
        detailed_status=status,
        weather_code=None,
        weather_icon_name=None,
        visibility_distance=None,
        dewpoint=None,
        humidex=None,
        heat_index=None,
        precipitation_probability=prec_chance / 100,
    )
