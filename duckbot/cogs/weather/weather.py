import datetime
import os
from math import ceil
from typing import Optional

import discord
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pyowm
import pytz
import timezonefinder
from discord.ext import commands
from pyowm.utils import config
from pyowm.weatherapi25.location import Location
from pyowm.weatherapi25.one_call import OneCall

from duckbot.db import Database

from .saved_location import SavedLocation

degrees = "\N{DEGREE SIGN}C"


class Weather(commands.Cog):
    def __init__(self, bot, db: Database):
        self.bot = bot
        self.db = db
        self.owm_client: pyowm.OWM = None

    def owm(self) -> pyowm.OWM:
        if self.owm_client is None:
            conf = config.get_default_config_for_subscription_type("free")
            self.owm_client = pyowm.OWM(os.getenv("OPENWEATHER_TOKEN"), conf)
        return self.owm_client

    @commands.group(name="weather", invoke_without_command=True)
    async def weather_command(self, context, city: str = None, country: str = None, index: int = None):
        await self.weather(context, city, country, index)

    async def weather(self, context, city: str, country: str, index: int):
        async with context.typing():
            try:
                return await self.send_weather(context, city, country, index)
            except Exception as e:
                await context.send(f"Iunno. Figure it out.\n{e}")
                raise e

    @weather_command.command(name="set", invoke_without_command=True)
    async def weather_set_command(self, context, city: str = None, country: str = None, index: int = None):
        await self.set_default_location(context, city, country, index)

    async def set_default_location(self, context, city: str, country: str, index: int) -> None:
        location = await self.search_location(context, city, country, index)
        if location is not None:
            saved_location = SavedLocation(id=context.author.id, name=location.name, country=location.country, city_id=location.id, latitude=location.lat, longitude=location.lon)
            with self.db.session(SavedLocation) as session:
                session.merge(saved_location)
                session.commit()
            await context.send(f"Location saved! {self.__location_string(location)}")

    async def search_location(self, context, city: str, country: str, index: int) -> Optional[Location]:
        if city is not None:
            country = country.upper().replace(",", "") if country is not None else None
            if country is not None and len(country) != 2:
                await context.send("Country must be an ISO country code, such as CA for Canada.")
                return None
            locations = self.owm().city_id_registry().locations_for(city.replace(",", ""), country=country)
            if not locations:
                await context.send("No cities found matching search.")
                return None
            elif len(locations) > 1:
                if index is not None:
                    return locations[int(index) - 1]
                else:
                    message = "Multiple cities found matching search.\nNarrow your search or specify an index to pick one of the following:\n"
                    options = [f"{i+1}: {self.__location_string(c)}" for i, c in enumerate(locations)]
                    await context.send(message + "\n".join(options))
                    return None
            else:
                return locations[0]
        else:
            await context.send("Not enough arguments to determine weather location, see https://github.com/duck-dynasty/duckbot/wiki/Commands#weather")
            return None

    def __location_string(self, city: Location):
        return f"{city.name}, {city.country}, geolocation = ({city.lat}, {city.lon})"

    async def send_weather(self, context, city: str, country: str, index: int) -> None:
        location = None
        if city is None:
            with self.db.session(SavedLocation) as session:
                saved = session.get(SavedLocation, context.author.id)
            if saved is not None:
                location = Location(name=saved.name, lon=saved.longitude, lat=saved.latitude, _id=saved.city_id, country=saved.country)
            else:
                await context.send("Set a default location using `!weather set city country-code`")
        else:
            location = await self.search_location(context, city, country, index)
        if location is not None:
            weather = self.owm().weather_manager().one_call(lat=location.lat, lon=location.lon, exclude="minutely", units="metric")
            await context.send(self.weather_message(location, weather), file=discord.File(self.weather_graph(location, weather)))

    def weather_message(self, city: Location, weather: OneCall) -> str:
        messages = []
        current = weather.current
        temp = current.temperature()
        now = f"{round(temp['temp'])}{degrees}"
        feels = f"{round(temp['feels_like'])}{degrees}"
        if self.__is_rainy(current) or self.__is_snowy(current):
            messages.append(f"In {city.name}, it is currently {now} with {current.detailed_status}, but feels like {feels}.")
        else:
            messages.append(f"In {city.name}, it is currently {now}, but feels like {feels}.")

        today = weather.forecast_daily[0]
        temp_today = today.temperature()
        rain_chance = round(today.precipitation_probability * 100)
        max_today = f"{round(temp_today['max'])}{degrees} (feeling like {round(temp_today['feels_like_day'])}{degrees})"
        min_today = f"{round(temp_today['min'])}{degrees} (feeling like {round(temp_today['feels_like_night'])}{degrees})"
        if self.__is_rainy(today):
            messages.append(f"Today, you can expect a high of {max_today} and a low of {min_today}, with a {rain_chance}% chance of {ceil(today.rain['all'])}mm of rain.")
        elif self.__is_snowy(today):
            messages.append(f"Today, you can expect a high of {max_today} and a low of {min_today}, with a {rain_chance}% chance of {ceil(today.snow['all'])}cm of snow.")
        else:
            messages.append(f"Today, you can expect a high of {max_today} and a low of {min_today}.")

        if rain_chance > 50 and self.__is_rainy(today):
            messages.append("Don't forget your umbrella!")
        elif rain_chance > 50 and self.__is_snowy(today):
            messages.append("Time to hire the old man down the street to shovel the driveway.")
        elif temp_today["max"] < -10:
            messages.append("Thankfully, I don't feel the cold.")
        elif temp_today["max"] > 35:
            messages.append("I might need to take a break today, it hot.")
        return " ".join(messages)

    def __is_rainy(self, weather) -> str:
        return (weather.status and "rain" in weather.status.lower()) or (weather.detailed_status and "rain" in weather.detailed_status.lower())

    def __is_snowy(self, weather) -> str:
        return (weather.status and "snow" in weather.status.lower()) or (weather.detailed_status and "snow" in weather.detailed_status.lower())

    def weather_graph(self, city: Location, weather: OneCall):
        hourly = [weather.forecast_hourly[i] for i in range(24)]
        tz = pytz.timezone(timezonefinder.TimezoneFinder().timezone_at(lat=city.lat, lng=city.lon))
        hours = [w.reference_time("date").astimezone(tz=tz) for w in hourly]
        figure, left_axis = plt.subplots()
        left_axis.set_xlabel("Time")
        left_axis.set_ylabel(f"Temperature ({degrees})")
        left_axis.plot(hours, [w.temperature()["temp"] for w in hourly], label="Temperature", color="orangered")
        left_axis.plot(hours, [w.temperature()["feels_like"] for w in hourly], label="Feels Like", color="forestgreen")
        left_axis.legend(loc="upper left")
        left_axis.set_facecolor("ghostwhite")

        right_axis = left_axis.twinx()
        right_axis.set_ylabel("Precipitation")
        rain = [w.rain["1h"] if "1h" in w.rain else 0 for w in hourly]
        snow = [w.snow["1h"] if "1h" in w.snow else 0 for w in hourly]
        rects_rain = right_axis.bar(hours, rain, label="Rain (mm)", color="blue", alpha=0.3, width=1.0 / 24)
        rects_snow = right_axis.bar(hours, snow, bottom=rain, label="Snow (cm)", color="powderblue", alpha=0.3, width=1.0 / 24)
        right_axis.legend(loc="upper right")

        y_max = max(1, max([r.get_height() + s.get_height() for r, s in zip(rects_rain, rects_snow)]))
        right_axis.set_ylim([0, y_max])

        for i, w in enumerate(hourly):
            probability = round(w.precipitation_probability * 100)
            plt.text(hours[i], 0.2 * y_max, f"{probability}%", ha="center", va="center", rotation=90, color="darkblue", alpha=0.5)
            plt.text(hours[i], 0.75 * y_max, w.detailed_status, ha="center", va="center", rotation=90, color="black", alpha=0.5)

        one_hour = datetime.timedelta(hours=1)
        left_axis.xaxis.set_major_locator(mdates.HourLocator(interval=4, tz=tz))
        left_axis.xaxis.set_major_formatter(mdates.DateFormatter("%I%p" if os.name == "nt" else "%-I%p", tz=tz))
        left_axis.set_xlim(min(hours) - one_hour, max(hours) + one_hour)
        plt.setp(left_axis.get_xticklabels(), rotation=30, horizontalalignment="right")
        figure.tight_layout()
        plt.savefig("weather.png", facecolor="ghostwhite")
        return "weather.png"
