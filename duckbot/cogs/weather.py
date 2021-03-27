import urllib.request
from bs4 import BeautifulSoup
from discord.ext import commands, tasks
import request
import json

class Weather(commands.Cog):

      @commands.Cog.listener('on_message')
      async def correct_typos(self, message):
            """Fetch weather details"""
            if message.content.strip().lower() == "!weather":
               data = await requests.get(f"http://api.openweathermap.org/data/2.5/weather?q='Helsinki'&appid=abf0d9470e7ea0b2d00f01e39a33ba5a")
               data = json.loads(data.text)
               weather = data['weather'][0]['description']
               await message.channel.send(f"Weather Details of Helsinki {weather}")
