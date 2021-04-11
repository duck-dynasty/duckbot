import urllib.request
from bs4 import BeautifulSoup
from discord.ext import commands, tasks
import requests
import json
from pathlib import Path
from dotenv import load_dotenv
import os
dotenv_path = Path('../.env')
load_dotenv(dotenv_path=dotenv_path)
#Fetch the city name based on user machine ip
#ip_key = os.getenv('IP_KEY')
ip_key="4b64bac52a37df8545e6eee13c52ea1"
ip="2001:2003:f9a1:dc00:d9f6:a0e4:9694:be4e"
api_key="59786cb1791e11c298bfb3536e331bc9"
ip_url = "https://api.ipstack.com/"+ip+"access_key="+ip_key
response = requests.get(ip_url).json()
city = response['city'] 
#city is taken by default Vienna as the ipurl
#not working until and unless .env stores the keys in user local
#city = 'Vienna'
class Weather(commands.Cog):

      @commands.Cog.listener('on_message')
      async def get_weather(self, message):
            """Fetch weather details"""
            if message.content.strip().lower() == "!weather":
               data = await requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}")
               data = json.loads(data.text)
               temp = data['main']['temp']
               desc = data['weather'][0]['description']
               await message.channel.send(f"{city} has temperature {temp} and most probably {desc}")
