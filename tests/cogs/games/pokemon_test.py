import random
from datetime import date
from unittest.mock import patch

from duckbot.cogs.games.pokemon import ANCHOR_DATE, POTD_SEED, Pokemon

POKEMON_API = "https://pokeapi.co/api/v2/pokemon"
SPECIES_API = "https://pokeapi.co/api/v2/pokemon-species"


async def test_pokemon_by_name(bot, context, responses):
    responses.add(responses.GET, f"{POKEMON_API}/pikachu", json=build_pokemon_data())
    responses.add(responses.GET, f"{SPECIES_API}/25/", json=build_species_data())
    clazz = Pokemon(bot)
    await clazz.pokemon(context, "pikachu")
    context.send.assert_called_once()
    embed = context.send.call_args.kwargs["embed"]
    assert embed.title == "#25 \u2014 Pikachu"


async def test_pokemon_by_id(bot, context, responses):
    responses.add(responses.GET, f"{POKEMON_API}/25", json=build_pokemon_data())
    responses.add(responses.GET, f"{SPECIES_API}/25/", json=build_species_data())
    clazz = Pokemon(bot)
    await clazz.pokemon(context, "25")
    context.send.assert_called_once()
    embed = context.send.call_args.kwargs["embed"]
    assert embed.title == "#25 \u2014 Pikachu"


async def test_pokemon_no_args_shows_potd(bot, context, responses):
    n = 10
    ids = list(range(1, n + 1))
    random.Random(POTD_SEED).shuffle(ids)
    potd_id = ids[0]
    responses.add(responses.GET, f"{SPECIES_API}?limit=1", json={"count": n})
    responses.add(responses.GET, f"{POKEMON_API}/{potd_id}", json=build_pokemon_data(name="testmon", pokemon_id=potd_id))
    responses.add(responses.GET, f"{SPECIES_API}/{potd_id}/", json=build_species_data(pokemon_id=potd_id))
    clazz = Pokemon(bot)
    with patch("duckbot.cogs.games.pokemon.date") as mock_date:
        mock_date.today.return_value = ANCHOR_DATE
        mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
        await clazz.pokemon(context, None)
    context.send.assert_called_once()
    embed = context.send.call_args.kwargs["embed"]
    assert "Pokemon of the Day:" in embed.title


async def test_pokemon_not_found(bot, context, responses):
    responses.add(responses.GET, f"{POKEMON_API}/fakemon", status=404)
    clazz = Pokemon(bot)
    await clazz.pokemon(context, "fakemon")
    context.send.assert_called_once_with("Could not find a Pokemon named 'fakemon'.")


def test_build_embed_has_correct_fields(bot):
    clazz = Pokemon(bot)
    data = build_pokemon_data()
    species = build_species_data()
    embed = clazz.build_embed(data, species)
    assert embed.title == "#25 \u2014 Pikachu"
    assert "Mouse Pokemon" in embed.description
    assert "A Pokemon. It is cool." in embed.description
    assert len(embed.fields) == 3
    assert embed.fields[0].name == "Type"
    assert embed.fields[0].value == "Electric"
    assert embed.fields[1].name == "Height / Weight"
    assert embed.fields[1].value == "0.4 m / 6.0 kg"
    assert embed.fields[2].name == "Base Stats"
    assert "HP: 35" in embed.fields[2].value
    assert embed.thumbnail.url == "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png"


def test_build_embed_potd_title(bot):
    clazz = Pokemon(bot)
    data = build_pokemon_data()
    species = build_species_data()
    embed = clazz.build_embed(data, species, is_potd=True)
    assert embed.title == "Pokemon of the Day: #25 \u2014 Pikachu"


def test_build_embed_dual_type(bot):
    clazz = Pokemon(bot)
    types = [{"slot": 1, "type": {"name": "fire"}}, {"slot": 2, "type": {"name": "flying"}}]
    data = build_pokemon_data(name="charizard", pokemon_id=6, types=types)
    species = build_species_data(pokemon_id=6)
    embed = clazz.build_embed(data, species)
    assert embed.fields[0].value == "Fire / Flying"
    assert embed.color.value == 0xEE8130


def test_build_embed_color_from_primary_type(bot):
    clazz = Pokemon(bot)
    data = build_pokemon_data()
    species = build_species_data()
    embed = clazz.build_embed(data, species)
    assert embed.color.value == 0xF7D02C


def test_clean_flavor_text():
    assert Pokemon.clean_flavor_text("Hello\fworld\nfoo\rbar") == "Hello world foo bar"


def test_clean_flavor_text_no_artifacts():
    assert Pokemon.clean_flavor_text("Already clean text.") == "Already clean text."


def test_get_flavor_text_returns_english():
    species = build_species_data(flavor_text="A cool\fPokemon.")
    result = Pokemon.get_flavor_text(species)
    assert result == "A cool Pokemon."


def test_get_flavor_text_no_english_returns_fallback():
    species = {"flavor_text_entries": [{"flavor_text": "Japanese", "language": {"name": "ja"}, "version": {"name": "red"}}]}
    result = Pokemon.get_flavor_text(species)
    assert result == "It eats people."


