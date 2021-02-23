from discord.ext import commands
import random
from bs4 import BeautifulSoup

import urllib.parse
import urllib.request
import random
import re


class Recipe(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def __search(query_dict):
        """
        Search recipes parsing the returned html data.
        """
        base_url = "https://allrecipes.com/search/results/?"
        query_url = urllib.parse.urlencode(query_dict)

        url = base_url + query_url

        req = urllib.request.Request(url)
        req.add_header('Cookie', 'euConsent=true')

        html_content = urllib.request.urlopen(req).read()

        soup = BeautifulSoup(html_content, 'html.parser')

        search_data = []
        articles = soup.findAll("article", {"class": "fixed-recipe-card"})

        iterarticles = iter(articles)
        next(iterarticles)
        for article in iterarticles:
            data = {}
            try:
                data["name"] = article.find("h3", {"class": "fixed-recipe-card__h3"}).get_text().strip(' \t\n\r')
                data["description"] = article.find("div", {"class": "fixed-recipe-card__description"}).get_text().strip(' \t\n\r')
                data["url"] = article.find("a", href=re.compile('^https://www.allrecipes.com/recipe/'))['href']
                try:
                    data["image"] = article.find("a", href=re.compile('^https://www.allrecipes.com/recipe/')).find("img")["data-original-src"]
                except Exception as e1:
                    pass
                try:
                    data["rating"] = float(article.find("div", {"class": "fixed-recipe-card__ratings"}).find("span")["data-ratingstars"])
                except ValueError:
                    data["rating"] = None
            except Exception as e2:
                pass
            if data and "image" in data:  # Do not include if no image -> its probably an add or something you do not want in your result
                search_data.append(data)

        try:
            if len(search_data) > 0:
                a = random.choice(search_data)
                return f"How about a nice {a['name']}. {a['description']} This recipe has a {a['rating']:.2} rating! {a['url']}"
            else:
                return f"I am terribly sorry. There doesn't seem to be any recipes for {query_dict['wt']}."
        except:
            return f"This is embarassing. Something went wrong while trying to find a recipe for {query_dict['wt']}."
    
    @commands.command(name = "recipe")
    async def recipe(self, context, *args):
        a = ' '.join(args)
        s = re.sub(r'[^\w\s]', '', a)
        s = {
                "wt": s,         # Query keywords
            }

        response = self.__search(s)
        await context.send(response)
