from dataclasses import dataclass
from typing import List

from .building import Building
from .item import Item, sinkable
from .rates import Rates


@dataclass
class Recipe:
    name: str
    building: Building
    inputs: Rates
    outputs: Rates

    def __hash__(self):
        return hash(self.name)


@dataclass
class ModifiedRecipe:
    original_recipe: Recipe
    power_shards: int
    sloops: int

    def __hash__(self):
        return hash(self.name)

    @property
    def name(self) -> str:
        return f"{self.original_recipe.name}#{self.power_shards}#{self.sloops}"

    @property
    def building(self) -> Building:
        return self.original_recipe.building

    @property
    def inputs(self) -> Rates:
        return self.original_recipe.inputs * self.shard_scale

    @property
    def outputs(self) -> Rates:
        return self.original_recipe.outputs * self.shard_scale * self.sloop_scale

    @property
    def shard_scale(self) -> float:
        return 1.0 + self.power_shards * 0.5 if self.building.max_shards > 0 else 1.0

    @property
    def sloop_scale(self) -> float:
        return 1.0 + self.sloops / self.building.max_sloop if self.building.max_sloop > 0 else 1.0


def default() -> List[Recipe]:
    return [
        refine("Plastic", Item.CrudeOil * 30 >> Item.Plastic * 20 + Item.HeavyOilResidue * 10),
        refine("Rubber", Item.CrudeOil * 30 >> Item.Rubber * 20 + Item.HeavyOilResidue * 20),
        refine("PetroleumCoke", Item.HeavyOilResidue * 40 >> Item.PetroleumCoke * 120),
        manu(Item.AdaptiveControlUnit, Item.AutomatedWiring * 5 + Item.CircuitBoard * 5 + Item.HeavyModularFrame * 1 + Item.Computer * 2 >> Item.AdaptiveControlUnit * 1),
        encode(
            Item.AiExpensionServer,
            Item.MagneticFieldGenerator * 4 + Item.NeuralQuantumProcessor * 4 + Item.SuperpositionOscillator * 4 + Item.ExcitedPhotonicMatter * 100
            >> Item.AiExpensionServer * 4 + Item.DarkMatterResidue * 100,
        ),
        assy(Item.AiLimiter, Item.CopperSheet * 25 + Item.Quickwire * 100 >> Item.AiLimiter * 5),
        assy(Item.AlcladAluminumSheet, Item.AluminumIngot * 30 + Item.CopperIngot * 10 >> Item.AlcladAluminumSheet * 30),
        ctor(Item.AlienDnaCapsule, Item.AlienProtein * 10 >> Item.AlienDnaCapsule * 10),
        ctor("HogProtein", Item.HogRemains * 20 >> Item.AlienProtein * 20),
        ctor("SpitterProtein", Item.SpitterRemains * 20 >> Item.AlienProtein * 20),
        ctor("StingerProtein", Item.StingerRemains * 20 >> Item.AlienProtein * 20),
        ctor("HatcherProtein", Item.HatcherRemains * 20 >> Item.AlienProtein * 20),
        refine(Item.AluminaSolution, Item.Bauxite * 120 + Item.Water * 180 >> Item.AluminaSolution * 120 + Item.Silica * 50),
        ctor(Item.AluminumCasing, Item.AluminumIngot * 90 >> Item.AluminumCasing * 60),
        foundry(Item.AluminumIngot, Item.AluminumScrap * 90 + Item.Silica * 75 >> Item.AluminumIngot * 60),
        refine(Item.AluminumScrap, Item.AluminaSolution * 240 + Item.Coal * 120 >> Item.AluminumScrap * 360 + Item.Water * 120),
        assy(Item.AssemblyDirectorSystem, Item.AdaptiveControlUnit * 1.5 + Item.Supercomputer * 0.75 >> Item.AssemblyDirectorSystem * 0.75),
        assy(Item.AutomatedWiring, Item.Stator * 2.5 + Item.Cable * 50 >> Item.AutomatedWiring * 2.5),
        manu(Item.BallisticWarpDrive, Item.ThermalPropulsionRocket * 1 + Item.SingularityCell * 5 + Item.SuperpositionOscillator * 2 + Item.DarkMatterCrystal * 40 >> Item.BallisticWarpDrive * 1),
        blend(Item.Battery, Item.SulfuricAcid * 50 + Item.AluminaSolution * 40 + Item.AluminumCasing * 20 >> Item.Battery * 20 + Item.Water * 30),
        blend(Item.BiochemicalSculptor, Item.AssemblyDirectorSystem * 0.5 + Item.FicsiteTrigon * 40 + Item.Water * 10 >> Item.BiochemicalSculptor * 2),
        ctor("Biomass#Mycelia", Item.Mycelia * 15 >> Item.Biomass * 150),
        ctor("Biomass#AlienProtein", Item.AlienProtein * 15 >> Item.Biomass * 1500),
        ctor("Biomass#Leaves", Item.Leaves * 120 >> Item.Biomass * 60),
        ctor("Biomass#Wood", Item.Wood * 60 >> Item.Biomass * 300),
        assy(Item.BlackPowder, Item.Coal * 15 + Item.Sulfur * 15 >> Item.BlackPowder * 30),
        ctor(Item.Cable, Item.Wire * 60 >> Item.Cable * 30),
        smelt(Item.CateriumIngot, Item.CateriumOre * 45 >> Item.CateriumIngot * 15),
        assy(Item.CircuitBoard, Item.CopperSheet * 15 + Item.Plastic * 30 >> Item.CircuitBoard * 7.5),
        assy(Item.ClusterNobelisk, Item.Nobelisk * 7.5 + Item.SmokelessPowder * 10 >> Item.ClusterNobelisk * 2.5),
        manu(Item.Computer, Item.CircuitBoard * 10 + Item.Cable * 20 + Item.Plastic * 40 >> Item.Computer * 2.5),
        ctor(Item.Concrete, Item.Limestone * 45 >> Item.Concrete * 15),
        blend(Item.CoolingSystem, Item.HeatSink * 12 + Item.Rubber * 12 + Item.Water * 30 + Item.NitrogenGas * 150 >> Item.CoolingSystem * 6),
        smelt(Item.CopperIngot, Item.CopperOre * 30 >> Item.CopperIngot * 30),
        ctor(Item.CopperPowder, Item.CopperIngot * 300 >> Item.CopperPowder * 50),
        ctor(Item.CopperSheet, Item.CopperIngot * 20 >> Item.CopperSheet * 10),
        manu(Item.CrystalOscillator, Item.QuartzCrystal * 18 + Item.Cable * 14 + Item.ReinforcedIronPlate * 2.5 >> Item.CrystalOscillator * 1),
        accel(Item.DarkMatterCrystal, Item.Diamonds * 30 + Item.DarkMatterResidue * 150 >> Item.DarkMatterCrystal * 30),
        convert(Item.DarkMatterResidue, Item.ReanimatedSam * 50 >> Item.DarkMatterResidue * 100),
        accel(Item.Diamonds, Item.Coal * 600 >> Item.Diamonds * 30),
        assy(Item.ElectromagneticControlRod, Item.Stator * 6 + Item.AiLimiter * 4 >> Item.ElectromagneticControlRod * 4),
        ctor(Item.EmptyCanister, Item.Plastic * 30 >> Item.EmptyCanister * 60),
        ctor(Item.EmptyFluidTank, Item.AluminumIngot * 60 >> Item.EmptyFluidTank * 60),
        assy(Item.EncasedIndustrialBeam, Item.SteelBeam * 18 + Item.Concrete * 36 >> Item.EncasedIndustrialBeam * 6),
        assy(Item.EncasedPlutoniumCell, Item.PlutoniumPellet * 10 + Item.Concrete * 20 >> Item.EncasedPlutoniumCell * 5),
        blend(Item.EncasedUraniumCell, Item.Uranium * 50 + Item.Concrete * 15 + Item.SulfuricAcid * 40 >> Item.EncasedUraniumCell * 25 + Item.SulfuricAcid * 10),
        Recipe(str(Item.ExcitedPhotonicMatter), Building.Converter, inputs=Rates(), outputs=Item.ExcitedPhotonicMatter * 200),
        manu(Item.ExplosiveRebar, Item.IronRebar * 10 + Item.SmokelessPowder * 10 + Item.SteelPipe * 10 >> Item.ExplosiveRebar * 5),
        assy(Item.Fabric, Item.Mycelia * 15 + Item.Biomass * 75 >> Item.Fabric * 15),
        convert("FicsiteIngot#Iron", Item.ReanimatedSam * 40 + Item.IronIngot * 240 >> Item.FicsiteIngot * 10),
        convert("FicsiteIngot#Aluminum", Item.ReanimatedSam * 60 + Item.AluminumIngot * 120 >> Item.FicsiteIngot * 30),
        convert("FicsiteIngot#Caterium", Item.ReanimatedSam * 40 + Item.CateriumIngot * 60 >> Item.FicsiteIngot * 15),
        ctor(Item.FicsiteTrigon, Item.FicsiteIngot * 10 >> Item.FicsiteTrigon * 30),
        accel(Item.Ficsonium, Item.PlutoniumWaste * 10 + Item.SingularityCell * 10 + Item.DarkMatterResidue * 200 >> Item.Ficsonium * 10),
        encode(
            Item.FicsoniumFuelRod,
            Item.Ficsonium * 5 + Item.ElectromagneticControlRod * 5 + Item.FicsiteTrigon * 100 + Item.ExcitedPhotonicMatter * 50 >> Item.FicsoniumFuelRod * 2.5 + Item.DarkMatterResidue * 50,
        ),
        refine(Item.Fuel, Item.CrudeOil * 60 >> Item.Fuel * 40 + Item.PolymerResin * 30),
        refine("ResidualFuel", Item.HeavyOilResidue * 60 >> Item.Fuel * 40),
        blend(Item.FusedModularFrame, Item.HeavyModularFrame * 1.5 + Item.AluminumCasing * 75 + Item.NitrogenGas * 37.5 >> Item.FusedModularFrame * 1.5),
        manu(Item.GasFilter, Item.Fabric * 15 + Item.Coal * 30 + Item.IronPlate * 15 >> Item.GasFilter * 7.5),
        assy(Item.GasNobelisk, Item.Nobelisk * 5 + Item.Biomass * 50 >> Item.GasNobelisk),
        assy(Item.HeatSink, Item.AlcladAluminumSheet * 37.5 + Item.CopperSheet * 22.5 >> Item.HeatSink * 7.5),
        manu(Item.HeavyModularFrame, Item.ModularFrame * 10 + Item.SteelPipe * 40 + Item.EncasedIndustrialBeam * 10 + Item.Screw * 240 >> Item.HeavyModularFrame * 2),
        manu(Item.HighSpeedConnector, Item.Quickwire * 210 + Item.Cable * 37.5 + Item.CircuitBoard * 3.75 >> Item.HighSpeedConnector * 3.75),
        assy(Item.HomingRifleAmmo, Item.RifleAmmo * 50 + Item.HighSpeedConnector * 2.5 >> Item.HomingRifleAmmo * 25),
        manu(Item.IodineInfusedFilter, Item.GasFilter * 3.75 + Item.Quickwire * 30 + Item.AluminumCasing * 3.75 >> Item.IodineInfusedFilter * 3.75),
        refine(Item.IonizedFuel, Item.RocketFuel * 40 + Item.PowerShard * 2.5 >> Item.IonizedFuel * 40 + Item.CompactedCoal * 5),
        smelt(Item.IronIngot, Item.IronOre * 30 >> Item.IronIngot * 30),
        ctor(Item.IronPlate, Item.IronIngot * 30 >> Item.IronPlate * 20),
        ctor(Item.IronRebar, Item.IronRod * 15 >> Item.IronRebar * 15),
        ctor(Item.IronRod, Item.IronIngot * 15 >> Item.IronRod * 15),
    ]