def test_get_flavor_text_empty_entries():
    result = Pokemon.get_flavor_text({"flavor_text_entries": []})
    assert result == "It eats people."


def test_get_genus_returns_english():
    species = build_species_data(genus="Mouse Pokemon")
    result = Pokemon.get_genus(species)
    assert result == "Mouse Pokemon"


def test_get_genus_no_english_returns_empty():
    species = {"genera": [{"genus": "Japanese", "language": {"name": "ja"}}]}
    result = Pokemon.get_genus(species)
    assert result == ""


def test_potd_deterministic(bot):
    clazz = Pokemon(bot)
    clazz._pokemon_count = 1025
    with patch("duckbot.cogs.games.pokemon.date") as mock_date:
        mock_date.today.return_value = date(2025, 6, 15)
        mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
        id1 = clazz._get_pokemon_of_the_day_id()
        id2 = clazz._get_pokemon_of_the_day_id()
    assert id1 == id2
    assert 1 <= id1 <= 1025


def test_potd_different_days_give_different_pokemon(bot):
    clazz = Pokemon(bot)
    clazz._pokemon_count = 1025
    with patch("duckbot.cogs.games.pokemon.date") as mock_date:
        mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
        mock_date.today.return_value = date(2025, 6, 15)
        id1 = clazz._get_pokemon_of_the_day_id()
        mock_date.today.return_value = date(2025, 6, 16)
        id2 = clazz._get_pokemon_of_the_day_id()
    assert id1 != id2


def test_pokemon_count_cached(bot, responses):
    responses.add(responses.GET, f"{SPECIES_API}?limit=1", json={"count": 1025})
    clazz = Pokemon(bot)
    count1 = clazz.pokemon_count
    count2 = clazz.pokemon_count
    assert count1 == count2 == 1025
    assert len(responses.calls) == 1


def test_pokemon_names_cached(bot, responses):
    responses.add(responses.GET, f"{SPECIES_API}?limit=1", json={"count": 3})
    responses.add(responses.GET, f"{SPECIES_API}?limit=3", json={"results": [{"name": "bulbasaur"}, {"name": "ivysaur"}, {"name": "venusaur"}]})
    clazz = Pokemon(bot)
    names1 = clazz.pokemon_names
    names2 = clazz.pokemon_names
    assert names1 == names2 == ["bulbasaur", "ivysaur", "venusaur"]
    assert len(responses.calls) == 2  # one for count, one for names


async def test_autocomplete_returns_matches(bot, responses):
    responses.add(responses.GET, f"{SPECIES_API}?limit=1", json={"count": 3})
    responses.add(responses.GET, f"{SPECIES_API}?limit=3", json={"results": [{"name": "pikachu"}, {"name": "pichu"}, {"name": "bulbasaur"}]})
    clazz = Pokemon(bot)
    results = await clazz.pokemon_name_autocomplete(None, "pik")
    assert len(results) == 1
    assert results[0].name == "pikachu"


async def test_autocomplete_short_input_returns_empty(bot):
    clazz = Pokemon(bot)
    results = await clazz.pokemon_name_autocomplete(None, "pi")
    assert results == []


async def test_autocomplete_max_25_results(bot, responses):
    responses.add(responses.GET, f"{SPECIES_API}?limit=1", json={"count": 30})
    names = [{"name": f"pokemon{i}"} for i in range(30)]
    responses.add(responses.GET, f"{SPECIES_API}?limit=30", json={"results": names})
    clazz = Pokemon(bot)
    results = await clazz.pokemon_name_autocomplete(None, "pok")
    assert len(results) == 25


def build_pokemon_data(name="pikachu", pokemon_id=25, types=None, stats=None):
    if types is None:
        types = [{"slot": 1, "type": {"name": "electric"}}]
    if stats is None:
        stats = [
            {"base_stat": 35, "stat": {"name": "hp"}},
            {"base_stat": 55, "stat": {"name": "attack"}},
            {"base_stat": 40, "stat": {"name": "defense"}},
            {"base_stat": 50, "stat": {"name": "special-attack"}},
            {"base_stat": 50, "stat": {"name": "special-defense"}},
            {"base_stat": 90, "stat": {"name": "speed"}},
        ]
    return {
        "id": pokemon_id,
        "name": name,
        "types": types,
        "stats": stats,
        "height": 4,
        "weight": 60,
        "species": {"url": f"https://pokeapi.co/api/v2/pokemon-species/{pokemon_id}/"},
        "sprites": {
            "front_default": f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{pokemon_id}.png",
        },
    }


def build_species_data(pokemon_id=25, flavor_text="A Pokemon.\fIt is cool.", genus="Mouse Pokemon"):
    return {
        "id": pokemon_id,
        "flavor_text_entries": [
            {"flavor_text": "Japanese text", "language": {"name": "ja"}, "version": {"name": "red"}},
            {"flavor_text": flavor_text, "language": {"name": "en"}, "version": {"name": "red"}},
        ],
        "genera": [
            {"genus": "Japanese genus", "language": {"name": "ja"}},
            {"genus": genus, "language": {"name": "en"}},
        ],
    }
