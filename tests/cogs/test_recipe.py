import pytest
import mock
from async_mock_ext import patch_async_mock
from duckmock.urllib import patch_urlopen
from cogs.recipe import Recipe

URLOPEN = "urllib.request.urlopen"


@pytest.mark.asyncio
@patch_async_mock
@mock.patch('discord.ext.commands.Bot')
async def test_search_with_result(bot):
    mock_data = {
        "name": "test_1",
         "description": "This is the first test recipe.",
         "url": "this-is-a-test-1",
         "rating": 4.7
    }
    with patch_urlopen(with_content(mock_data)):
        search_term = "test1"
        clazz = Recipe(bot)
        a_tasty_meal = clazz.search(search_term)
        assert a_tasty_meal == f"""How about a nice {mock_data["name"]}. {mock_data["description"]} This recipe has a {mock_data["rating"]} rating! https://www.allrecipes.com/recipe/10759/{mock_data["url"]}/"""


@pytest.mark.asyncio
@patch_async_mock
@mock.patch('discord.ext.commands.Bot')
async def test_search_with_result(bot):
    with patch_urlopen(without_content()):
        search_term = "test2"
        clazz = Recipe(bot)
        a_tasty_meal = clazz.search(search_term)
        assert a_tasty_meal == f"I am terribly sorry. There doesn't seem to be any recipes for {search_term}."


def with_content(*args):
    html = "<html>"
    for a in args:
        html += f"""
<article class="fixed-recipe-card">
	<img src="https://pubads.g.doubleclick.net/gampad/ad?iu=/3865/DFP_1x1_impression_tracker&amp;sz=1x1&amp;t=adpartner%3Dallrecipesmagazine_earned_impression&amp;c=47296729-323f-4f6d-bda9-2581f95b921e">
	<a ng-class="{{ highlighted : saved }}" title="Save this recipe" data-ng-show="showHeart" class="favorite ng-isolate-scope" data-id="10759" data-type="'Recipe'" data-name="&quot;Oatmeal Peanut Butter Cookies III&quot;" data-segmentpageproperties="segmentContentInfo" data-imageurl="'https://images.media-allrecipes.com/userphotos/300x300/591345.jpg'"><span class="ng-binding"></span></a>
	<div class="grid-card-image-container">
        	<a href="https://www.allrecipes.com/recipe/10759/{a["url"]}/" data-content-provider-id="" data-internal-referrer-link="hub recipe" data-click-id="cardslot 2" class="ng-isolate-scope" target="_self">
			<img class="fixed-recipe-card__img ng-isolate-scope" data-lazy-load="" data-original-src="https://images.media-allrecipes.com/userphotos/300x300/591345.jpg" alt="Oatmeal Peanut Butter Cookies III Recipe and Video - These are so close to the Girl Scout oatmeal peanut butter cookies that you  won't know the difference!" title="Oatmeal Peanut Butter Cookies III Recipe and Video" src="https://images.media-allrecipes.com/userphotos/300x300/591345.jpg" style="display: inline;">
	        </a>
            	<a href="https://www.allrecipes.com/video/3120/{a["url"]}/" data-content-provider-id="" data-internal-referrer-link="hub recipe" data-click-id="cardslot 2" class="ng-isolate-scope" target="_self">
                	<span class="watchButton">
                    		<span class="watchButton__text">WATCH</span>
	                </span>
        	</a>
    	</div>
    	<div class="fixed-recipe-card__info">
        	<h3 class="fixed-recipe-card__h3">
            		<a href="https://www.allrecipes.com/recipe/10759/{a["url"]}/" data-content-provider-id="" data-internal-referrer-link="hub recipe" class="fixed-recipe-card__title-link ng-isolate-scope" target="_self">
                		<span class="fixed-recipe-card__title-link">{a["name"]}</span>
            		</a>
        	</h3>
        	<a href="https://www.allrecipes.com/recipe/10759/{a["url"]}/" data-content-provider-id="" data-internal-referrer-link="hub recipe" class="ng-isolate-scope" target="_self">
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


def without_content():
    return "<html></html>"
