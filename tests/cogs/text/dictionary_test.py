import discord
import pytest

from duckbot.cogs.text import Dictionary

HEADERS = {"app_id": "app-id", "app_key": "app-key"}
LEMMAS_URI = "https://od-api.oxforddictionaries.com/api/v2/lemmas/en"
ENTRIES_URI = "https://od-api.oxforddictionaries.com/api/v2/entries/en-us"


@pytest.fixture(autouse=True)
def set_oxford_token_env(monkeypatch):
    monkeypatch.setenv("OXFORD_DICTIONARY_ID", HEADERS["app_id"])
    monkeypatch.setenv("OXFORD_DICTIONARY_KEY", HEADERS["app_key"])


async def test_define_no_root_words(bot, context, responses):
    responses.add(responses.GET, f"{LEMMAS_URI}/nothing", json={"error": "No lemma was found in dictionary 'en' for the inflected form 'nothing'"})
    responses.add(responses.GET, f"{ENTRIES_URI}/why", json=why_definition())
    clazz = Dictionary(bot)
    await clazz.define(context, "nothing")
    embed = discord.Embed(title="why")
    adverb_lines = [
        "1. for what reason or purpose",
        "_why did he do it?_",
        "  • used to make or agree to a suggestion",
        "    _why don't I give you a lift?_",
        "",
        "2. (with reference to a reason) on account of which; for which",
        "_\n              the reason why flu shots need repeating every year is that the virus changes_",
        "  • the reason for which",
        "    _each has faced similar hardships, and perhaps that is why they are friends_",
        "",
    ]
    interjection_lines = [
        "1. expressing surprise or indignation",
        "_why, that's absurd!_",
        "",
        "2. used to add emphasis to a response",
        "_“You think so?” “Why, yes.”_",
        "",
    ]
    noun_lines = [
        "1. a reason or explanation",
        "_the whys and wherefores of these procedures need to be explained to students_",
        "",
    ]
    embed.add_field(name="adverb: **why**  /(h)wī/", value="\n".join(adverb_lines), inline=False)
    embed.add_field(name="interjection: **why**  /(h)wī/", value="\n".join(interjection_lines), inline=False)
    embed.add_field(name="noun: **why**  /(h)wī/", value="\n".join(noun_lines), inline=False)
    context.send.assert_called_once_with(embeds=[embed])


async def test_define_single_root_word(bot, context, responses):
    responses.add(responses.GET, f"{LEMMAS_URI}/cow", json=cow_lemma())
    responses.add(responses.GET, f"{ENTRIES_URI}/cow", json=cow_definition())
    clazz = Dictionary(bot)
    await clazz.define(context, "cow")
    embed = discord.Embed(title="cow")
    verb_lines = [
        "1. cause (someone) to submit to one's wishes by intimidation",
        "_the intellectuals had been cowed into silence_",
        "",
    ]
    noun_lines = [
        "1. a fully grown female animal of a domesticated breed of ox, kept to produce milk or beef",
        "_a dairy cow_",
        "  • (loosely) a domestic bovine animal, regardless of sex or age.",
        "  • (in farming) a female domestic bovine animal which has borne more than one calf.",
        "  • the female of certain other large animals, for example elephant, rhinoceros, whale, or seal.",
        "",
        "2. an unpleasant or disliked woman",
        "_what does he see in that cow?_",
        "  • an unpleasant person or thing.",
        "",
    ]
    embed.add_field(name="noun: **cow**  /kou/", value="\n".join(noun_lines), inline=False)
    embed.add_field(name="verb: **cow**  /kou/", value="\n".join(verb_lines), inline=False)
    context.send.assert_called_once_with(embeds=[embed])


