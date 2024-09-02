from __future__ import annotations

from enum import Enum, auto, unique


@unique
class Form(Enum):
    Solid = auto()
    Fluid = auto()
    Aux = auto()


@unique
class Item(Enum):
    IronOre = (auto(), Form.Solid, 1)
    IronIngot = (auto(), Form.Solid, 2)
    IronPlate = (auto(), Form.Solid, 6)
    IronRod = (auto(), Form.Solid, 4)

    Water = (auto(), Form.Fluid, 0)
    CrudeOil = (auto(), Form.Fluid, 0)
    HeavyOilResidue = (auto(), Form.Fluid, 0)
    PolymerResin = (auto(), Form.Solid, 12)
    Fuel = (auto(), Form.Fluid, 0)
    EmptyCanister = (auto(), Form.Solid, 60)
    PackagedFuel = (auto(), Form.Solid, 270)
    PackagedWater = (auto(), Form.Solid, 130)
    Plastic = (auto(), Form.Solid, 75)
    Rubber = (auto(), Form.Solid, 60)

    AwesomeTicketPoints = (auto(), Form.Aux, 0)
    MwPower = (auto(), Form.Aux, 0)

    def _generate_next_value_(name, start, count, last_values):  # noqa: N805
        return name

    def __init__(self, value, form: Form, points: int):
        self.form = form
        self.points = points

    def __mul__(self, rhs: float):
        from .rate import Rate

        return Rate(self, rhs)

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)
