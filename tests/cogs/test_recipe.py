import pytest
import mock
from async_mock_ext import patch_async_mock
from duckmock.urllib import patch_urlopen
from cogs.recipe import Recipe


def get_mock_data(name, rating):
    return {
        "name": name,
        "description": f"This is the {name} recipe.",
        "url": f"https://www.allrecipes.com/recipe/10759/{name}/",
        "rating": rating
    }


@pytest.mark.asyncio
@patch_async_mock
@mock.patch('discord.ext.commands.Bot')
async def test_search_recipes_returns_scraped_html(bot):
    mock_data = get_mock_data("test1", 4.7)
    with patch_urlopen(with_articles(mock_data)):
        search_term = "test1"
        clazz = Recipe(bot)
        response = clazz.search_recipes(search_term)
        assert response == with_articles(mock_data)


@pytest.mark.asyncio
@patch_async_mock
@mock.patch('discord.ext.commands.Bot')
async def test_parse_recipes_returns_articles(bot):
    mock_data = get_mock_data("test1", 4.7)
    expected_response = [get_mock_data("test1", 4.7)]
    html = with_articles(mock_data)
    clazz = Recipe(bot)
    response = clazz.parse_recipes(html)
    assert response == expected_response


@pytest.mark.asyncio
@patch_async_mock
@mock.patch('discord.ext.commands.Bot')
async def test_parse_recipes_returns_empty(bot):
    expected_response = []
    html = without_articles()
    clazz = Recipe(bot)
    response = clazz.parse_recipes(html)
    assert response == expected_response


@pytest.mark.asyncio
@patch_async_mock
@mock.patch('discord.ext.commands.Bot')
async def test_parse_recipes_no_content_returns_empty(bot):
    expected_response = []
    html = without_content()
    clazz = Recipe(bot)
    response = clazz.parse_recipes(html)
    assert response == expected_response


@pytest.mark.asyncio
@patch_async_mock
@mock.patch('discord.ext.commands.Bot')
async def test_select_recipes_with_one_return_one(bot):
    recipe_list = [get_mock_data("test1", 4.7)]
    clazz = Recipe(bot)
    response = clazz.select_recipe(recipe_list)
    assert response == recipe_list[0]


@pytest.mark.asyncio
@patch_async_mock
@mock.patch('discord.ext.commands.Bot')
async def test_select_recipes_with_many_return_one(bot):
    recipe_list = [get_mock_data("test1", 4.7), get_mock_data("test2", 4.9)]
    clazz = Recipe(bot)
    response = clazz.select_recipe(recipe_list)
    assert response in recipe_list


@pytest.mark.asyncio
@patch_async_mock
@mock.patch('discord.ext.commands.Bot')
@mock.patch('discord.ext.commands.Context')
async def test_command_with_content_return_recipe(bot, context):
    mock_data = get_mock_data("test1", 4.7)
    expected_response = f"How about a nice {mock_data['name']}. {mock_data['description']} This recipe has a {mock_data['rating']:.2} rating! {mock_data['url']}"
    with patch_urlopen(with_articles(mock_data)):
        search_term = "test1"
        clazz = Recipe(bot)
        await clazz._Recipe__recipe(context, search_term)
        context.send.assert_called_once_with(expected_response)


@pytest.mark.asyncio
@patch_async_mock
@mock.patch('discord.ext.commands.Bot')
@mock.patch('discord.ext.commands.Context')
async def test_command_without_content_return_sorry(bot, context):
    with patch_urlopen(without_content()):
        search_term = "test1"
        expected_response = f"I am terribly sorry. There doesn't seem to be any recipes for {search_term}."
        clazz = Recipe(bot)
        await clazz._Recipe__recipe(context, search_term)
        context.send.assert_called_once_with(expected_response)


def with_articles(*args):
    html = "<html>"
    for a in args:
        html += f"""
<article class="fixed-recipe-card">
    <img src="https://pubads.g.doubleclick.net/gampad/ad?iu=/3865/DFP_1x1_impression_tracker&amp;sz=1x1&amp;t=adpartner%3Dallrecipesmagazine_earned_impression&amp;c=47296729-323f-4f6d-bda9-2581f95b921e">
    <a ng-class="{{ highlighted : saved }}" title="Save this recipe" data-ng-show="showHeart" class="favorite ng-isolate-scope" data-id="10759" data-type="'Recipe'" data-name="&quot;Oatmeal Peanut Butter Cookies III&quot;" data-segmentpageproperties="segmentContentInfo" data-imageurl="'https://images.media-allrecipes.com/userphotos/300x300/591345.jpg'"><span class="ng-binding"></span></a>
    <div class="grid-card-image-container">
            <a href="{a["url"]}" data-content-provider-id="" data-internal-referrer-link="hub recipe" data-click-id="cardslot 2" class="ng-isolate-scope" target="_self">
            <img class="fixed-recipe-card__img ng-isolate-scope" data-lazy-load="" data-original-src="https://images.media-allrecipes.com/userphotos/300x300/591345.jpg" alt="Oatmeal Peanut Butter Cookies III Recipe and Video - These are so close to the Girl Scout oatmeal peanut butter cookies that you  won't know the difference!" title="Oatmeal Peanut Butter Cookies III Recipe and Video" src="https://images.media-allrecipes.com/userphotos/300x300/591345.jpg" style="display: inline;">
            </a>
                <a href="{a["url"]}" data-content-provider-id="" data-internal-referrer-link="hub recipe" data-click-id="cardslot 2" class="ng-isolate-scope" target="_self">
                    <span class="watchButton">
                            <span class="watchButton__text">WATCH</span>
                    </span>
            </a>
        </div>
        <div class="fixed-recipe-card__info">
            <h3 class="fixed-recipe-card__h3">
                    <a href="{a["url"]}" data-content-provider-id="" data-internal-referrer-link="hub recipe" class="fixed-recipe-card__title-link ng-isolate-scope" target="_self">
                        <span class="fixed-recipe-card__title-link">{a["name"]}</span>
                    </a>
            </h3>
            <a href="{a["url"]}" data-content-provider-id="" data-internal-referrer-link="hub recipe" class="ng-isolate-scope" target="_self">
                    <div class="fixed-recipe-card__ratings">
                        <span class="stars stars-5" onclick="AnchorScroll('reviews')" data-ratingstars="{a["rating"]}" aria-label="Rated 4.79 out of 5 stars"></span>
                <span class="fixed-recipe-card__reviews">1K</span>
                    </div>
                    <div data-ellipsis="" class="fixed-recipe-card__description ng-isolate-scope">{a["description"]}</div>
            </a>
            <div class="fixed-recipe-card__profile">
                    <a href="https://www.allrecipes.com/cook/jreaney@redrose.net/" data-content-provider-id="" data-internal-referrer-link="hub recipe" class="ng-isolate-scope" target="_self">
                            <ul class="cook-submitter-info">
                                    <li>
                                        <img class="cook-img" alt="profile image" src="https://images.media-allrecipes.com/userphotos/50x50/5677172.jpg">
                                    </li>
                                    <li>
                                        <h4><span>By</span> Joanne Reaney</h4>
                                    </li>
                            </ul>
                        </a>
            </div>
    </div>
</article>"""
    return html + "</html>"


def without_articles():
    return """<html><article class="fixed-recipe-card"></article></html>"""


def without_content():
    return "<html></html>"