async def test_define_multiple_root_words(bot, context, responses):
    responses.add(responses.GET, f"{LEMMAS_URI}/homing", json=homing_lemma())
    responses.add(responses.GET, f"{ENTRIES_URI}/homing", json=homing_definition())
    responses.add(responses.GET, f"{ENTRIES_URI}/home", json=home_definition())
    clazz = Dictionary(bot)
    await clazz.define(context, "homing")
    homing = discord.Embed(title="homing")
    homing_adjective_lines = [
        "1. relating to an animal's ability to return to a place or territory after traveling a distance away from it",
        "_a strong homing instinct_",
        "  • (of a pigeon) trained to fly home from a great distance and bred for long-distance racing.",
        "  • (of a weapon or piece of equipment) fitted with an electronic device that enables it to find and hit a target",
        "    _a homing missile_",
        "",
    ]
    homing.add_field(name="adjective: **homing**  /ˈhōmiNG/", value="\n".join(homing_adjective_lines), inline=False)
    home = discord.Embed(title="home")
    home_noun_lines = [
        "1. the place where one lives permanently, especially as a member of a family or household",
        "_I was nineteen when I left home and went to college_",
        "  • the family or social unit occupying a home",
        "    _he came from a good home and was well educated_",
        "  • a house or an apartment considered as a commercial property",
        "    _low-cost homes for first-time buyers_",
        "  • a place where something flourishes, is most typically found, or from which it originates",
        "    _Piedmont is the home of Italy's finest red wines_",
        "  • a place where an object is kept.",
        "",
        "2. an institution for people needing professional care or supervision",
        "_an old people's home_",
        "",
        "3. (in sports) the goal or end point",
        "_he was four fences from home_",
        "  • the place where a player is free from attack.",
        "  • (in lacrosse) each of the three players stationed nearest their opponents's goal.",
        "  • a game played or won by a team on their own field or court.",
        "",
    ]
    home_adjective_lines = [
        "1. relating to the place where one lives",
        "_I don't have your home address_",
        "  • made, done, or intended for use in the place where one lives",
        "    _traditional home cooking_",
        "  • relating to one's own country and its domestic affairs",
        "    _Japanese competitors are selling cars for lower prices in the US than in their home market_",
        "",
        "2. (of a sports game) played at the team's own field or court",
        "_their first home game of the season_",
        "  • relating to or denoting a sports team that is playing at its own field or court",
        "    _the home team_",
        "",
        "3. denoting the administrative center of an organization",
        "_the company has moved its home office_",
        "",
    ]
    home_adverb_lines = [
        "1. to or at the place where one lives",
        "_what time did he get home last night?_",
        "  • to the end or conclusion of a race or something difficult",
        "    _the favorite romped home six lengths clear_",
        "  • to or toward home plate.",
        "  • to the intended or correct position",
        "    _he drove the bolt home noisily_",
        "",
    ]
    home_verb_lines = [
        "1. (of an animal) return by instinct to its territory after leaving it",
        "_a dozen geese homing to their summer nesting grounds_",
        "  • (of a pigeon bred for long-distance racing) fly back to or arrive at its loft after being released at a distant point",
        "    _pigeons who do not home will win no prizes_",
        "",
        "2. move or be aimed toward (a target or destination) with great accuracy",
        "_more than 100 missiles were launched, homing in on radar emissions_",
        "  • focus attention on",
        "    _a teaching style that homes in on what is of central importance for each student_",
        "",
    ]
    home.add_field(name="adjective: **home**  /hōm/", value="\n".join(home_adjective_lines), inline=False)
    home.add_field(name="adverb: **home**  /hōm/", value="\n".join(home_adverb_lines), inline=False)
    home.add_field(name="noun: **home**  /hōm/", value="\n".join(home_noun_lines), inline=False)
    home.add_field(name="verb: **home**  /hōm/", value="\n".join(home_verb_lines), inline=False)
    context.send.assert_called_once_with(embeds=[home, homing])


def homing_lemma():
    return {
        "metadata": {"provider": "Oxford University Press"},
        "results": [
            {
                "id": "homing",
                "language": "en",
                "lexicalEntries": [
                    {"inflectionOf": [{"id": "homing", "text": "homing"}], "language": "en", "lexicalCategory": {"id": "adjective", "text": "Adjective"}, "text": "homing"},
                    {"inflectionOf": [{"id": "home", "text": "home"}], "language": "en", "lexicalCategory": {"id": "verb", "text": "Verb"}, "text": "homing"},
                ],
                "word": "homing",
            }
        ],
    }


def homing_definition():
    return {
        "id": "homing",
        "metadata": {"operation": "retrieve", "provider": "Oxford University Press", "schema": "RetrieveEntry"},
        "results": [
            {
                "id": "homing",
                "language": "en-us",
                "lexicalEntries": [
                    {
                        "entries": [
                            {
                                "pronunciations": [
                                    {"dialects": ["American English"], "phoneticNotation": "respell", "phoneticSpelling": "ˈhōmiNG"},
                                    {
                                        "audioFile": "https://audio.oxforddictionaries.com/en/mp3/homing_us_1.mp3",
                                        "dialects": ["American English"],
                                        "phoneticNotation": "IPA",
                                        "phoneticSpelling": "ˈhoʊmɪŋ",
                                    },
                                ],
                                "senses": [
                                    {
                                        "definitions": ["relating to an animal's ability to return to a place or territory after traveling a distance away from it"],
                                        "domainClasses": [{"id": "zoology", "text": "Zoology"}],
                                        "examples": [{"text": "a strong homing instinct"}],
                                        "id": "m_en_gbus0475890.005",
                                        "shortDefinitions": ["relating to animal's ability to return to its territory after travelling away from it"],
                                        "subsenses": [
                                            {
                                                "definitions": ["(of a pigeon) trained to fly home from a great distance and bred for long-distance racing."],
                                                "id": "m_en_gbus0475890.007",
                                                "shortDefinitions": ["trained to fly home from great distance and bred for long-distance racing"],
                                            },
                                            {
                                                "definitions": ["(of a weapon or piece of equipment) fitted with an electronic device that enables it to find and hit a target"],
                                                "domainClasses": [{"id": "weapons", "text": "Weapons"}],
                                                "examples": [{"text": "a homing missile"}],
                                                "id": "m_en_gbus0475890.008",
                                                "shortDefinitions": ["(of weapon or piece of equipment) fitted with electronic device that enables it to find and hit target"],
                                            },
                                        ],
                                    }
                                ],
                            }
                        ],
                        "language": "en-us",
                        "lexicalCategory": {"id": "adjective", "text": "Adjective"},
                        "text": "homing",
                    }
                ],
                "type": "headword",
                "word": "homing",
            }
        ],
        "word": "homing",
    }


