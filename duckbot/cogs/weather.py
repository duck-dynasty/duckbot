import os
from pyowm import OWM
from pyowm.utils import config, timestamps
from datetime import datetime, timedelta
import pytz
from discord.ext import commands

class Weather(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.tz = pytz.timezone("US/Eastern")
        self.owm_client = None

    def owm(self):
        if self.owm_client is None:
            conf = config.get_default_config_for_subscription_type('free')
            self.openweather = OWM(os.environ["OPENWEATHER_TOKEN"], conf)
            self.owm_client = self.openweather.weather_manager()
        return self.owm_client

    @commands.command(name="weather")
    async def weather(self, context, *args):
        weather = self.owm().weather_at_place('Toronto,ON,CA').weather
        min, max = self.__get_min_max_temp(weather)
        print(weather)
        print(min, max)
        forecaster = self.owm().forecast_at_place('Toronto,ON,CA', '3h')
        print(forecaster.when_starts('iso'), forecaster.when_ends('iso'))
        print(self.__get_min_max_temp(forecaster.get_weather_at(timestamps.next_three_hours())))

        for time in self.__get_times():
            print(self.__get_min_max_temp(forecaster.get_weather_at(time)))

    def __get_min_max_temp(self, weather):
        temp = weather.temperature('celsius')
        return temp['temp_min'], temp['temp_max']

    def __get_times(self):
        noon = timestamps.tomorrow(12, 0) # TODO this is UTC, not eastern
        three_hours = timedelta(hours=3)
        return [
            noon - three_hours - three_hours - three_hours,
            noon - three_hours - three_hours,
            noon - three_hours,
            noon,
            noon + three_hours,
            noon + three_hours + three_hours,
            noon + three_hours + three_hours + three_hours,
        ]