from unittest import mock

import pytest
from pyowm.weatherapi25.location import Location
from pyowm.weatherapi25.one_call import OneCall
from pyowm.weatherapi25.weather import Weather as pyowmWeather

from duckbot.cogs.weather import Weather
from duckbot.cogs.weather.saved_location import SavedLocation


@pytest.fixture
@mock.patch("pyowm.commons.cityidregistry.CityIDRegistry")
def city_id(c):
    return c


@pytest.fixture
@mock.patch("pyowm.weatherapi25.weather_manager.WeatherManager")
def weather_manager(w):
    return w


@pytest.fixture
@mock.patch("pyowm.OWM")
def owm(o, city_id, weather_manager):
    o.city_id_registry.return_value = city_id
    o.weather_manager.return_value = weather_manager
    return o


@pytest.fixture
def clazz(bot, owm, db):
    claz = Weather(bot, db)
    claz.owm_client = owm
    return claz


def make_city(name):
    return Location(name, 1, 1, 1)


def test_owm_creates_instance(bot, db, monkeypatch):
    monkeypatch.setenv("OPENWEATHER_TOKEN", "token")
    claz = Weather(bot, db)
    assert claz.owm() == claz.owm_client


def test_owm_returns_cached_instance(clazz, owm):
    clazz.owm_client = owm
    assert clazz.owm() == owm


@pytest.mark.asyncio
async def test_weather_get_failure(clazz, owm, context):
    owm.weather_manager.side_effect = Exception("ded")
    with pytest.raises(Exception):
        await clazz.weather(context, "city", None, None)
    context.send.assert_called_once_with("Iunno. Figure it out.\nded")


@pytest.mark.asyncio
async def test_search_location_no_args(clazz, context):
    assert await clazz.search_location(context, None, None, None) is None
    context.send.assert_called_once_with("Not enough arguments to determine weather location, see https://github.com/duck-dynasty/duckbot/wiki/Commands#weather")


@pytest.mark.asyncio
async def test_search_location_no_matches(clazz, context, city_id):
    city_id.locations_for.return_value = []
    assert await clazz.search_location(context, "city", None, None) is None
    context.send.assert_called_once_with("No cities found matching search.")


@pytest.mark.asyncio
async def test_search_location_single_return_city_only(clazz, context, city_id):
    city_id.locations_for.return_value = [make_city("city")]
    city = await clazz.search_location(context, "city", None, None)
    city_id.locations_for.assert_called_once_with("city", country=None)
    assert city.to_dict() == make_city("city").to_dict()


@pytest.mark.asyncio
async def test_search_location_city_name_with_comma_removed(clazz, context, city_id):
    city_id.locations_for.return_value = [make_city("city")]
    city = await clazz.search_location(context, "city,", None, None)
    city_id.locations_for.assert_called_once_with("city", country=None)
    assert city.to_dict() == make_city("city").to_dict()


@pytest.mark.asyncio
async def test_search_location_single_return_country_arg(clazz, context, city_id):
    city_id.locations_for.return_value = [make_city("city")]
    city = await clazz.search_location(context, "city", "US", None)
    city_id.locations_for.assert_called_once_with("city", country="US")
    assert city.to_dict() == make_city("city").to_dict()


@pytest.mark.asyncio
async def test_search_location_single_return_invalid_country_code(clazz, context, city_id):
    city_id.locations_for.return_value = [make_city("city")]
    city = await clazz.search_location(context, "city", "invalid", None)
    assert city is None
    context.send.assert_called_once_with("Country must be an ISO country code, such as CA for Canada.")


@pytest.mark.asyncio
async def test_search_location_multiple_matches(clazz, context, city_id):
    city_id.locations_for.return_value = [make_city("1"), make_city("2")]
    city = await clazz.search_location(context, "city", None, None)
    assert city is None
    context.send.assert_called()


@pytest.mark.asyncio
async def test_search_location_multiple_matches_with_index(clazz, context, city_id):
    city_id.locations_for.return_value = [make_city("1"), make_city("2")]
    city = await clazz.search_location(context, "city", "US", 1)
    assert city.to_dict() == make_city("1").to_dict()


@pytest.mark.asyncio
async def test_set_default_location_location_saved(clazz, session, context):
    async def mock_search_location(context, city, country, index):
        return make_city("city")

    city = make_city("city")
    clazz.search_location = mock_search_location
    await clazz.set_default_location(context, None, None, None)
    context.send.assert_called_once_with(f"Location saved! {city.name}, {city.country}, geolocation = ({city.lat}, {city.lon})")
    session.merge.assert_called()
    session.commit.assert_called()


