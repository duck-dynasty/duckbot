## Command Overview

|            Command             | Summary                                            |
| :----------------------------: | -------------------------------------------------- |
|            `!8ball`            | get a magic eight ball style fortune               |
|            `!ascii`            | renders text as ascii art                          |
|   [`!calc`](#wolfram-alpha)    | search for something on wolfram alpha              |
|            `!coin`             | flips a coin in real life                          |
|  [`!day`](#day-announcements)  | announces the current day of the week              |
|   [`!define`](#definitions)    | define a word                                      |
|             `!dog`             | displays a random dog photo                        |
|            `!duck`             | gives a link to this repo                          |
|           `!fortune`           | get a random fortune told to you by a cow          |
|       `!help` or `!wiki`       | gives a link to this wiki                          |
|            `!lmgt`             | generates a google search link for the given query |
|            `!mock`             | converts text into MoCkInG tExT                    |
|     [`!pokemon`](#pokemon)     | gives information about pokemon                    |
|  [`!recipe`](#recipe-search)   | search for a random recipe                         |
|        [`!roll`](#dice)        | rolls Dungeons and Dragons style dice              |
|  [`!start`, `!stop`](#music)   | start or stop playing music                        |
|       [`!truth`](#truth)       | fact checks a message when used in a reply         |
|     [`!weather`](#weather)     | retrieve weather information                       |
|     [`!satisfy`](#satisfy)     | produce a factory for _Satisfactory_               |
| [`/grass-stats`](#touch-grass) | show activity leaderboard for the last hour        |
| [`!yolo`](#yolo-pull-requests) | list open pull requests in this repo               |

## Wolfram Alpha

DuckBot gives out a few results to arbitrary queries to [wolfram alpha](https://www.wolframalpha.com/). The results from wolfram are pretty complex, DuckBot spews out a few results in a fairly dumb manner, and gives you a link for your query on wolfram if you want to dig further.

## Day Announcements

Every day in the 7am hour, DuckBot will announce to the general channel the current day of the week. If the day is also a statutory holiday, or an otherwise special day, DuckBot will announce that at the same time. You can run this on demand using the `!day` command.

## Definitions

DuckBot can define words, source data from the Oxford Dictionary. In the cases where a word has multiple possible root words, DuckBot will try to define all of them.

## Recipe Search

Do you crave a particular food but want an arbitrary recipe?

- Run the `!recipe` command with an argument to search for a specific recipe with a random result.
- Run the `!recipe` command with no argument to blindly return any recipe.

## Dice

DuckBot will roll Dungeons and Dragons style dice for you. See [dice syntax](https://d20.readthedocs.io/en/latest/start.html#dice-syntax) for the full list of what is possible.

> Human: !roll 1d20\
> DuckBot: Rolls: 1d20 (3)\
> Total: 3

## Music

DuckBot plays everyone's favourite background noise inside whatever voice channel you're in. Use `!start` to summon the bot, and `!stop` to dismiss it. DuckBot only has so much stamina, and will stop playing music after about four hours.

## Pokemon

DuckBot can provide information about Pokémon, because that matters. The command can search for pokemon by name (autocomplete available) or by id. Providing no arguments gives the _pokemon of the day!!!_ Yayyy!!

```
/pokemon [name-or-id]
```

## Truth

DuckBot will use the power of AI to analyze claims in a referenced message and provides a formatted response indicating whether claims are confirmed, disputed, or unverified. Fact-checks are done by using Claude AI (via Anthropic's API).

Usage Instructions:

1. Find a message in Discord that you want to fact-check
1. Reply to that message with the command `!truth`
1. DuckBot will respond with a formatted analysis of any factual claims found in the original message

## Weather

DuckBot can give you basic weather information for a given location, sourced from [OpenWeather](https://openweathermap.org/). The command takes the form of:

```
!weather [location]
```

If `location` is omitted, DuckBot will try to use the default location you have set. You can set your default location using:

```
!weather set location
```

The `location` is a little finicky. It takes the form of `city country-code index`.\
If the city name includes spaces, you have to put it `"in quotes"`.\
The country code is the two character country code (like CA for Canada), or the two character state code for cities in the USA.\
Commas will be removed from city and country names.\
If there's ever ambiguity, DuckBot will respond with all of the cities found for the search, and will number them all. After specifying the city and country code, you can specify the index to select a single city from the list.

Here's an example usage:

> Human: !weather set london\
> DuckBot: Multiple cities found matching search.\
> Narrow your search or specify an index to pick one of the following:\
> 1: London, GB, geolocation = (51.50853, -0.12574)\
> 2: London, AR, geolocation = (35.328972, -93.25296)\
> 3: London, KY, geolocation = (37.128979, -84.08326)\
> 4: London, OH, geolocation = (39.886452, -83.44825)\
> 5: London, MO, geolocation = (40.445, -95.234978)\
> 6: London, CA, geolocation = (36.476059, -119.443176)\
> 7: London, CA, geolocation = (42.983391, -81.23304)\
> Human: !weather set london ca\
> DuckBot: Multiple cities found matching search.\
> Narrow your search or specify an index to pick one of the following:\
> 1: London, CA, geolocation = (36.476059, -119.443176)\
> 2: London, CA, geolocation = (42.983391, -81.23304)\
> Human: !weather set london ca 2\
> DuckBot: Location saved! London, CA, geolocation = (42.983391, -81.23304)

## Satisfy

DuckBot can produce factories for _Satisfactory_ given various constraints. This command set is pretty hefty, so buckle up, boyos.

### High-Level

Users can run various commands to set up the factory constraints, then eventually use `/satisfy solve` to produce a solution. Each user has only one factory they can manipulate at a time, and solving does not clear the factory. The intended loop goes like:

1. set up inputs/outputs/maximize
1. decide on recipe inclusions/exclusions
1. solve
1. be happy, or go to 1

The intent is to use "raw supply" recipes to determine what inputs are needed for a factory, then finding a reasonable place in game that has those resources available, then doing another solve with the actual input constraints and maximizing the desired output.

The solutions produced are scored by an arbitrary set of metrics which hopefully lead to something reasonable. Fully optimal solutions are always wonky though, like including several recipes for the same item, so the iterative process above is still recommended. The solver objective is loosely:

1. prioritize `maximize` items above all else
1. penalize for using `input` items, or using raw inputs (like ores)
1. penalize for using somersloops and power shards
1. penalize leaving unsinkable items as factory outputs
1. penalize number of machines

In short, the solver aims to maximize the output while minimizing the input to the factory. Penalties per item are weighted (_item weights_), and are a function of raw resource rarity and item complexity. All else equal, it will also prefer simpler factories (eg, diluted fuel vs packaged diluted fuel).

Finally, strongly prefer slash commands to regular ones. Items and recipes have autocomplete, which is only available for slash commands.

### Raw Supply

Things like miners and extractors are also modeled as recipes. These recipes have no input but produce a raw material output, and are called raw supply in recipe banks. Each raw supply recipe is named the same as the raw item it produces, like `IronOre` produces `IronOre` from nothing. These recipes can be added or removed when the recipe bank isn't set up how you want (for example, you may want to exclude `CrudeOil` and only use an input of plastic you have available).

Note that most default recipes for non-raw items are also named the same as the item (like `IronIngot`). These are not raw supply recipes since the have an input.

### Auxiliary Items

Power and awesome points are also modeled as items, and are selectable anywhere an item is selectable. Useful for `maximize` solves. They are named `MwPower` and `AwesomeTicketPoints`.

### Satisfy Subcommands

```
/satisfy state
```

DuckBot will display the factory state on every command, but the message gets deleted after a minute. This command keeps the factory state up for five minutes instead. Note that `/satisfy solve` messages are not deleted and also include the factory state.

```
/satisfy reset
```

Destroys your factory state. Default state is no inputs or outputs, no recipe includes or excludes, and the default set of recipes in the game selected.

```
/satisfy input   item rate
```

Adds `item` as an input available to the factory. Typically set to ores, oil, water, etc that is around the factory, plus whatever is pulled in via logistics networks (like trains). Also typical to use alongside `/satisfy maximize` to find out how much of something it is possible to produce.

Running the command twice for the same item clobbers the prior rate value.

```
/satisfy output   item rate
```

Ensures a minimal output for the factory to produce. Typically used when raw supply recipes are available to determine what inputs are necessary to be provided.\
May lead to solutions being impossible, especially without raw supply recipes.

Running the command twice for the same item clobbers the prior rate value.

```
/satisfy maximize   item
```

Tells the solver to maximize output of the given item. Should only be used when there are no raw supply recipes available (or at least it is impossible to create the target item with the raw supply), or it will lead to the infinite factory as a solution.

Maximization occurs by item weights, so it will _not_ behave as you expect when multiple items are maximized. The solver will pick the item with the better rate to weight ratio. It is recommended to maximize a single item only.

There's no way to remove a maximize item, a full reset of the factory is required.

```
/satisfy booster   item amount
```

Make power shards or somersloops available to use in the factory. Note that power shards are not relevant unless somersloops are also added.

```
/satisfy recipe bank   name
```

Changes the recipe bank. For the love of god, use slash commands for this one. Recipe bank names are available in autocomplete. Some recipe banks include,

- Default: only default in game recipes, no raw supply or conversion recipes
- All: all available recipes, includes raw supply and conversions
- _RawSupply_ modifier: the set of raw supply recipes
- _Conversions_ modifier: the set of raw resource conversion recipes, does not include other recipes in the Converter

```
/satisfy recipe include   name [power_shards sloops]
```

Makes a recipe available to the solver even if it is not in the recipe bank.\
Note: alternatively, undoes `/satisfy recipe exclude` for the recipe. In that case, the recipe may not be available to the solver unless it is in the recipe bank.

Power shards and sloops amount can also be specified to include a specific boosted recipe. If neither is provided, all boosted variants of the recipe are included. Note that this can lead to some confusing factory states (with a recipe being both included and excluded) since boosted recipes are not distinguished from the base recipe. Basically, deal with it.

```
/satisfy recipe exclude   name [power_shards sloops]
```

Makes a recipe unavailable to the solver even if it is in the recipe bank.\
Note: alternatively, undoes `/satisfy recipe include` for the recipe. In that case, the recipe may still be available to the solver unless it is not in the recipe bank.

Power shards and sloops amount can also be specified to exclude a specific boosted recipe. If neither is provided, all boosted variants of the recipe are excluded. Note that this can lead to some confusing factory states (with a recipe being both included and excluded) since boosted recipes are not distinguished from the base recipe. Basically, deal with it.

```
/satisfy recipe limit   name limit [power_shards sloops]
```

Makes it so the solver cannot use more than `limit` instances of a given recipe. Note that if the recipe is not available (not in the bank, or explicitly excluded), then this limit will have no effect.

Power shards and sloops amount can also be specified to limit usage of a specific boosted recipe. If neither is provided, all boosted variants of the recipe are limited.

```
/satisfy solve
```

Runs the dang ol' solver. Outputs are structured like,

> **{recipe}**\
> {amount of machine}\
> {total input/output of recipe}

Recipes will appear in alphabetical order, not in any other logical grouping.

Note that values like "12.34 constructor" does not mean you need to build 13 constructors precisely with one at 34%. Rather, any number of buildings can be made, so long as they equal the throughput of 12.34 constructors. So, it could be 5 fully overclocked ones, for example.

Slooped up machines are depicted in the recipe name. It will be something like _Recipe @ 250% + 2.0x_. The `%` is the clock rate, while `x` is the sloop production multiplier. This is also described in the amount of machines line.

### Possible Errors

**Why do you hate possible?**\
DuckBot errors out with this when the desired output item is not possible to make with the given inputs, and raw supply recipes available. Changing the recipe bank to `All` is the simplest way to force a result to see what inputs you may be missing. Or check in game, though keep in mind, alternate recipes may drastically change what items are actually necessary.

**No.**\
DuckBot rejects you outright if the factory state does not have enough information to produce a factory at all. At least outputs are required. If any maximization targets are given, inputs are also required.

**->**\
DuckBot will sometimes produce the null factory. Either the input and output were trivial, or the solution is infinite. Workarounds include not using raw supply recipes, or not using any inputs at all when using raw supply.

## Touch Grass

DuckBot monitors message activity and will tell you to touch grass if you're sending too many messages. During work hours (Mon-Fri 8am-6pm EDT / 12pm-10pm UTC) the threshold is 40 messages per hour; outside work hours it's 120 messages per hour. Notifications have a 1-hour cooldown per user.

Use `/grass-stats` to see the activity leaderboard showing message counts for all tracked users in the last 60 minutes.

## Yolo Pull Requests

DuckBot will list the open pull requests when the bot owner or one of the repository owners uses the `!yolo` command.\
You can also automatically merge open pull requests by specifying the pull request number. DuckBot will do some basic checks like ensure the pull request checks have passed, and also ask you for confirmation.

> Human: !yolo 69\
> DuckBot: Bruh, that'll merge this god-awful pull request... are you sure you trust it? I sure as hell don't. (+pull request)

The same person needs to send the same command within a minute of the first will initiate the merge.

> Human: !yolo 69\
> DuckBot: Welp. See you on the other side, brother.

DuckBot will approve the pull request and merge it then.