def home_definition():
    return {
        "id": "home",
        "metadata": {"operation": "retrieve", "provider": "Oxford University Press", "schema": "RetrieveEntry"},
        "results": [
            {
                "id": "home",
                "language": "en-us",
                "lexicalEntries": [
                    {
                        "derivatives": [{"id": "homelike", "text": "homelike"}],
                        "entries": [
                            {
                                "etymologies": ["Old English hām, of Germanic origin; related to Dutch heem and German Heim"],
                                "pronunciations": [
                                    {"dialects": ["American English"], "phoneticNotation": "respell", "phoneticSpelling": "hōm"},
                                    {"audioFile": "https://audio.oxforddictionaries.com/en/mp3/home_us_1.mp3", "dialects": ["American English"], "phoneticNotation": "IPA", "phoneticSpelling": "hoʊm"},
                                ],
                                "senses": [
                                    {
                                        "definitions": ["the place where one lives permanently, especially as a member of a family or household"],
                                        "examples": [{"text": "I was nineteen when I left home and went to college"}, {"text": "they have made Provence their home"}],
                                        "id": "m_en_gbus0474570.006",
                                        "semanticClasses": [{"id": "housing", "text": "Housing"}],
                                        "shortDefinitions": ["place where one lives permanently"],
                                        "subsenses": [
                                            {
                                                "definitions": ["the family or social unit occupying a home"],
                                                "examples": [{"text": "he came from a good home and was well educated"}],
                                                "id": "m_en_gbus0474570.009",
                                                "semanticClasses": [{"id": "family", "text": "Family"}],
                                                "shortDefinitions": ["family etc. occupying this place"],
                                            },
                                            {
                                                "definitions": ["a house or an apartment considered as a commercial property"],
                                                "examples": [{"text": "low-cost homes for first-time buyers"}],
                                                "id": "m_en_gbus0474570.010",
                                                "semanticClasses": [{"id": "housing", "text": "Housing"}],
                                                "shortDefinitions": ["flat or house"],
                                                "synonyms": [
                                                    {"language": "en", "text": "house"},
                                                    {"language": "en", "text": "apartment"},
                                                    {"language": "en", "text": "bungalow"},
                                                    {"language": "en", "text": "cottage"},
                                                    {"language": "en", "text": "terraced house"},
                                                    {"language": "en", "text": "semi-detached house"},
                                                    {"language": "en", "text": "detached house"},
                                                ],
                                                "thesaurusLinks": [{"entry_id": "home", "sense_id": "t_en_gb0007069.002"}],
                                            },
                                            {
                                                "constructions": [{"text": "home to"}],
                                                "definitions": ["a place where something flourishes, is most typically found, or from which it originates"],
                                                "examples": [{"text": "Piedmont is the home of Italy's finest red wines"}],
                                                "id": "m_en_gbus0474570.012",
                                                "semanticClasses": [{"id": "area", "text": "Area"}],
                                                "shortDefinitions": ["place where thing originates or is found"],
                                                "synonyms": [
                                                    {"language": "en", "text": "domain"},
                                                    {"language": "en", "text": "realm"},
                                                    {"language": "en", "text": "place of origin"},
                                                    {"language": "en", "text": "source"},
                                                    {"language": "en", "text": "cradle"},
                                                    {"language": "en", "text": "fount"},
                                                    {"language": "en", "text": "fountainhead"},
                                                    {"language": "en", "text": "natural habitat"},
                                                    {"language": "en", "text": "natural environment"},
                                                    {"language": "en", "text": "natural territory"},
                                                    {"language": "en", "text": "habitat"},
                                                    {"language": "en", "text": "home ground"},
                                                    {"language": "en", "text": "stamping ground"},
                                                    {"language": "en", "text": "haunt"},
                                                ],
                                                "thesaurusLinks": [{"entry_id": "home", "sense_id": "t_en_gb0007069.005"}, {"entry_id": "home", "sense_id": "t_en_gb0007069.006"}],
                                            },
                                            {
                                                "definitions": ["a place where an object is kept."],
                                                "id": "m_en_gbus0474570.013",
                                                "registers": [{"id": "informal", "text": "Informal"}],
                                                "semanticClasses": [{"id": "location", "text": "Location"}],
                                                "shortDefinitions": ["place where object is kept"],
                                                "synonyms": [
                                                    {"language": "en", "text": "natural habitat"},
                                                    {"language": "en", "text": "natural environment"},
                                                    {"language": "en", "text": "natural territory"},
                                                    {"language": "en", "text": "habitat"},
                                                    {"language": "en", "text": "home ground"},
                                                    {"language": "en", "text": "stamping ground"},
                                                    {"language": "en", "text": "haunt"},
                                                ],
                                                "thesaurusLinks": [{"entry_id": "home", "sense_id": "t_en_gb0007069.006"}],
                                            },
                                        ],
                                        "synonyms": [
                                            {"language": "en", "text": "place of residence"},
                                            {"language": "en", "text": "accommodation"},
                                            {"language": "en", "text": "property"},
                                            {"language": "en", "text": "a roof over one's head"},
                                        ],
                                        "thesaurusLinks": [{"entry_id": "home", "sense_id": "t_en_gb0007069.001"}],
                                    },
                                    {
                                        "definitions": ["an institution for people needing professional care or supervision"],
                                        "examples": [{"text": "an old people's home"}],
                                        "id": "m_en_gbus0474570.015",
                                        "semanticClasses": [{"id": "residential_facility", "text": "Residential_Facility"}],
                                        "shortDefinitions": ["institution for people needing care"],
                                        "synonyms": [
                                            {"language": "en", "text": "institution"},
                                            {"language": "en", "text": "residential home"},
                                            {"language": "en", "text": "nursing home"},
                                            {"language": "en", "text": "old people's home"},
                                            {"language": "en", "text": "retirement home"},
                                            {"language": "en", "text": "convalescent home"},
                                            {"language": "en", "text": "rest home"},
                                            {"language": "en", "text": "children's home"},
                                        ],
                                        "thesaurusLinks": [{"entry_id": "home", "sense_id": "t_en_gb0007069.004"}],
                                    },
                                    {
                                        "definitions": ["(in sports) the goal or end point"],
                                        "domainClasses": [{"id": "sport", "text": "Sport"}],
                                        "examples": [{"text": "he was four fences from home"}],
                                        "id": "m_en_gbus0474570.017",
                                        "semanticClasses": [{"id": "marked_line", "text": "Marked_Line"}],
                                        "shortDefinitions": ["finishing point in race"],
                                        "subsenses": [
                                            {
                                                "definitions": ["the place where a player is free from attack."],
                                                "domainClasses": [{"id": "sport", "text": "Sport"}],
                                                "id": "m_en_gbus0474570.018",
                                                "semanticClasses": [{"id": "playing_position", "text": "Playing_Position"}],
                                                "shortDefinitions": ["place where player is free from attack"],
                                            },
                                            {
                                                "definitions": ["(in lacrosse) each of the three players stationed nearest their opponents's goal."],
                                                "domainClasses": [{"id": "sport", "text": "Sport"}],
                                                "id": "m_en_gbus0474570.019",
                                                "semanticClasses": [{"id": "team_player", "text": "Team_Player"}],
                                                "shortDefinitions": ["each of players nearest opponents' goal in lacrosse"],
                                            },
                                            {
                                                "crossReferenceMarkers": ["short for home plate"],
                                                "crossReferences": [{"id": "home_plate", "text": "home plate", "type": "abbreviation of"}],
                                                "domains": [{"id": "baseball", "text": "Baseball"}],
                                                "id": "m_en_gbus0474570.020",
                                                "shortDefinitions": ["home plate"],
                                            },
                                            {
                                                "definitions": ["a game played or won by a team on their own field or court."],
                                                "domainClasses": [{"id": "sport", "text": "Sport"}],
                                                "id": "m_en_gbus0474570.021",
                                                "semanticClasses": [{"id": "contest", "text": "Contest"}],
                                                "shortDefinitions": ["match played by team on home ground"],
                                            },
                                        ],
                                    },
                                ],
                            }
                        ],
                        "language": "en-us",
                        "lexicalCategory": {"id": "noun", "text": "Noun"},
                        "phrases": [
                            {"id": "a_home_away_from_home", "text": "a home away from home"},
                            {"id": "at_home", "text": "at home"},
                            {"id": "bring_something_home_to", "text": "bring something home to"},
                            {"id": "close_to_home", "text": "close to home"},
                            {"id": "come_home", "text": "come home"},
                            {"id": "come_home_to_someone", "text": "come home to someone"},
                            {"id": "drive_something_home", "text": "drive something home"},
                            {"id": "hit_home", "text": "hit home"},
                            {"id": "home_and_dry", "text": "home and dry"},
                            {"id": "home_free", "text": "home free"},
                            {"id": "home_is_where_the_heart_is", "text": "home is where the heart is"},
                            {"id": "home_sweet_home", "text": "home sweet home"},
                        ],
                        "text": "home",
                    },
                    {
                        "derivatives": [{"id": "homelike", "text": "homelike"}],
                        "entries": [
                            {
                                "pronunciations": [
                                    {"dialects": ["American English"], "phoneticNotation": "respell", "phoneticSpelling": "hōm"},
                                    {"audioFile": "https://audio.oxforddictionaries.com/en/mp3/home_us_1.mp3", "dialects": ["American English"], "phoneticNotation": "IPA", "phoneticSpelling": "hoʊm"},
                                ],
                                "senses": [
                                    {
                                        "definitions": ["relating to the place where one lives"],
                                        "examples": [{"text": "I don't have your home address"}],
                                        "id": "m_en_gbus0474570.024",
                                        "shortDefinitions": ["relating to one's home"],
                                        "subsenses": [
                                            {
                                                "definitions": ["made, done, or intended for use in the place where one lives"],
                                                "examples": [{"text": "traditional home cooking"}],
                                                "id": "m_en_gbus0474570.026",
                                                "shortDefinitions": ["made, done, etc. in one's home"],
                                                "synonyms": [
                                                    {"language": "en", "text": "home-made"},
                                                    {"language": "en", "text": "home-grown"},
                                                    {"language": "en", "text": "locally produced"},
                                                    {"language": "en", "text": "family"},
                                                    {"language": "en", "text": "local"},
                                                ],
                                                "thesaurusLinks": [{"entry_id": "home", "sense_id": "t_en_gb0007069.015"}],
                                            },
                                            {
                                                "definitions": ["relating to one's own country and its domestic affairs"],
                                                "examples": [{"text": "Japanese competitors are selling cars for lower prices in the US than in their home market"}],
                                                "id": "m_en_gbus0474570.027",
                                                "shortDefinitions": ["relating to one's own country"],
                                                "synonyms": [
                                                    {"language": "en", "text": "domestic"},
                                                    {"language": "en", "text": "internal"},
                                                    {"language": "en", "text": "local"},
                                                    {"language": "en", "text": "national"},
                                                    {"language": "en", "text": "interior"},
                                                    {"language": "en", "text": "native"},
                                                ],
                                                "thesaurusLinks": [{"entry_id": "home", "sense_id": "t_en_gb0007069.014"}],
                                            },
                                        ],
                                    },
                                    {
                                        "definitions": ["(of a sports game) played at the team's own field or court"],
                                        "examples": [{"text": "their first home game of the season"}, {"text": "a home win"}],
                                        "id": "m_en_gbus0474570.029",
                                        "shortDefinitions": ["played at team's own ground"],
                                        "subsenses": [
                                            {
                                                "definitions": ["relating to or denoting a sports team that is playing at its own field or court"],
                                                "domainClasses": [{"id": "sport", "text": "Sport"}],
                                                "examples": [{"text": "the home team"}, {"text": "home fans"}],
                                                "id": "m_en_gbus0474570.030",
                                                "shortDefinitions": ["denoting sports team playing at own ground"],
                                            }
                                        ],
                                    },
                                    {
                                        "definitions": ["denoting the administrative center of an organization"],
                                        "examples": [{"text": "the company has moved its home office"}],
                                        "id": "m_en_gbus0474570.032",
                                        "regions": [{"id": "north_american", "text": "North_American"}],
                                        "shortDefinitions": ["denoting organization's administrative centre"],
                                    },
                                ],
                            }
                        ],
                        "language": "en-us",
                        "lexicalCategory": {"id": "adjective", "text": "Adjective"},
                        "phrases": [
                            {"id": "a_home_away_from_home", "text": "a home away from home"},
                            {"id": "at_home", "text": "at home"},
                            {"id": "bring_something_home_to", "text": "bring something home to"},
                            {"id": "close_to_home", "text": "close to home"},
                            {"id": "come_home", "text": "come home"},
                            {"id": "come_home_to_someone", "text": "come home to someone"},
                            {"id": "drive_something_home", "text": "drive something home"},
                            {"id": "hit_home", "text": "hit home"},
                            {"id": "home_and_dry", "text": "home and dry"},
                            {"id": "home_free", "text": "home free"},
                            {"id": "home_is_where_the_heart_is", "text": "home is where the heart is"},
                            {"id": "home_sweet_home", "text": "home sweet home"},
                        ],
                        "text": "home",
                    },
                    {
                        "derivatives": [{"id": "homelike", "text": "homelike"}],
                        "entries": [
                            {
                                "pronunciations": [
                                    {"dialects": ["American English"], "phoneticNotation": "respell", "phoneticSpelling": "hōm"},
                                    {"audioFile": "https://audio.oxforddictionaries.com/en/mp3/home_us_1.mp3", "dialects": ["American English"], "phoneticNotation": "IPA", "phoneticSpelling": "hoʊm"},
                                ],
                                "senses": [
                                    {
                                        "definitions": ["to or at the place where one lives"],
                                        "examples": [{"text": "what time did he get home last night?"}, {"text": "I stayed home with the kids"}],
                                        "id": "m_en_gbus0474570.034",
                                        "shortDefinitions": ["to one's home"],
                                        "subsenses": [
                                            {
                                                "definitions": ["to the end or conclusion of a race or something difficult"],
                                                "examples": [{"text": "the favorite romped home six lengths clear"}],
                                                "id": "m_en_gbus0474570.037",
                                                "shortDefinitions": ["to end or conclusion of race etc."],
                                            },
                                            {
                                                "definitions": ["to or toward home plate."],
                                                "domainClasses": [{"id": "baseball", "text": "Baseball"}],
                                                "domains": [{"id": "baseball", "text": "Baseball"}],
                                                "id": "m_en_gbus0474570.038",
                                                "shortDefinitions": ["to or toward home plate"],
                                            },
                                            {
                                                "definitions": ["to the intended or correct position"],
                                                "examples": [{"text": "he drove the bolt home noisily"}],
                                                "id": "m_en_gbus0474570.039",
                                                "shortDefinitions": ["to intended or correct position"],
                                            },
                                        ],
                                    }
                                ],
                            }
                        ],
                        "language": "en-us",
                        "lexicalCategory": {"id": "adverb", "text": "Adverb"},
                        "phrases": [
                            {"id": "a_home_away_from_home", "text": "a home away from home"},
                            {"id": "at_home", "text": "at home"},
                            {"id": "bring_something_home_to", "text": "bring something home to"},
                            {"id": "close_to_home", "text": "close to home"},
                            {"id": "come_home", "text": "come home"},
                            {"id": "come_home_to_someone", "text": "come home to someone"},
                            {"id": "drive_something_home", "text": "drive something home"},
                            {"id": "hit_home", "text": "hit home"},
                            {"id": "home_and_dry", "text": "home and dry"},
                            {"id": "home_free", "text": "home free"},
                            {"id": "home_is_where_the_heart_is", "text": "home is where the heart is"},
                            {"id": "home_sweet_home", "text": "home sweet home"},
                        ],
                        "text": "home",
                    },
                    {
                        "derivatives": [{"id": "homelike", "text": "homelike"}],
                        "entries": [
                            {
                                "grammaticalFeatures": [{"id": "intransitive", "text": "Intransitive", "type": "Subcategorization"}],
                                "pronunciations": [
                                    {"dialects": ["American English"], "phoneticNotation": "respell", "phoneticSpelling": "hōm"},
                                    {"audioFile": "https://audio.oxforddictionaries.com/en/mp3/home_us_1.mp3", "dialects": ["American English"], "phoneticNotation": "IPA", "phoneticSpelling": "hoʊm"},
                                ],
                                "senses": [
                                    {
                                        "definitions": ["(of an animal) return by instinct to its territory after leaving it"],
                                        "examples": [{"text": "a dozen geese homing to their summer nesting grounds"}],
                                        "id": "m_en_gbus0474570.042",
                                        "shortDefinitions": ["(of animal) return by instinct to its territory"],
                                        "subsenses": [
                                            {
                                                "definitions": ["(of a pigeon bred for long-distance racing) fly back to or arrive at its loft after being released at a distant point"],
                                                "examples": [{"text": "pigeons who do not home will win no prizes"}],
                                                "id": "m_en_gbus0474570.048",
                                                "shortDefinitions": ["(of pigeon) return after being released at distance"],
                                            }
                                        ],
                                    },
                                    {
                                        "definitions": ["move or be aimed toward (a target or destination) with great accuracy"],
                                        "examples": [{"text": "more than 100 missiles were launched, homing in on radar emissions"}],
                                        "id": "m_en_gbus0474570.050",
                                        "shortDefinitions": ["move accurately towards target"],
                                        "subsenses": [
                                            {
                                                "definitions": ["focus attention on"],
                                                "examples": [{"text": "a teaching style that homes in on what is of central importance for each student"}],
                                                "id": "m_en_gbus0474570.051",
                                                "shortDefinitions": ["focus attention on"],
                                            }
                                        ],
                                        "synonyms": [
                                            {"language": "en", "text": "focus on"},
                                            {"language": "en", "text": "focus attention on"},
                                            {"language": "en", "text": "concentrate on"},
                                            {"language": "en", "text": "zero in on"},
                                            {"language": "en", "text": "centre on"},
                                            {"language": "en", "text": "fix on"},
                                            {"language": "en", "text": "aim at"},
                                            {"language": "en", "text": "highlight"},
                                            {"language": "en", "text": "spotlight"},
                                            {"language": "en", "text": "underline"},
                                            {"language": "en", "text": "pinpoint"},
                                        ],
                                        "thesaurusLinks": [{"entry_id": "home_in_on", "sense_id": "t_en_gb0007069.016"}],
                                    },
                                ],
                            }
                        ],
                        "language": "en-us",
                        "lexicalCategory": {"id": "verb", "text": "Verb"},
                        "phrases": [
                            {"id": "a_home_away_from_home", "text": "a home away from home"},
                            {"id": "at_home", "text": "at home"},
                            {"id": "bring_something_home_to", "text": "bring something home to"},
                            {"id": "close_to_home", "text": "close to home"},
                            {"id": "come_home", "text": "come home"},
                            {"id": "come_home_to_someone", "text": "come home to someone"},
                            {"id": "drive_something_home", "text": "drive something home"},
                            {"id": "hit_home", "text": "hit home"},
                            {"id": "home_and_dry", "text": "home and dry"},
                            {"id": "home_free", "text": "home free"},
                            {"id": "home_is_where_the_heart_is", "text": "home is where the heart is"},
                            {"id": "home_sweet_home", "text": "home sweet home"},
                        ],
                        "text": "home",
                    },
                ],
                "type": "headword",
                "word": "home",
            }
        ],
        "word": "home",
    }


