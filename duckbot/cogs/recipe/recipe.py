import random
import re

import requests
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
        soup = BeautifulSoup(html_content, "html.parser")

        articles = soup.findAll("div", {"class": "component card card__recipe card__facetedSearchResult"})

        for article in articles:
            data = {}
            try:
                data["name"] = article.find("h3", {"class": "card__title"}).get_text().strip(" \t\n\r")
                data["description"] = article.find("div", {"class": "card__summary"}).get_text().strip(" \t\n\r")
                data["url"] = article.find("a", href=re.compile(r"^https://www\.allrecipes\.com/recipe/"))["href"]
                data["rating"] = len(article.findAll("span", {"class": "rating-star active"}))

                recipe_list.append(data)
            except Exception:
                pass

        return recipe_list

    @staticmethod
    def search_recipes(search_term):
        """Search allrecipes with a given search term then return html data."""

        html_content = ""
        for page in range(1, 6):
            url = "https://www.allrecipes.com/element-api/content-proxy/faceted-searches-load-more"
            result = requests.get(url, params={"search": search_term, "page": page}, headers={"Cookie": "euConsent=true"}).json()
            html_content += result.get("html", "")

            if not result.get("hasNext", False):
                break

        return html_content

    async def recipe(self, context, search_term):
        # clean up the arguments to make a valid recipe search
        search_term = re.sub(r"[^\w\s]", "", search_term)

        try:
            # search for recipes on allrecipes.com
            html_content = self.search_recipes(search_term)

            # parse the html to get all recipes from the search
            recipe_list = self.parse_recipes(html_content)

            if len(recipe_list) == 0:
                response = f"I am terribly sorry. There doesn't seem to be any recipes for {search_term}."
            else:
                recipe = self.select_recipe(recipe_list)
                response = f"How about a nice {recipe['name']}. {recipe['description']} This recipe has a {recipe['rating']}/5 rating! {recipe['url']}"
        except Exception:
            response = "I am terribly sorry. I am having problems reading All Recipes for you."

        await context.send(response)

    @commands.command(name="recipe")
    async def recipe_command(self, context, *, search_term: str = ""):
        async with context.typing():
            await self.recipe(context, search_term)
