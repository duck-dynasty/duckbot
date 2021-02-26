import re
import random
import urllib
from bs4 import BeautifulSoup
from discord.ext import commands


class Recipe(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def __search(search_term):
        """Search recipes parsing the returned html data.

        Retrieves a random recipe from allrecipes based on a search term. The
        recipe html is then parsed for the required DuckBot output.

        Args:
            search_term:
                A recipe you want to search for.

        Returns:
            A dictionary of recipie data that will include a title, url, and description.

        Raises:
            some error i need to find: An error occurred searching or parsing or connecting
        """
        

        query_dict = {"wt": search_term}
        query_url = urllib.parse.urlencode(query_dict)
        url = f"https://allrecipes.com/search/results/?{query_url}"

        req = urllib.request.Request(url)
        req.add_header('Cookie', 'euConsent=true')

        html_content = urllib.request.urlopen(req).read()
        soup = BeautifulSoup(html_content, 'html.parser')

        search_data = []
        articles = soup.findAll("article", {"class": "fixed-recipe-card"})

        if articles is None:
            return f"This is embarassing. Something went wrong while trying to find a recipe for {search_term}."
        elif len(articles) == 0:
            return f"I am terribly sorry. There doesn't seem to be any recipes for {search_term}."
        else:
            article = random.choice(articles)
        
        data = {}
        try:
            data["name"] = article.find("h3", {"class": "fixed-recipe-card__h3"}).get_text().strip(' \t\n\r')
            data["description"] = article.find("div", {"class": "fixed-recipe-card__description"}).get_text().strip(' \t\n\r')
            data["url"] = article.find("a", href=re.compile('^https://www.allrecipes.com/recipe/'))['href']
            try:
                data["rating"] = float(article.find("div", {"class": "fixed-recipe-card__ratings"}).find("span")["data-ratingstars"])
            except ValueError:
                data["rating"] = None
        except Exception as e2:
            return f"This is embarassing. Something went wrong while trying to find a recipe for {search_term}."

        return f"How about a nice {data['name']}. {data['description']} This recipe has a {data['rating']:.2} rating! {data['url']}"
    
    @commands.command(name = "recipe")
    async def recipe(self, context, *args):
        whole_args = ' '.join(args)
        filtered_args = re.sub(r'[^\w\s]', '', whole_args)
        response = self.__search(filtered_args)

        await context.send(response)