def packager() -> List[Recipe]:
    return [
        can(Item.PackagedAluminaSolution, Item.AluminaSolution * 120 >> Item.PackagedAluminaSolution * 120),
        uncan(Item.AluminaSolution, Item.PackagedAluminaSolution * 120 >> Item.AluminaSolution * 120),
        can(Item.PackagedOil, Item.CrudeOil * 30 >> Item.PackagedOil * 30),
        uncan(Item.CrudeOil, Item.PackagedOil * 60 >> Item.CrudeOil * 60),
        can(Item.PackagedFuel, Item.Fuel * 40 >> Item.PackagedFuel * 40),
        uncan(Item.Fuel, Item.PackagedFuel * 60 >> Item.Fuel * 60),
        can(Item.PackagedHeavyOilResidue, Item.HeavyOilResidue * 30 >> Item.PackagedHeavyOilResidue * 30),
        uncan(Item.HeavyOilResidue, Item.PackagedHeavyOilResidue * 20 >> Item.HeavyOilResidue * 20),
        tank(Item.PackagedIonizedFuel, Item.IonizedFuel * 80 >> Item.PackagedIonizedFuel * 40),
        untank(Item.IonizedFuel, Item.PackagedIonizedFuel * 40 >> Item.IonizedFuel * 80),
    ]


