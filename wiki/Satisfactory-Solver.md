DuckBot can produce factories for _Satisfactory_ given various constraints. This command set is pretty hefty, so buckle up, boyos.

## High-Level

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

## Raw Supply

Things like miners and extractors are also modeled as recipes. These recipes have no input but produce a raw material output, and are called raw supply in recipe banks. Each raw supply recipe is named the same as the raw item it produces, like `IronOre` produces `IronOre` from nothing. These recipes can be added or removed when the recipe bank isn't set up how you want (for example, you may want to exclude `CrudeOil` and only use an input of plastic you have available).

Note that most default recipes for non-raw items are also named the same as the item (like `IronIngot`). These are not raw supply recipes since the have an input.

## Auxiliary Items

Power and awesome points are also modeled as items, and are selectable anywhere an item is selectable. Useful for `maximize` solves. They are named `MwPower` and `AwesomeTicketPoints`.

## Satisfy Subcommands

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

Running `/satisfy maximize` again for an item that is already being maximized will remove it from the maximize set.

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

## Possible Errors

**Why do you hate possible?**\
DuckBot errors out with this when the desired output item is not possible to make with the given inputs, and raw supply recipes available. Changing the recipe bank to `All` is the simplest way to force a result to see what inputs you may be missing. Or check in game, though keep in mind, alternate recipes may drastically change what items are actually necessary.

**No.**\
DuckBot rejects you outright if the factory state does not have enough information to produce a factory at all. At least outputs are required. If any maximization targets are given, inputs are also required.

**->**\
DuckBot will sometimes produce the null factory. Either the input and output were trivial, or the solution is infinite. Workarounds include not using raw supply recipes, or not using any inputs at all when using raw supply.