def cow_lemma():
    return {
        "metadata": {"provider": "Oxford University Press"},
        "results": [
            {
                "id": "cow",
                "language": "en",
                "lexicalEntries": [
                    {"inflectionOf": [{"id": "cow", "text": "cow"}], "language": "en", "lexicalCategory": {"id": "noun", "text": "Noun"}, "text": "cow"},
                    {"inflectionOf": [{"id": "cow", "text": "cow"}], "language": "en", "lexicalCategory": {"id": "verb", "text": "Verb"}, "text": "cow"},
                ],
                "word": "cow",
            }
        ],
    }


def cow_definition():
    return {
        "id": "cow",
        "metadata": {"operation": "retrieve", "provider": "Oxford University Press", "schema": "RetrieveEntry"},
        "results": [
            {
                "id": "cow",
                "language": "en-us",
                "lexicalEntries": [
                    {
                        "entries": [
                            {
                                "etymologies": ["Old English cū, of Germanic origin; related to Dutch koe and German Kuh, from an Indo-European root shared by Latin bos and Greek bous"],
                                "homographNumber": "100",
                                "pronunciations": [
                                    {"dialects": ["American English"], "phoneticNotation": "respell", "phoneticSpelling": "kou"},
                                    {"audioFile": "https://audio.oxforddictionaries.com/en/mp3/cow_us_1.mp3", "dialects": ["American English"], "phoneticNotation": "IPA", "phoneticSpelling": "kaʊ"},
                                ],
                                "senses": [
                                    {
                                        "definitions": ["a fully grown female animal of a domesticated breed of ox, kept to produce milk or beef"],
                                        "examples": [{"text": "a dairy cow"}],
                                        "id": "m_en_gbus0228150.006",
                                        "semanticClasses": [{"id": "cow", "text": "Cow"}],
                                        "shortDefinitions": ["domesticated female bovine animal"],
                                        "subsenses": [
                                            {
                                                "definitions": ["(loosely) a domestic bovine animal, regardless of sex or age."],
                                                "id": "m_en_gbus0228150.009",
                                                "semanticClasses": [{"id": "cow", "text": "Cow"}],
                                                "shortDefinitions": ["domestic bovine animal"],
                                            },
                                            {
                                                "crossReferenceMarkers": ["Compare with heifer"],
                                                "crossReferences": [{"id": "heifer", "text": "heifer", "type": "see also"}],
                                                "definitions": ["(in farming) a female domestic bovine animal which has borne more than one calf."],
                                                "domainClasses": [{"id": "farming", "text": "Farming"}],
                                                "id": "m_en_gbus0228150.010",
                                                "semanticClasses": [{"id": "cow", "text": "Cow"}],
                                                "shortDefinitions": ["cow which has borne calves"],
                                            },
                                            {
                                                "definitions": ["the female of certain other large animals, for example elephant, rhinoceros, whale, or seal."],
                                                "domainClasses": [{"id": "zoology", "text": "Zoology"}],
                                                "id": "m_en_gbus0228150.011",
                                                "semanticClasses": [{"id": "mammal", "text": "Mammal"}],
                                                "shortDefinitions": ["female elephant etc."],
                                            },
                                        ],
                                    },
                                    {
                                        "definitions": ["an unpleasant or disliked woman"],
                                        "examples": [{"text": "what does he see in that cow?"}],
                                        "id": "m_en_gbus0228150.013",
                                        "registers": [{"id": "derogatory", "text": "Derogatory"}],
                                        "semanticClasses": [{"id": "disliked_woman", "text": "Disliked_Woman"}],
                                        "shortDefinitions": ["woman"],
                                        "subsenses": [
                                            {
                                                "definitions": ["an unpleasant person or thing."],
                                                "id": "m_en_gbus0228150.014",
                                                "regions": [{"id": "australian", "text": "Australian"}, {"id": "new_zealand", "text": "New_Zealand"}],
                                                "registers": [{"id": "informal", "text": "Informal"}],
                                                "semanticClasses": [{"id": "disliked_thing", "text": "Disliked_Thing"}],
                                                "shortDefinitions": ["unpleasant person or thing"],
                                            }
                                        ],
                                    },
                                ],
                            }
                        ],
                        "language": "en-us",
                        "lexicalCategory": {"id": "noun", "text": "Noun"},
                        "phrases": [{"id": "have_a_cow", "text": "have a cow"}, {"id": "till_the_cows_come_home", "text": "till the cows come home"}],
                        "text": "cow",
                    }
                ],
                "type": "headword",
                "word": "cow",
            },
            {
                "id": "cow",
                "language": "en-us",
                "lexicalEntries": [
                    {
                        "entries": [
                            {
                                "etymologies": ["late 16th century: probably from Old Norse kúga ‘oppress’"],
                                "grammaticalFeatures": [{"id": "transitive", "text": "Transitive", "type": "Subcategorization"}],
                                "homographNumber": "200",
                                "pronunciations": [
                                    {"dialects": ["American English"], "phoneticNotation": "respell", "phoneticSpelling": "kou"},
                                    {"audioFile": "https://audio.oxforddictionaries.com/en/mp3/cow_us_1.mp3", "dialects": ["American English"], "phoneticNotation": "IPA", "phoneticSpelling": "kaʊ"},
                                ],
                                "senses": [
                                    {
                                        "definitions": ["cause (someone) to submit to one's wishes by intimidation"],
                                        "examples": [{"text": "the intellectuals had been cowed into silence"}],
                                        "id": "m_en_gbus0228160.005",
                                        "shortDefinitions": ["cause someone to submit to one's wishes by intimidation"],
                                        "synonyms": [
                                            {"language": "en", "text": "intimidate"},
                                            {"language": "en", "text": "daunt"},
                                            {"language": "en", "text": "browbeat"},
                                            {"language": "en", "text": "bully"},
                                            {"language": "en", "text": "badger"},
                                            {"language": "en", "text": "dragoon"},
                                            {"language": "en", "text": "bludgeon"},
                                            {"language": "en", "text": "tyrannize"},
                                            {"language": "en", "text": "overawe"},
                                            {"language": "en", "text": "awe"},
                                            {"language": "en", "text": "dismay"},
                                            {"language": "en", "text": "dishearten"},
                                            {"language": "en", "text": "unnerve"},
                                            {"language": "en", "text": "subdue"},
                                            {"language": "en", "text": "scare"},
                                            {"language": "en", "text": "terrorize"},
                                            {"language": "en", "text": "frighten"},
                                            {"language": "en", "text": "petrify"},
                                        ],
                                        "thesaurusLinks": [{"entry_id": "cow", "sense_id": "t_en_gb0003145.001"}],
                                    }
                                ],
                            }
                        ],
                        "language": "en-us",
                        "lexicalCategory": {"id": "verb", "text": "Verb"},
                        "text": "cow",
                    }
                ],
                "type": "headword",
                "word": "cow",
            },
        ],
        "word": "cow",
    }