def converter() -> List[Recipe]:
    return [
        convert("Bauxite#Caterium", Item.ReanimatedSam * 10 + Item.CateriumOre * 150 >> Item.Bauxite * 120),
        convert("Bauxite#Copper", Item.ReanimatedSam * 10 + Item.CopperOre * 180 >> Item.Bauxite * 120),
        convert("CateriumOre#Copper", Item.ReanimatedSam * 10 + Item.CopperOre * 150 >> Item.CateriumOre * 120),
        convert("CateriumOre#Quartz", Item.ReanimatedSam * 10 + Item.RawQuartz * 120 >> Item.CateriumOre * 120),
        convert("Coal#Iron", Item.ReanimatedSam * 10 + Item.IronOre * 180 >> Item.Coal * 120),
        convert("Coal#Limestone", Item.ReanimatedSam * 10 + Item.Limestone * 360 >> Item.Coal * 120),
        convert("CopperOre#Quartz", Item.ReanimatedSam * 10 + Item.RawQuartz * 100 >> Item.CopperOre * 120),
        convert("CopperOre#Sulfur", Item.ReanimatedSam * 10 + Item.Sulfur * 120 >> Item.CopperOre * 120),
        convert("IronOre#Limestone", Item.ReanimatedSam * 10 + Item.Limestone * 240 >> Item.IronOre * 120),
    ]


