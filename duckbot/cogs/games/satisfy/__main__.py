from .factory import Factory
from .item import Item
from .rate import Rates
from .recipe import all
from .solver import recipe_explosion, recipe_explosion_optimize

if __name__ == "__main__":
    inputs, targets = Item.IronOre * 30 >> Item.IronPlate * 20

    inputs, targets = Item.CrudeOil * 300 + Item.Water * 100000 >> Item.Plastic * 900
    power = 30000
    sloops = 100
    factory = Factory(inputs=inputs, targets=Rates(), power=power, sloops=sloops, recipes=all(), maximize=set([Item.Plastic]))

    results = recipe_explosion_optimize(factory)
    print()
    for recipe, rate in results.items():
        print(recipe, rate)
