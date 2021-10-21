import json

import pytest
from responses import RequestsMock, matchers

from duckbot.cogs.recipe import Recipe

RECIPE_SEARCH_URI = "https://www.allrecipes.com/element-api/content-proxy/faceted-searches-load-more"


@pytest.mark.asyncio
async def test_search_recipes_returns_scraped_html(bot, responses):
    search_term = "test1"
    mock_data = get_mock_data(search_term, 5)
    setup_responses(responses, search_term, with_articles(mock_data))
    clazz = Recipe(bot)
    response = clazz.search_recipes(search_term)
    assert response == json_articles(mock_data)
    assert_requests(responses, search_term)


@pytest.mark.asyncio
async def test_parse_recipes_returns_articles(bot):
    mock_data = get_mock_data("test1", 5)
    expected_response = [get_mock_data("test1", 5) for _ in range(5)]
    html = json_articles(mock_data)
    clazz = Recipe(bot)
    response = clazz.parse_recipes(html)
    assert response == expected_response


@pytest.mark.asyncio
async def test_parse_recipes_returns_empty(bot):
    expected_response = []
    html = without_articles()
    clazz = Recipe(bot)
    response = clazz.parse_recipes(html)
    assert response == expected_response


@pytest.mark.asyncio
async def test_parse_recipes_no_content_returns_empty(bot):
    expected_response = []
    html = without_content()
    clazz = Recipe(bot)
    response = clazz.parse_recipes(html)
    assert response == expected_response


@pytest.mark.asyncio
async def test_select_recipes_with_one_return_one(bot):
    recipe_list = [get_mock_data("test1", 5)]
    clazz = Recipe(bot)
    response = clazz.select_recipe(recipe_list)
    assert response == recipe_list[0]


@pytest.mark.asyncio
async def test_select_recipes_with_many_return_one(bot):
    recipe_list = [get_mock_data("test1", 5), get_mock_data("test2", 4)]
    clazz = Recipe(bot)
    response = clazz.select_recipe(recipe_list)
    assert response in recipe_list


@pytest.mark.asyncio
async def test_recipe_with_content_return_recipe(bot, context, responses):
    search_term = "test1"
    mock_data = get_mock_data(search_term, 5)
    expected_response = f"How about a nice {mock_data['name']}. {mock_data['description']} This recipe has a {mock_data['rating']}/5 rating! {mock_data['url']}"
    setup_responses(responses, search_term, with_articles(mock_data))
    clazz = Recipe(bot)
    await clazz.recipe(context, search_term)
    context.send.assert_called_once_with(expected_response)
    assert_requests(responses, search_term)


@pytest.mark.asyncio
async def test_recipe_without_articles_return_sorry(bot, context, responses):
    search_term = "test1"
    expected_response = f"I am terribly sorry. There doesn't seem to be any recipes for {search_term}."
    setup_responses(responses, search_term, without_articles(), num_pages=1)
    clazz = Recipe(bot)
    await clazz.recipe(context, search_term)
    context.send.assert_called_once_with(expected_response)
    assert_requests(responses, search_term, num_pages=1)


@pytest.mark.asyncio
async def test_recipe_without_content_return_sorry(bot, context, responses):
    search_term = "test1"
    expected_response = "I am terribly sorry. I am having problems reading All Recipes for you."
    setup_responses(responses, search_term, without_content(), num_pages=1)
    clazz = Recipe(bot)
    await clazz.recipe(context, search_term)
    context.send.assert_called_once_with(expected_response)
    assert_requests(responses, search_term, num_pages=1)


def setup_responses(responses: RequestsMock, search_term: str, body: str, num_pages: int = 5):
    for page in range(1, num_pages + 1):
        responses.add(
            method=responses.GET,
            url=RECIPE_SEARCH_URI,
            match=[matchers.query_param_matcher({"search": search_term, "page": str(page)})],
            match_querystring=False,
            headers={"Cookie": "euConsent=true"},
            body=body,
        )


def assert_requests(responses: RequestsMock, search_term: str, num_pages: int = 5):
    assert len(responses.calls) == num_pages
    for page in range(0, num_pages):
        assert responses.calls[page].request.url == f"{RECIPE_SEARCH_URI}?search={search_term}&page={page+1}"


def get_mock_data(name, rating):
    return {"name": name, "description": f"This is the {name} recipe.", "url": f"https://www.allrecipes.com/recipe/10759/{name}/", "rating": rating}


