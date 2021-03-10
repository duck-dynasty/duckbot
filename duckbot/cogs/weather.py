import os
from pyowm import OWM
from pyowm.utils import config, timestamps
from discord.ext import commands

class Weather(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.owm_client = None

    def owm(self):
        if self.owm_client is None:
            conf = config.get_default_config_for_subscription_type('free')
            self.openweather = OWM(os.environ["OPENWEATHER_TOKEN"], conf)
            self.owm_client = self.openweather.weather_manager()
        return self.owm_client

    @commands.command(name="weather")
    async def weather(self, context, *args):
        print(self.owm().forecast_at_place('Toronto,ON,CA', '3h').get_weather_at(timestamps.now()))