@pytest.mark.asyncio
async def test_set_default_location_location_not_saved(clazz, session, context):
    async def mock_search_location(context, city, country, index):
        return None

    clazz.search_location = mock_search_location
    await clazz.set_default_location(context, None, None, None)
    session.merge.assert_not_called()
    session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_send_weather_no_default_no_args(clazz, session, context):
    session.get.return_value = None
    await clazz.send_weather(context, None, None, None)
    context.send.assert_called_once_with("Set a default location using `!weather set city country-code`")


@pytest.mark.asyncio
@mock.patch("discord.File")
async def test_send_weather_default_location(file, clazz, session, context):
    session.get.return_value = SavedLocation(id=1, name="city", country="country", city_id=123, latitude=1, longitude=2)
    clazz.weather_message = stub_weather_msg
    clazz.weather_graph = stub_weather_gph
    await clazz.send_weather(context, None, None, None)
    context.send.assert_called_once_with("weather", file=file.return_value)


@pytest.mark.asyncio
@mock.patch("discord.File")
async def test_send_weather_provided_location(file, clazz, context):
    async def mock_search_location(context, *args):
        return make_city("city")

    clazz.search_location = mock_search_location
    clazz.weather_message = stub_weather_msg
    clazz.weather_graph = stub_weather_gph
    await clazz.send_weather(context, "city", None, None)
    context.send.assert_called_once_with("weather", file=file.return_value)


def test_weather_message_no_precipitation(clazz):
    message = clazz.weather_message(make_city("city"), one_call())
    assert "In city, it is currently 3°C, but feels like 5°C." in message
    assert "Today, you can expect a high of 10°C (feeling like 15°C) and a low of 0°C (feeling like -10°C)." in message


def test_weather_message_rainy(clazz):
    message = clazz.weather_message(make_city("city"), one_call("rainy"))
    assert "In city, it is currently 3°C with rainy, but feels like 5°C." in message
    assert "Today, you can expect a high of 10°C (feeling like 15°C) and a low of 0°C (feeling like -10°C), with a 50% chance of 2mm of rain." in message


def test_weather_message_snowy(clazz):
    message = clazz.weather_message(make_city("city"), one_call("snowy"))
    assert "In city, it is currently 3°C with snowy, but feels like 5°C." in message
    assert "Today, you can expect a high of 10°C (feeling like 15°C) and a low of 0°C (feeling like -10°C), with a 50% chance of 3cm of snow." in message


def test_weather_message_umbrella(clazz):
    message = clazz.weather_message(make_city("city"), one_call("rain", 100))
    assert "Don't forget your umbrella!" in message


def test_weather_message_shovel(clazz):
    message = clazz.weather_message(make_city("city"), one_call("snowy", 100))
    assert "Time to hire the old man down the street to shovel the driveway." in message


def test_weather_message_cold(clazz):
    message = clazz.weather_message(make_city("city"), one_call(max_temp=-11))
    assert "Thankfully, I don't feel the cold." in message


def test_weather_message_hot(clazz):
    message = clazz.weather_message(make_city("city"), one_call(max_temp=40))
    assert "I might need to take a break today, it hot." in message


@pytest.fixture
@mock.patch("duckbot.cogs.weather.weather.plt")
def plt(plot):
    fig = mock.MagicMock()
    axis = mock.MagicMock()
    plot.subplots.return_value = (fig, axis)
    axis.twinx.return_value = axis
    axis.bar.return_value = []
    return plot


@mock.patch("timezonefinder.TimezoneFinder")
def test_weather_graph_for_code_coverage(tzfinder, clazz, plt):
    tzfinder.return_value.timezone_at.return_value = "US/Eastern"
    img = clazz.weather_graph(make_city("city"), one_call())
    assert img == "weather.png"


def stub_weather_msg(city, weather):
    return "weather"


def stub_weather_gph(city, weather):
    return "weather.png"


def one_call(status=None, prec_chance=49.9, max_temp=10):
    wea = weather(status, prec_chance, max_temp)
    return OneCall(lat=1, lon=1, timezone="UTC", current=wea, forecast_daily=[wea], forecast_hourly=[wea] * 24)


def weather(status, prec_chance, max_temp):
    return pyowmWeather(
        reference_time=0,
        sunset_time=0,
        sunrise_time=0,
        clouds=0,
        rain={"all": 1.9, "1h": 0.5},
        snow={"all": 2.9, "1h": 1.5},
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
