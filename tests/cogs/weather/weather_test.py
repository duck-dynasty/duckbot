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
def weather(bot, owm, db):
    clazz = Weather(bot, db)
    clazz._owm = owm
    return clazz


def make_city(name):
    return Location(name, 1, 1, 1)


def test_owm_creates_instance(bot, db, monkeypatch):
    monkeypatch.setenv("OPENWEATHER_TOKEN", "token")
    clazz = Weather(bot, db)
    assert clazz.owm == clazz._owm


def test_owm_returns_cached_instance(weather, owm):
    weather._owm = owm
    assert weather.owm == owm


@pytest.mark.asyncio
async def test_weather_get_failure(weather, owm, context):
    owm.weather_manager.side_effect = Exception("ded")
    with pytest.raises(Exception):
        await weather.weather(context, "city", None, None)
    context.send.assert_called_once_with("Iunno. Figure it out.\nded")


@pytest.mark.asyncio
async def test_search_location_no_args(weather, context):
    assert await weather.search_location(context, None, None, None) is None
    context.send.assert_called_once_with("Not enough arguments to determine weather location, see https://github.com/duck-dynasty/duckbot/wiki/Commands#weather")


@pytest.mark.asyncio
async def test_search_location_no_matches(weather, context, city_id):
    city_id.locations_for.return_value = []
    assert await weather.search_location(context, "city", None, None) is None
    context.send.assert_called_once_with("No cities found matching search.")


@pytest.mark.asyncio
async def test_search_location_single_return_city_only(weather, context, city_id):
    city_id.locations_for.return_value = [make_city("city")]
    city = await weather.search_location(context, "city", None, None)
    city_id.locations_for.assert_called_once_with("city", country=None)
    assert city.to_dict() == make_city("city").to_dict()


@pytest.mark.asyncio
async def test_search_location_city_name_with_comma_removed(weather, context, city_id):
    city_id.locations_for.return_value = [make_city("city")]
    city = await weather.search_location(context, "city,", None, None)
    city_id.locations_for.assert_called_once_with("city", country=None)
    assert city.to_dict() == make_city("city").to_dict()


@pytest.mark.asyncio
async def test_search_location_single_return_country_arg(weather, context, city_id):
    city_id.locations_for.return_value = [make_city("city")]
    city = await weather.search_location(context, "city", "US", None)
    city_id.locations_for.assert_called_once_with("city", country="US")
    assert city.to_dict() == make_city("city").to_dict()


@pytest.mark.asyncio
async def test_search_location_single_return_invalid_country_code(weather, context, city_id):
    city_id.locations_for.return_value = [make_city("city")]
    city = await weather.search_location(context, "city", "invalid", None)
    assert city is None
    context.send.assert_called_once_with("Country must be an ISO country code, such as CA for Canada.")


@pytest.mark.asyncio
async def test_search_location_multiple_matches(weather, context, city_id):
    city_id.locations_for.return_value = [make_city("1"), make_city("2")]
    city = await weather.search_location(context, "city", None, None)
    assert city is None
    context.send.assert_called()


@pytest.mark.asyncio
async def test_search_location_multiple_matches_with_index(weather, context, city_id):
    city_id.locations_for.return_value = [make_city("1"), make_city("2")]
    city = await weather.search_location(context, "city", "US", 1)
    assert city.to_dict() == make_city("1").to_dict()


@pytest.mark.asyncio
async def test_set_default_location_location_saved(weather, session, context):
    async def mock_search_location(context, city, country, index):
        return make_city("city")

    city = make_city("city")
    weather.search_location = mock_search_location
    await weather.set_default_location(context, None, None, None)
    context.send.assert_called_once_with(f"Location saved! {city.name}, {city.country}, geolocation = ({city.lat}, {city.lon})")
    session.merge.assert_called()
    session.commit.assert_called()


@pytest.mark.asyncio
async def test_set_default_location_location_not_saved(weather, session, context):
    async def mock_search_location(context, city, country, index):
        return None

    weather.search_location = mock_search_location
    await weather.set_default_location(context, None, None, None)
    session.merge.assert_not_called()
    session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_send_weather_no_default_no_args(weather, session, context):
    session.get.return_value = None
    await weather.send_weather(context, None, None, None)
    context.send.assert_called_once_with("Set a default location using `!weather set city country-code`")


@pytest.mark.asyncio
@mock.patch("discord.File")
async def test_send_weather_default_location(file, weather, session, context):
    session.get.return_value = SavedLocation(id=1, name="city", country="country", city_id=123, latitude=1, longitude=2)
    weather.weather_message = stub_weather_msg
    weather.weather_graph = stub_weather_gph
    await weather.send_weather(context, None, None, None)
    context.send.assert_called_once_with("weather", file=file.return_value)


@pytest.mark.asyncio
@mock.patch("discord.File")
async def test_send_weather_provided_location(file, weather, context):
    async def mock_search_location(context, *args):
        return make_city("city")

    weather.search_location = mock_search_location
    weather.weather_message = stub_weather_msg
    weather.weather_graph = stub_weather_gph
    await weather.send_weather(context, "city", None, None)
    context.send.assert_called_once_with("weather", file=file.return_value)


def test_weather_message_no_precipitation(weather):
    message = weather.weather_message(make_city("city"), one_call())
    assert "In city, it is currently 3°C, but feels like 5°C." in message
    assert "Today, you can expect a high of 10°C (feeling like 15°C) and a low of 0°C (feeling like -10°C)." in message


def test_weather_message_rainy(weather):
    message = weather.weather_message(make_city("city"), one_call("rainy"))
    assert "In city, it is currently 3°C with rainy, but feels like 5°C." in message
    assert "Today, you can expect a high of 10°C (feeling like 15°C) and a low of 0°C (feeling like -10°C), with a 50% chance of 2mm of rain." in message


def test_weather_message_snowy(weather):
    message = weather.weather_message(make_city("city"), one_call("snowy"))
    assert "In city, it is currently 3°C with snowy, but feels like 5°C." in message
    assert "Today, you can expect a high of 10°C (feeling like 15°C) and a low of 0°C (feeling like -10°C), with a 50% chance of 3cm of snow." in message


def test_weather_message_umbrella(weather):
    message = weather.weather_message(make_city("city"), one_call("rain", 100))
    assert "Don't forget your umbrella!" in message


def test_weather_message_shovel(weather):
    message = weather.weather_message(make_city("city"), one_call("snowy", 100))
    assert "Time to hire the old man down the street to shovel the driveway." in message


def test_weather_message_cold(weather):
    message = weather.weather_message(make_city("city"), one_call(max_temp=-11))
    assert "Thankfully, I don't feel the cold." in message


def test_weather_message_hot(weather):
    message = weather.weather_message(make_city("city"), one_call(max_temp=40))
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
def test_weather_graph_for_code_coverage(tzfinder, weather, plt):
    tzfinder.return_value.timezone_at.return_value = "US/Eastern"
    img = weather.weather_graph(make_city("city"), one_call())
    assert img == "weather.png"


def stub_weather_msg(city, weather):
    return "weather"


def stub_weather_gph(city, weather):
    return "weather.png"


def one_call(status=None, prec_chance=49.9, max_temp=10):
    wea = make_weather(status, prec_chance, max_temp)
    return OneCall(lat=1, lon=1, timezone="UTC", current=wea, forecast_daily=[wea], forecast_hourly=[wea] * 24)


def make_weather(status, prec_chance, max_temp):
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
