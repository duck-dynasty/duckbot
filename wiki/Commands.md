Command Overview
----------------

| Command | Summary |
|:-:|-|
| [`!day`](#day-announcements) | announces the current day of the week |
| [`!recipe`](#recipe-search) | search for a random recipe |
| [`!start`, `!stop`](#music) | start or stop playing music |
| [`!weather`](#weather) | retrieve weather information |
| [`!calc`](#wolfram-alpha) | search for something on wolfram alpha |
| `!lmgt` | generates a google search link for the given query |
| `!8ball` | get a magic eight ball style fortune |
| `!fortune` | get a random fortune told to you by a cow |
| `!dog` | displays a random dog photo |
| `!ascii` | renders text as ascii art |
| `!mock` | converts text into MoCkInG tExT |
| [`!roll`](#dice) | rolls Dungeons and Dragons style dice |
| `!coin` | flips a coin. in real life |
| [`!yolo`](#yolo-pull-requests) | list open pull requests in this repo |
| `!help` | gives a link to this wiki |
| `!duck` | gives a link to this repo |

Day Announcements
-----------------
Every day in the 7am hour, DuckBot will announce to the general channel the current day of the week. If the day is also a statutory holiday, or an otherwise special day, DuckBot will announce that at the same time. You can run this on demand using the `!day` command.

Recipe Search
-------------
Do you crave a particular food but want an arbitrary recipe?
* Run the `!recipe` command with an argument to search for a specific recipe with a random result.
* Run the `!recipe` command with no argument to blindly return any recipe.

Music
-----
DuckBot plays everyone's favourite background noise inside whatever voice channel you're in. Use `!start` to summon the bot, and `!stop` to dismiss it. DuckBot only has so much stamina, and will stop playing music after about four hours.

Weather
-------
DuckBot can give you basic weather information for a given location, sourced from [OpenWeather](https://openweathermap.org/). The command takes the form of:
```
!weather [location]
```
If `location` is omitted, DuckBot will try to use the default location you have set. You can set your default location using:
```
!weather set location
```

The `location` is a little finicky. It takes the form of `city country-code index`.  
If the city name includes spaces, you have to put it `"in quotes"`.  
The country code is the two character country code (like CA for Canada), or the two character state code for cities in the USA.  
Commas will be removed from city and country names.  
If there's ever ambiguity, DuckBot will respond with all of the cities found for the search, and will number them all. After specifying the city and country code, you can specify the index to select a single city from the list.

Here's an example usage:
> Human: !weather set london  
> DuckBot: Multiple cities found matching search.  
> Narrow your search or specify an index to pick one of the following:  
> 1: London, GB, geolocation = (51.50853, -0.12574)  
> 2: London, AR, geolocation = (35.328972, -93.25296)  
> 3: London, KY, geolocation = (37.128979, -84.08326)  
> 4: London, OH, geolocation = (39.886452, -83.44825)  
> 5: London, MO, geolocation = (40.445, -95.234978)  
> 6: London, CA, geolocation = (36.476059, -119.443176)  
> 7: London, CA, geolocation = (42.983391, -81.23304)  
> Human: !weather set london ca  
> DuckBot: Multiple cities found matching search.  
> Narrow your search or specify an index to pick one of the following:  
> 1: London, CA, geolocation = (36.476059, -119.443176)  
> 2: London, CA, geolocation = (42.983391, -81.23304)  
> Human: !weather set london ca 2  
> DuckBot: Location saved! London, CA, geolocation = (42.983391, -81.23304)

Wolfram Alpha
-------------
DuckBot gives out a few results to arbitrary queries to [wolfram alpha](https://www.wolframalpha.com/). The results from wolfram are pretty complex, DuckBot spews out a few results in a fairly dumb manner, and gives you a link for your query on wolfram if you want to dig further.

Dice
----
DuckBot will roll Dungeons and Dragons style dice for you. See [dice syntax](https://d20.readthedocs.io/en/latest/start.html#dice-syntax) for the full list of what is possible.

> Human: !roll 1d20  
> DuckBot: Rolls: 1d20 (3)  
> Total: 3

Yolo Pull Requests
------------------
DuckBot will list the open pull requests when the bot owner or one of the repository owners uses the `!yolo` command.  
You can also automatically merge open pull requests by specifying the pull request number. DuckBot will do some basic checks like ensure the pull request checks have passed, and also ask you for confirmation.

> Human: !yolo 69  
> DuckBot: Bruh, that'll merge this god-awful pull request... are you sure you trust it? I sure as hell don't. (+pull request)

The same person needs to send the same command within a minute of the first will initiate the merge.
> Human: !yolo 69  
> DuckBot: Welp. See you on the other side, brother.

DuckBot will approve the pull request and merge it then.
