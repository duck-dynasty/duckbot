from dataclasses import dataclass
from typing import List, Optional

from .building import Building
from .item import Item

Rate = tuple[Item, float]


@dataclass
class Recipe:
    name: str
    building: Building
    inputs: dict[Item, float]
    outputs: dict[Item, float]

    def __hash__(self):
        return hash(self.name)


def default() -> List[Recipe]:
    return [
        smelt("IronIngot", Item.IronOre * 30, Item.IronIngot * 30),
        ctor("IronPlate", Item.IronIngot * 30, Item.IronPlate * 20),
        ctor("IronRod", Item.IronIngot * 30, Item.IronRod * 30),
    ]


def all() -> List[Recipe]:
    return default() + recycled()


def recipe(name: str, building: Building, inputs: List[Optional[Rate]], outputs: List[Optional[Rate]]) -> Recipe:
    return Recipe(name, building, inputs=dict([x for x in inputs if x is not None]), outputs=dict([x for x in outputs if x is not None]))


def smelt(name: str, input: Rate, output: Rate) -> Recipe:
    return recipe(name, Building.Smelter, [input], [output])


def ctor(name: str, input: Rate, output: Rate) -> Recipe:
    return recipe(name, Building.Constructor, [input], [output])


def assy(name: str, input1: Rate, input2: Rate, output: Rate) -> Recipe:
    return recipe(name, Building.Assembler, [input1, input2], [output])


def manu(name: str, input1: Rate, input2: Rate, input3: Rate, input4: Optional[Rate], output: Rate) -> Recipe:
    return recipe(name, Building.Manufacturer, [input1, input2, input3, input4], [output])


def refinery(name: str, input1: Rate, input2: Optional[Rate], output1: Rate, output2: Optional[Rate] = None) -> Recipe:
    return recipe(name, Building.Refinery, [input1, input2], [output1, output2])


def pack(name: str, rate: int, input: Item, output: Item) -> Recipe:
    return recipe(name, Building.Packager, [input * rate, Item.EmptyCanister * rate], [output * rate])


def unpack(name: str, rate: int, input: Item, output: Item) -> Recipe:
    return recipe(name, Building.Packager, [input * rate], [output * rate, Item.EmptyCanister * rate])


def recycled() -> List[Recipe]:
    return [
        refinery("HeavyOilResidue", Item.CrudeOil * 30, None, Item.HeavyOilResidue * 40, Item.PolymerResin * 20),
        refinery("RecycledPlastic", Item.Rubber * 30, Item.Fuel * 30, Item.Plastic * 60),
        refinery("RecycledRubber", Item.Plastic * 30, Item.Fuel * 30, Item.Rubber * 60),
        refinery("ResidualPlastic", Item.PolymerResin * 60, Item.Water * 20, Item.Plastic * 20),
        refinery("ResidualRubber", Item.PolymerResin * 40, Item.Water * 40, Item.Rubber * 20),
        refinery("DilutedPackagedFuel", Item.HeavyOilResidue * 30, Item.PackagedWater * 60, Item.PackagedFuel * 60),
        pack("PackagedWater", 60, Item.Water, Item.PackagedWater),
        unpack("UnpackageFuel", 60, Item.PackagedFuel, Item.Fuel),
    ]
