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
        # TODO: add filtering to ensure no gluten free or vegan recipes
        return random.choice(recipe_list)

    @staticmethod
    def parse_recipes(html_content):
        recipe_list = []
        soup = BeautifulSoup(html_content, 'html.parser')

        articles = soup.findAll("article", {"class": "fixed-recipe-card"})

        for article in articles:  # if there are no articles this loop will be skipped
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
            except:
                pass

        return recipe_list

    @staticmethod
    def search_recipes(search_term):
        """Search recipes parsing the returned html data.

        Retrieves a random recipe from allrecipes based on a search term. The
        recipe html is then parsed for the required DuckBot output.

        Args:
            search_term:
                A recipe you want to search for.

        Returns:
            A dictionary of recipie data that will include a title, url, and description.

        Raises:
            some error i need to find: An error occurred connecting or retrieving html
        """

        query_dict = {"wt": search_term}
        query_url = urllib.parse.urlencode(query_dict)
        url = f"https://allrecipes.com/search/results/?{query_url}"

        req = urllib.request.Request(url)
        req.add_header('Cookie', 'euConsent=true')

        html_content = urllib.request.urlopen(req).read()

        return html_content
        
    @commands.command(name = "recipe")
    async def recipe(self, context, *args):
        # clean up the arguments to make a valid recipe search
        search_term = ' '.join(args)
        search_term = re.sub(r'[^\w\s]', '', search_term)

        # search for recipes on allrecipes.com
        html_content = self.search_recipes(search_term)

        # parse the html to get all recipes from the search
        recipe_list = self.parse_recipes(html_content)

        if len(recipe_list) == 0:
            response = f"I am terribly sorry. There doesn't seem to be any recipes for {search_term}."
        else:
            recipe = self.select_recipe(recipe_list)
            response = f"How about a nice {recipe['name']}. {recipe['description']} This recipe has a {recipe['rating']:.2} rating! {recipe['url']}"

        await context.send(response)
