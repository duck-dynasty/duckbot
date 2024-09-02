from dataclasses import dataclass
from typing import List

from .building import Building
from .item import Form, Item
from .rate import Rate, Rates


@dataclass
class Recipe:
    name: str
    building: Building
    inputs: Rates
    outputs: Rates

    def __hash__(self):
        return hash(self.name)


def default() -> List[Recipe]:
    return [
        smelt("IronIngot", Item.IronOre * 30 >> Item.IronIngot * 30),
        ctor("IronPlate", Item.IronIngot * 30 >> Item.IronPlate * 20),
        ctor("IronRod", Item.IronIngot * 30 >> Item.IronRod * 30),
        refine("Plastic", Item.CrudeOil * 30 >> Item.Plastic * 20 + Item.HeavyOilResidue * 10),
        refine("Rubber", Item.CrudeOil * 30 >> Item.Rubber * 20 + Item.HeavyOilResidue * 20),
    ]


def awesome_sink() -> List[Recipe]:
    return [sink(item) for item in Item if item.form == Form.Solid and item.points > 0]


def all() -> List[Recipe]:
    return default() + recycled() + awesome_sink()


def recipe(name: str, building: Building, inout: tuple[Rates, Rates]) -> Recipe:
    return Recipe(name, building, inputs=inout[0].rates, outputs=inout[1].rates)


def smelt(name: str, inout: tuple[Rates, Rates]) -> Recipe:
    return recipe(name, Building.Smelter, inout)


def ctor(name: str, inout: tuple[Rates, Rates]) -> Recipe:
    return recipe(name, Building.Constructor, inout)


def assy(name: str, inout: tuple[Rates, Rates]) -> Recipe:
    return recipe(name, Building.Assembler, inout)


def manu(name: str, inout: tuple[Rates, Rates]) -> Recipe:
    return recipe(name, Building.Manufacturer, inout)


def refine(name: str, inout: tuple[Rates, Rates]) -> Recipe:
    return recipe(name, Building.Refinery, inout)


def pack(name: str, inout: tuple[Rates, Rates]) -> Recipe:
    return recipe(name, Building.Packager, inout[0] + Item.EmptyCanister * list(inout[0].rates.values())[0] >> inout[1])


def unpack(name: str, inout: tuple[Rates, Rates]) -> Recipe:
    return recipe(name, Building.Packager, inout[0] >> inout[1] + Item.EmptyCanister * list(inout[1].rates.values())[0])


def blend(name: str, inout: tuple[Rates, Rates]) -> Recipe:
    return recipe(name, Building.Blender, inout)


def sink(item: Item) -> Recipe:
    return recipe(f"Sink{item}", Building.AwesomeSink, item * 1 >> Item.AwesomeTicketPoints * item.points)


def bioburn(name: str, input: Rate) -> Recipe:
    return recipe(name, Building.BiomassBurner, input >> Item.MwPower * 30)


def recycled() -> List[Recipe]:
    return [
        refine("HeavyOilResidue", Item.CrudeOil * 30 >> Item.HeavyOilResidue * 40 + Item.PolymerResin * 20),
        refine("RecycledPlastic", Item.Rubber * 30 + Item.Fuel * 30 >> Item.Plastic * 60),
        refine("RecycledRubber", Item.Plastic * 30 + Item.Fuel * 30 >> Item.Rubber * 60),
        refine("ResidualPlastic", Item.PolymerResin * 60 + Item.Water * 20 >> Item.Plastic * 20),
        refine("ResidualRubber", Item.PolymerResin * 40 + Item.Water * 40 >> Item.Rubber * 20),
        refine("DilutedPackagedFuel", Item.HeavyOilResidue * 30 + Item.PackagedWater * 60 >> Item.PackagedFuel * 60),
        pack("PackagedWater", Item.Water * 60 >> Item.PackagedWater * 60),
        unpack("UnpackageFuel", Item.PackagedFuel * 60 >> Item.Fuel * 60),
    ]
