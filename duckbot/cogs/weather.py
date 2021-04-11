import os
import pyowm
from pyowm.utils import config
from pyowm.weatherapi25.location import Location
from discord.ext import commands
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, BigInteger, String, Float

degrees = "\N{DEGREE SIGN}C"

Base = declarative_base()


class SavedLocation(Base):
    __tablename__ = "weather_locations"

    id = Column(BigInteger, primary_key=True)
    name = Column(String, nullable=False)
    country = Column(String, nullable=False)
    city_id = Column(BigInteger, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)


class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.owm_client = None

    def owm(self) -> pyowm.OWM:
        if self.owm_client is None:
            conf = config.get_default_config_for_subscription_type("free")
            self.owm_client = pyowm.OWM(os.getenv("OPENWEATHER_TOKEN"), conf)
        return self.owm_client

    @commands.group(name="weather", invoke_without_command=True)
    async def weather_command(self, context, city: str = None, country: str = None, index: int = None):
        await self.weather(context, city, country, index)

    async def weather(self, context, city: str, country: str, index: int):
        try:
            return await self.get_weather(context, city, country, index)
        except Exception as e:
            await context.send(f"Iunno. Figure it out.\n{e}")

    @weather_command.command(name="set", invoke_without_command=True)
    async def weather_set_command(self, context, city: str = None, country: str = None, index: int = None):
        await self.set_default_location(context, city, country, index)

    async def set_default_location(self, context, city: str, country: str, index: int):
        location = await self.search_location(context, city, country, index)
        if location is not None:
            saved_location = SavedLocation(id=context.author.id, name=location.name, country=location.country, city_id=location.id, latitude=location.lat, longitude=location.lon)
            with self.bot.get_cog("db").session(SavedLocation) as session:
                session.merge(saved_location)
                session.commit()
            await context.send(f"Location saved! {self.__location_string(location)}")

    async def search_location(self, context, city: str, country: str, index: int):
        if city is not None:
            country = country.upper() if country is not None else None
            if country is not None and len(country) != 2:
                await context.send("Country must be an ISO country code, such as CA for Canada.")
                return None
            locations = self.owm().city_id_registry().locations_for(city, country=country)
            if not locations:
                await context.send("No cities found matching search.")
                return None
            elif len(locations) > 1:
                if index is not None:
                    return locations[int(index) - 1]
                else:
                    message = "Multiple cities found matching search.\nNarrow your search or specify an index to pick one of the following:\n"
                    options = [f"{i+1}: {self.__location_string(city)}" for i, city in enumerate(locations)]
                    await context.send(message + "\n".join(options))
                    return None
            else:
                return locations[0]
        else:
            await context.send("Not enough arguments to determine weather location, see https://github.com/Chippers255/duckbot/wiki#weather")
            return None

    def __location_string(self, city):
        return f"{city.name}, {city.country}, geolocation = ({city.lat}, {city.lon})"

    async def get_weather(self, context, city: str, country: str, index: int):
        location = None
        if city is None:
            with self.bot.get_cog("db").session(SavedLocation) as session:
                saved = session.get(SavedLocation, context.author.id)
            if saved is not None:
                location = Location(name=saved.name, lon=saved.longitude, lat=saved.latitude, _id=saved.city_id, country=saved.country)
            else:
                await context.send("Set a default location using `!weather set city country-code`")
        else:
            location = await self.search_location(context, city, country, index)
        if location is not None:
            weather = self.owm().weather_manager().one_call(lat=location.lat, lon=location.lon, exclude="minutely,hourly", units="metric")
            await context.send(self.weather_message(location, weather))

    def weather_message(self, city, weather):
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
        rain_chance = today.precipitation_probability * 100
        max_today = f"{round(temp_today['max'])}{degrees} (feeling like {round(temp_today['feels_like_day'])}{degrees})"
        min_today = f"{round(temp_today['min'])}{degrees} (feeling like {round(temp_today['feels_like_night'])}{degrees})"
        if self.__is_rainy(today):
            messages.append(f"Today, you can expect a high of {max_today} and a low of {min_today}, with a {rain_chance}% chance of {today.rain['all']}mm of rain.")
        elif self.__is_snowy(today):
            messages.append(f"Today, you can expect a high of {max_today} and a low of {min_today}, with a {rain_chance}% chance of {today.snow['all']}cm of snow.")
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

    def __is_rainy(self, weather):
        return (weather.status and "rain" in weather.status.lower()) or (weather.detailed_status and "rain" in weather.detailed_status.lower())

    def __is_snowy(self, weather):
        return (weather.status and "snow" in weather.status.lower()) or (weather.detailed_status and "snow" in weather.detailed_status.lower())
