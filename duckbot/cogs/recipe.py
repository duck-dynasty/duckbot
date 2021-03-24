import re
import random
import urllib
from bs4 import BeautifulSoup
from discord.ext import commands


class Recipe(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def select_recipe(recipe_list):
        """Given a list of recipes, select a random one."""
        return random.choice(recipe_list)

    @staticmethod
    def parse_recipes(html_content):
        """Parse raw HTML from allrecipes to find a list of recipes."""
        recipe_list = []
        soup = BeautifulSoup(html_content, 'html.parser')

        articles = soup.findAll("article", {"class": "fixed-recipe-card"})

        for article in articles:
            data = {}
            try:
                data["name"] = article.find("h3", {"class": "fixed-recipe-card__h3"}).get_text().strip(' \t\n\r')
                data["description"] = article.find("div", {"class": "fixed-recipe-card__description"}).get_text().strip(' \t\n\r')
                data["url"] = article.find("a", href=re.compile('^https://www.allrecipes.com/recipe/'))['href']

                try:
                    data["rating"] = float(article.find("div", {"class": "fixed-recipe-card__ratings"}).find("span")["data-ratingstars"])
                except ValueError:
                    data["rating"] = None

                recipe_list.append(data)
            except Exception:
                pass

        return recipe_list

    @staticmethod
    def search_recipes(search_term):
        """Search allrecipes with a given search term then return html data."""

        query_dict = {"wt": search_term}
        query_url = urllib.parse.urlencode(query_dict)
        url = f"https://allrecipes.com/search/results/?{query_url}"

        req = urllib.request.Request(url)
        req.add_header('Cookie', 'euConsent=true')

        html_content = urllib.request.urlopen(req).read()

        return html_content

    async def __recipe(self, context, *args):
        # clean up the arguments to make a valid recipe search
        search_term = ' '.join(args)
        search_term = re.sub(r'[^\w\s]', '', search_term)

        # search for recipes on allrecipes.com
        html_content = self.search_recipes(search_term)

        # parse the html to get all recipes from the search
        recipe_list = self.parse_recipes(html_content)

        if recipe_list is None:
            response = f"I am terribly sorry. There doesn't seem to be any recipes for {search_term}."
        else:
            recipe = self.select_recipe(recipe_list)
            response = f"How about a nice {recipe['name']}. {recipe['description']} This recipe has a {recipe['rating']:.2} rating! {recipe['url']}"

        await context.send(response)

    @commands.command(name="recipe")
    async def recipe(self, context, *args):
        await self.__recipe(context, *args)