def awesome_sink() -> List[Recipe]:
    return [sink(item) for item in Item if sinkable(item)]


def all() -> List[Recipe]:
    return default() + recycled() + awesome_sink()


def recipe(name: str | Item, building: Building, inout: tuple[Rates, Rates]) -> Recipe:
    return Recipe(str(name), building, inputs=inout[0], outputs=inout[1])


def smelt(name: str | Item, inout: tuple[Rates, Rates]) -> Recipe:
    return recipe(name, Building.Smelter, inout)


def foundry(name: str | Item, inout: tuple[Rates, Rates]) -> Recipe:
    return recipe(name, Building.Foundry, inout)


def ctor(name: str | Item, inout: tuple[Rates, Rates]) -> Recipe:
    return recipe(name, Building.Constructor, inout)


def assy(name: str | Item, inout: tuple[Rates, Rates]) -> Recipe:
    return recipe(name, Building.Assembler, inout)


def manu(name: str | Item, inout: tuple[Rates, Rates]) -> Recipe:
    return recipe(name, Building.Manufacturer, inout)


def refine(name: str | Item, inout: tuple[Rates, Rates]) -> Recipe:
    return recipe(name, Building.Refinery, inout)


def can(packaged: Item, inout: tuple[Rates, Rates]) -> Recipe:
    return recipe(packaged, Building.Packager, inout[0] + Item.EmptyCanister * list(inout[1].rates.values())[0] >> inout[1])


def uncan(unpacked: Item, inout: tuple[Rates, Rates]) -> Recipe:
    return recipe(f"Unpackage{unpacked}", Building.Packager, inout[0] >> inout[1] + Item.EmptyCanister * list(inout[0].rates.values())[0])


def tank(packaged: Item, inout: tuple[Rates, Rates]) -> Recipe:
    return recipe(packaged, Building.Packager, inout[0] + Item.EmptyFluidTank * list(inout[1].rates.values())[0] >> inout[1])


def untank(unpacked: Item, inout: tuple[Rates, Rates]) -> Recipe:
    return recipe(f"Unpackage{unpacked}", Building.Packager, inout[0] >> inout[1] + Item.EmptyFluidTank * list(inout[0].rates.values())[0])


def blend(name: str | Item, inout: tuple[Rates, Rates]) -> Recipe:
    return recipe(name, Building.Blender, inout)


def accel(name: str | Item, inout: tuple[Rates, Rates]) -> Recipe:
    return recipe(name, Building.ParticleAccelerator, inout)


def convert(name: str | Item, inout: tuple[Rates, Rates]) -> Recipe:
    return recipe(name, Building.Converter, inout)


def encode(name: str | Item, inout: tuple[Rates, Rates]) -> Recipe:
    return recipe(name, Building.QuantumEncoder, inout)


def sink(item: Item) -> Recipe:
    return recipe(f"Sink{item}", Building.AwesomeSink, item * 1 >> Item.AwesomeTicketPoints * item.points)


def bioburn(name: str, input: Rates) -> Recipe:
    return recipe(name, Building.BiomassBurner, input >> Item.MwPower * 30)


def recycled() -> List[Recipe]:
    return [
        refine("HeavyOilResidue", Item.CrudeOil * 30 >> Item.HeavyOilResidue * 40 + Item.PolymerResin * 20),
        refine("RecycledPlastic", Item.Rubber * 30 + Item.Fuel * 30 >> Item.Plastic * 60),
        refine("RecycledRubber", Item.Plastic * 30 + Item.Fuel * 30 >> Item.Rubber * 60),
        refine("ResidualPlastic", Item.PolymerResin * 60 + Item.Water * 20 >> Item.Plastic * 20),
        refine("ResidualRubber", Item.PolymerResin * 40 + Item.Water * 40 >> Item.Rubber * 20),
        refine("DilutedPackagedFuel", Item.HeavyOilResidue * 30 + Item.PackagedWater * 60 >> Item.PackagedFuel * 60),
        can(Item.PackagedWater, Item.Water * 60 >> Item.PackagedWater * 60),
        uncan(Item.Fuel, Item.PackagedFuel * 60 >> Item.Fuel * 60),
    ]
