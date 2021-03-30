import os
import pyowm
from pyowm.utils import config
from discord.ext import commands

degrees = "\N{DEGREE SIGN}C"


class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.owm_client = None
        self.db = {}

    def owm(self) -> pyowm.OWM:
        if self.owm_client is None:
            conf = config.get_default_config_for_subscription_type("free")
            self.owm_client = pyowm.OWM(os.getenv("OPENWEATHER_TOKEN"), conf)
        return self.owm_client

    @commands.command(name="weather")
    async def weather_command(self, context, *args):
        await self.weather(context, *args)

    async def weather(self, context, *args):
        try:
            if len(args) > 0:
                command = args[0]
                if command == "set":
                    return await self.set_weather(context, *args[1:])
            return await self.get_weather(context, *args)
        except:
            await context.send("Iunno. Figure it out.")

    async def set_weather(self, context, *args):
        city = await self.get_location(context, *args)
        if city is not None:
            self.db[context.author.id] = city
            await context.send(f"Location saved! {self.__city_string(city)}")

    async def get_location(self, context, *args):
        if len(args) > 0:
            cities = self.owm().city_id_registry()
            city = args[0]
            country = args[1].upper() if len(args) > 1 else None
            if country is not None and len(country) != 2:
                await context.send("Country must be an ISO country code, such as CA for Canada.")
                return None
            locations = cities.locations_for(city, country=country)
            if not locations:
                await context.send("No cities found for city search")
                return None
            elif len(locations) > 1:
                if len(args) > 2:
                    index = args[2]
                    return locations[int(index) - 1]
                else:
                    message = "Multiple cities found for search, narrow your search or specify an index for the following:\n"
                    options = [f"{i+1}: {self.__city_string(city)}" for i, city in enumerate(locations)]
                    await context.send(message + "\n".join(options))
                    return None
            else:
                return locations[0]
        else:
            await context.send("Not enough arguments to determine weather location, see https://github.com/Chippers255/duckbot/wiki#weather")
            return None

    def __city_string(self, city):
        return f"{city.name}, {city.country}, geolocation = ({city.lat}, {city.lon})"

    async def get_weather(self, context, *args):
        city = None
        if not args:
            if context.author.id in self.db:
                city = self.db[context.author.id]
            else:
                await context.send("Set a default location using !weather set city country-code")
        else:
            city = await self.get_location(context, *args)
        if city is not None:
            weather = self.owm().weather_manager().one_call(lat=city.lat, lon=city.lon, exclude="minutely,hourly", units="metric")
            await context.send(self.weather_message(city, weather))

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
        elif rain_chance and self.__is_snowy(today):
            messages.append("Time to hire the old man down the street to shovel the driveway.")
        elif temp_today["max"] < -10:
            messages.append("Thankfully, I don't feel the cold.")
        elif temp_today["max"] > 35:
            messages.append("I might need to take a break today, it hot.")
        return " ".join(messages)

    def __is_rainy(self, weather):
        return "rain" in weather.status.lower() or "rain" in weather.detailed_status.lower()

    def __is_snowy(self, weather):
        return "snow" in weather.status.lower() or "snow" in weather.detailed_status.lower()