def why_definition():
    return {
        "id": "why",
        "metadata": {"operation": "retrieve", "provider": "Oxford University Press", "schema": "RetrieveEntry"},
        "results": [
            {
                "id": "why",
                "language": "en-us",
                "lexicalEntries": [
                    {
                        "entries": [
                            {
                                "etymologies": ["Old English hwī, hwȳ ‘by what cause’, instrumental case of hwæt ‘what’, of Germanic origin"],
                                "pronunciations": [
                                    {"dialects": ["American English"], "phoneticNotation": "respell", "phoneticSpelling": "(h)wī"},
                                    {
                                        "audioFile": "https://audio.oxforddictionaries.com/en/mp3/why_us_1.mp3",
                                        "dialects": ["American English"],
                                        "phoneticNotation": "IPA",
                                        "phoneticSpelling": "(h)waɪ",
                                    },
                                ],
                                "senses": [
                                    {
                                        "definitions": ["for what reason or purpose"],
                                        "examples": [{"text": "why did he do it?"}],
                                        "id": "m_en_gbus1157440.005",
                                        "shortDefinitions": ["for what reason or purpose"],
                                        "subsenses": [
                                            {
                                                "definitions": ["used to make or agree to a suggestion"],
                                                "examples": [{"text": "why don't I give you a lift?"}],
                                                "id": "m_en_gbus1157440.007",
                                                "notes": [{"text": "with negative", "type": "grammaticalNote"}],
                                                "shortDefinitions": ["used to make or agree to suggestion"],
                                            }
                                        ],
                                    }
                                ],
                            },
                            {
                                "grammaticalFeatures": [{"id": "relative", "text": "Relative", "type": "Referential"}],
                                "pronunciations": [
                                    {"dialects": ["American English"], "phoneticNotation": "respell", "phoneticSpelling": "(h)wī"},
                                    {
                                        "audioFile": "https://audio.oxforddictionaries.com/en/mp3/why_us_1.mp3",
                                        "dialects": ["American English"],
                                        "phoneticNotation": "IPA",
                                        "phoneticSpelling": "(h)waɪ",
                                    },
                                ],
                                "senses": [
                                    {
                                        "constructions": [{"text": "the reason why"}],
                                        "definitions": ["(with reference to a reason) on account of which; for which"],
                                        "examples": [{"text": "\n              the reason why flu shots need repeating every year is that the virus changes"}],
                                        "id": "m_en_gbus1157440.009",
                                        "shortDefinitions": ["on account of which"],
                                        "subsenses": [
                                            {
                                                "definitions": ["the reason for which"],
                                                "examples": [{"text": "each has faced similar hardships, and perhaps that is why they are friends"}],
                                                "id": "m_en_gbus1157440.011",
                                                "shortDefinitions": ["reason for which"],
                                            }
                                        ],
                                    }
                                ],
                            },
                        ],
                        "language": "en-us",
                        "lexicalCategory": {"id": "adverb", "text": "Adverb"},
                        "phrases": [{"id": "why_so%3F", "text": "why so?"}],
                        "text": "why",
                    },
                    {
                        "entries": [
                            {
                                "pronunciations": [
                                    {"dialects": ["American English"], "phoneticNotation": "respell", "phoneticSpelling": "(h)wī"},
                                    {
                                        "audioFile": "https://audio.oxforddictionaries.com/en/mp3/why_us_1.mp3",
                                        "dialects": ["American English"],
                                        "phoneticNotation": "IPA",
                                        "phoneticSpelling": "(h)waɪ",
                                    },
                                ],
                                "senses": [
                                    {
                                        "definitions": ["expressing surprise or indignation"],
                                        "examples": [{"text": "why, that's absurd!"}],
                                        "id": "m_en_gbus1157440.014",
                                        "shortDefinitions": ["expressing surprise or indignation"],
                                    },
                                    {
                                        "definitions": ["used to add emphasis to a response"],
                                        "examples": [{"text": "“You think so?” “Why, yes.”"}],
                                        "id": "m_en_gbus1157440.017",
                                        "shortDefinitions": ["used to add emphasis to response"],
                                    },
                                ],
                            }
                        ],
                        "language": "en-us",
                        "lexicalCategory": {"id": "interjection", "text": "Interjection"},
                        "phrases": [{"id": "why_so%3F", "text": "why so?"}],
                        "text": "why",
                    },
                    {
                        "entries": [
                            {
                                "inflections": [{"grammaticalFeatures": [{"id": "plural", "text": "Plural", "type": "Number"}], "inflectedForm": "whys"}],
                                "pronunciations": [
                                    {"dialects": ["American English"], "phoneticNotation": "respell", "phoneticSpelling": "(h)wī"},
                                    {
                                        "audioFile": "https://audio.oxforddictionaries.com/en/mp3/why_us_1.mp3",
                                        "dialects": ["American English"],
                                        "phoneticNotation": "IPA",
                                        "phoneticSpelling": "(h)waɪ",
                                    },
                                ],
                                "senses": [
                                    {
                                        "constructions": [{"text": "whys and wherefores"}],
                                        "definitions": ["a reason or explanation"],
                                        "examples": [{"text": "the whys and wherefores of these procedures need to be explained to students"}],
                                        "id": "m_en_gbus1157440.020",
                                        "semanticClasses": [{"id": "cause", "text": "Cause"}],
                                        "shortDefinitions": ["reason or explanation"],
                                    }
                                ],
                            }
                        ],
                        "language": "en-us",
                        "lexicalCategory": {"id": "noun", "text": "Noun"},
                        "phrases": [{"id": "why_so%3F", "text": "why so?"}],
                        "text": "why",
                    },
                ],
                "type": "headword",
                "word": "why",
            }
        ],
        "word": "why",
    }