def with_articles(*args):
    html = '''{"html":"'''
    for a in args:
        rating = """"""
        for _ in range(a["rating"]):
            rating += """                  <span class=\\"rating-star active\\" aria-hidden=\\"true\\" data-rating=\\"1\\">
                     <svg width=\\"24\\" height=\\"24\\" viewBox=\\"0 0 24 24\\" role=\\"img\\" aria-hidden=\\"true\\" tabindex=\\"-1\\" xmlns=\\"http://www.w3.org/2000/svg\\">
                        <path class=\\"rating-star-filled\\" d=\\"M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z\\"></path>
                     </svg>
                  </span>"""
        for _ in range(a["rating"], 5):
            rating += """                  <span class=\\"rating-star\\" aria-hidden=\\"true\\" data-rating=\\"1\\">
                     <svg width=\\"24\\" height=\\"24\\" viewBox=\\"0 0 24 24\\" role=\\"img\\" aria-hidden=\\"true\\" tabindex=\\"-1\\" xmlns=\\"http://www.w3.org/2000/svg\\">
                        <path class=\\"rating-star-filled\\" d=\\"M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z\\"></path>
                     </svg>
                  </span>"""

        html += f"""<div class=\\"component card card__recipe card__facetedSearchResult\\" role=\\"listitem\\">
   <div class=\\"card__imageContainer\\">
      <a class=\\"card__titleLink manual-link-behavior\\"
         href=\\"{a["url"]}\\"
         title=\\"{a["name"]}\\"
         aria-hidden=\\"true\\"
         tabindex=\\"-1\\"
         >
         <div
            class=\\"component lazy-image lazy-image-udf  aspect_1x1
            \\"
            data-src=\\"https://imagesvc.meredithcorp.io/v3/mm/image?url&#x3D;https%3A%2F%2Fimages.media-allrecipes.com%2Fuserphotos%2F631222.jpg\\"
            data-special-crop=\\"\\"
            data-alt=\\"{a["name"]}\\"
            data-title=\\"{a["name"]}\\"
            data-shop-image=\\"false\\"
            data-original-width=\\"250\\"
            data-original-height=\\"250\\"
            data-high-density=\\"\\"
            data-main-recipe=\\"\\"
            data-crop-percentage=\\"100\\"
            data-width=\\"272\\"
            data-tracking-zone=\\"image\\"
            data-orientation=\\"\\"
            data-content-type=\\"\\"
            >
            <noscript>
               <img src=\\"https://imagesvc.meredithcorp.io/v3/mm/image?url=https%3A%2F%2Fimages.media-allrecipes.com%2Fuserphotos%2F631222.jpg\\"
                  alt=\\"{a["name"]}\\">
            </noscript>
            <div class=\\"inner-container js-inner-container \\">
            </div>
            <div class=\\"lazy-image__loadingPlaceholder\\">
               <img class=\\"loadingPlaceholder\\" alt=\\"\\" src=\\"data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%20100%20100'%3E%3C/svg%3E\\" />
            </div>
         </div>
      </a>
   </div>
   <div class=\\"card__detailsContainer\\">
      <div class=\\"card__detailsContainer-left\\">
         <a class=\\"card__titleLink manual-link-behavior\\"
            href=\\"{a["url"]}\\"
            title=\\"{a["name"]}\\"
            >
            <h3 class=\\"card__title\\">
               {a["name"]}
            </h3>
         </a>
         <div class=\\"card__ratingContainer\\">
            <div class=\\"component recipe-ratings \\">
               <div class=\\"ratings-dropdown-button\\">
                  <span class=\\"review-star-text\\">
                  Rating: Unrated
                  </span>
                  {rating}
               </div>
            </div>
            <span class=\\"card__ratingCount card__metaDetailText\\">
            1
            </span>
         </div>
         <div class=\\"card__summary\\">
            {a["description"]}
         </div>
         <div class=\\"card__author\\">
            <span class=\\"card__authorNamePrefix\\">By</span>
            <a class=\\"card__authorNameLink\\"
               href=\\"https://www.allrecipes.com/cook/45776/\\"
               title=\\"More content by JOEBON\\"
               data-tracking-content-headline=\\"{a["name"]}\\"
               data-tracking-category=\\"user action\\"
               >
            <span class=\\"card__authorName\\">JOEBON</span>
            </a>
         </div>
      </div>
   </div>
</div>""".replace(
            "\n", "\\n"
        )
    return html + """","hasNext":true,"totalResults":4624}"""


def json_articles(*args):
    content = with_articles(*args)
    result = json.loads(content)
    return result.get("html") * 5


def without_articles():
    return """{"html": "","hasNext":false,"totalResults":0}"""


def without_content():
    return ""
