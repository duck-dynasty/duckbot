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
    return regular() + packager() + power() + awesome_sink()


def all() -> List[Recipe]:
    return default() + converter() + alternates()


def regular() -> List[Recipe]:
    return [
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
        convert(Item.ExcitedPhotonicMatter, Rates() >> Item.ExcitedPhotonicMatter * 200),
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
        refine(Item.LiquidBiofuel, Item.SolidBiofuel * 90 + Item.Water * 45 >> Item.LiquidBiofuel * 60),
        assy(Item.MagneticFieldGenerator, Item.VersatileFramework * 2.5 + Item.ElectromagneticControlRod * 1 >> Item.MagneticFieldGenerator * 1),
        manu(Item.ModularEngine, Item.Motor * 2 + Item.Rubber * 15 + Item.SmartPlating * 2 >> Item.ModularEngine * 1),
        assy(Item.ModularFrame, Item.ReinforcedIronPlate * 3 + Item.IronRod * 12 >> Item.ModularFrame * 2),
        assy(Item.Motor, Item.Rotor * 10 + Item.Stator * 10 >> Item.Motor * 5),
        encode(
            Item.NeuralQuantumProcessor,
            Item.TimeCrystal * 15 + Item.Supercomputer * 3 + Item.FicsiteTrigon * 45 + Item.ExcitedPhotonicMatter * 75 >> Item.NeuralQuantumProcessor * 3 + Item.DarkMatterResidue * 75,
        ),
        blend(Item.NitricAcid, Item.NitrogenGas * 120 + Item.Water * 30 + Item.IronPlate * 10 >> Item.NitricAcid * 30),
        assy(Item.Nobelisk, Item.BlackPowder * 20 + Item.SteelPipe * 20 >> Item.Nobelisk * 10),
        blend(Item.NonFissileUranium, Item.UraniumWaste * 37.5 + Item.Silica * 25 + Item.NitricAcid * 15 + Item.SulfuricAcid * 15 >> Item.NonFissileUranium * 50 + Item.Water * 15),
        accel(Item.NuclearPasta, Item.CopperPowder * 100 + Item.PressureConversionCube * 0.5 >> Item.NuclearPasta * 0.5),
        manu(Item.NukeNobelisk, Item.Nobelisk * 2.5 + Item.EncasedUraniumCell * 10 + Item.SmokelessPowder * 5 + Item.AiLimiter * 3 >> Item.NukeNobelisk * 0.5),
        refine(Item.PetroleumCoke, Item.HeavyOilResidue * 40 >> Item.PetroleumCoke * 120),
        refine(Item.Plastic, Item.CrudeOil * 30 >> Item.Plastic * 20 + Item.HeavyOilResidue * 10),
        refine("ResidualPlastic", Item.PolymerResin * 60 + Item.Water * 20 >> Item.Plastic * 20),
        manu(Item.PlutoniumFuelRod, Item.EncasedPlutoniumCell * 7.5 + Item.SteelBeam * 4.5 + Item.ElectromagneticControlRod * 1.5 + Item.HeatSink * 2.5 >> Item.PlutoniumFuelRod * 0.25),
        accel(Item.PlutoniumPellet, Item.NonFissileUranium * 100 + Item.UraniumWaste * 25 >> Item.PlutoniumPellet * 30),
        ctor("PowerShard#BlueSlug", Item.BluePowerSlug * 7.5 >> Item.PowerShard * 7.5),
        ctor("PowerShard#YellowSlug", Item.YellowPowerSlug * 5 >> Item.PowerShard * 10),
        ctor("PowerShard#PurpleSlug", Item.PurplePowerSlug * 2.5 >> Item.PowerShard * 12.5),
        encode(
            "SyntheticPowerShard", Item.TimeCrystal * 10 + Item.DarkMatterCrystal * 10 + Item.QuartzCrystal * 60 + Item.ExcitedPhotonicMatter * 60 >> Item.PowerShard * 5 + Item.DarkMatterResidue * 60
        ),
        assy(Item.PressureConversionCube, Item.FusedModularFrame * 1 + Item.RadioControlUnit * 2 >> Item.PressureConversionCube * 1),
        assy(Item.PulseNobelisk, Item.Nobelisk * 5 + Item.CrystalOscillator * 1 >> Item.PulseNobelisk * 5),
        ctor(Item.QuartzCrystal, Item.RawQuartz * 37.5 >> Item.QuartzCrystal * 22.5),
        ctor(Item.Quickwire, Item.CateriumIngot * 12 >> Item.Quickwire * 60),
        manu(Item.RadioControlUnit, Item.AluminumCasing * 40 + Item.CrystalOscillator * 1.25 + Item.Computer * 2.5 >> Item.RadioControlUnit * 2.5),
        ctor(Item.ReanimatedSam, Item.Sam * 120 >> Item.ReanimatedSam * 30),
        assy(Item.ReinforcedIronPlate, Item.IronPlate * 30 + Item.Screw * 60 >> Item.ReinforcedIronPlate * 5),
        assy(Item.RifleAmmo, Item.CopperSheet * 15 + Item.SmokelessPowder * 10 >> Item.RifleAmmo * 75),
        blend(Item.RocketFuel, Item.Turbofuel * 60 + Item.NitricAcid * 10 >> Item.RocketFuel * 100 + Item.CompactedCoal * 10),
        assy(Item.Rotor, Item.IronRod * 20 + Item.Screw * 100 >> Item.Rotor * 4),
        refine(Item.Rubber, Item.CrudeOil * 30 >> Item.Rubber * 20 + Item.HeavyOilResidue * 20),
        refine("ResidualRubber", Item.PolymerResin * 40 + Item.Water * 40 >> Item.Rubber * 20),
        manu(Item.SamFluctuator, Item.ReanimatedSam * 60 + Item.Wire * 50 + Item.SteelPipe * 30 >> Item.SamFluctuator * 10),
        ctor(Item.Screw, Item.IronRod * 10 >> Item.Screw * 40),
        assy(Item.ShatterRebar, Item.IronRebar * 10 + Item.QuartzCrystal * 15 >> Item.ShatterRebar * 5),
        ctor(Item.Silica, Item.RawQuartz * 22.5 >> Item.Silica * 37.5),
        manu(Item.SingularityCell, Item.NuclearPasta * 1 + Item.DarkMatterCrystal * 20 + Item.IronPlate * 100 + Item.Concrete * 200 >> Item.SingularityCell * 10),
        assy(Item.SmartPlating, Item.ReinforcedIronPlate * 2 + Item.Rotor * 2 >> Item.SmartPlating * 2),
        refine(Item.SmokelessPowder, Item.BlackPowder * 20 + Item.HeavyOilResidue * 10 >> Item.SmokelessPowder * 20),
        ctor(Item.SolidBiofuel, Item.Biomass * 120 >> Item.SolidBiofuel * 60),
        assy(Item.Stator, Item.SteelPipe * 15 + Item.Wire * 40 >> Item.Stator * 5),
        ctor(Item.SteelBeam, Item.SteelIngot * 60 >> Item.SteelBeam * 15),
        foundry(Item.SteelIngot, Item.IronOre * 45 + Item.Coal * 45 >> Item.SteelIngot * 45),
        ctor(Item.SteelPipe, Item.SteelIngot * 30 >> Item.SteelPipe * 20),
        assy(Item.StunRebar, Item.IronRebar * 10 + Item.Quickwire * 50 >> Item.StunRebar * 10),
        refine(Item.SulfuricAcid, Item.Sulfur * 50 + Item.Water * 50 >> Item.SulfuricAcid * 50),
        manu(Item.Supercomputer, Item.Computer * 7.5 + Item.AiLimiter * 3.75 + Item.HighSpeedConnector * 5.625 + Item.Plastic * 52.5 >> Item.Supercomputer * 1.875),
        encode(
            Item.SuperpositionOscillator,
            Item.DarkMatterCrystal * 30 + Item.CrystalOscillator * 5 + Item.AlcladAluminumSheet * 45 + Item.ExcitedPhotonicMatter * 125
            >> Item.SuperpositionOscillator * 5 + Item.DarkMatterResidue * 125,
        ),
        manu(Item.ThermalPropulsionRocket, Item.ModularEngine * 2.5 + Item.TurboMotor * 1 + Item.CoolingSystem * 3 + Item.FusedModularFrame * 1 >> Item.ThermalPropulsionRocket * 1),
        convert(Item.TimeCrystal, Item.Diamonds * 12 >> Item.TimeCrystal * 6),
        manu(Item.TurboMotor, Item.CoolingSystem * 7.5 + Item.RadioControlUnit * 3.75 + Item.Motor * 7.5 + Item.Rubber * 45 >> Item.TurboMotor * 1.875),
        manu("TurboRifleAmmo#Manufacturer", Item.RifleAmmo * 120 + Item.AluminumCasing * 15 + Item.PackagedTurbofuel * 15 >> Item.TurboRifleAmmo * 250),
        blend("TurboRifleAmmo#Blender", Item.RifleAmmo * 120 + Item.AluminumCasing * 15 + Item.Turbofuel * 15 >> Item.TurboRifleAmmo * 250),
        refine(Item.Turbofuel, Item.Fuel * 22.5 + Item.CompactedCoal * 15 >> Item.Turbofuel * 18.75),
        manu(Item.UraniumFuelRod, Item.EncasedUraniumCell * 20 + Item.EncasedIndustrialBeam * 1.2 + Item.ElectromagneticControlRod * 2 >> Item.UraniumFuelRod * 0.4),
        assy(Item.VersatileFramework, Item.ModularFrame * 2.5 + Item.SteelBeam * 30 >> Item.VersatileFramework * 5),
        ctor(Item.Wire, Item.CopperIngot * 15 >> Item.Wire * 30),
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
        can(Item.PackagedLiquidBiofuel, Item.LiquidBiofuel * 40 >> Item.PackagedLiquidBiofuel * 40),
        uncan(Item.LiquidBiofuel, Item.PackagedLiquidBiofuel * 60 >> Item.LiquidBiofuel * 60),
        tank(Item.PackagedNitricAcid, Item.NitricAcid * 30 >> Item.PackagedNitricAcid * 30),
        untank(Item.NitricAcid, Item.PackagedNitricAcid * 30 >> Item.NitricAcid * 30),
        tank(Item.PackagedNitrogenGas, Item.NitrogenGas * 240 >> Item.PackagedNitrogenGas * 60),
        untank(Item.NitrogenGas, Item.PackagedNitrogenGas * 60 >> Item.NitrogenGas * 240),
        tank(Item.PackagedRocketFuel, Item.RocketFuel * 120 >> Item.PackagedRocketFuel * 60),
        untank(Item.RocketFuel, Item.PackagedRocketFuel * 60 >> Item.RocketFuel * 120),
        can(Item.PackagedSulfuricAcid, Item.SulfuricAcid * 40 >> Item.PackagedSulfuricAcid * 40),
        uncan(Item.SulfuricAcid, Item.PackagedSulfuricAcid * 60 >> Item.SulfuricAcid * 60),
        can(Item.PackagedTurbofuel, Item.Turbofuel * 20 >> Item.PackagedTurbofuel * 20),
        uncan(Item.Turbofuel, Item.PackagedTurbofuel * 20 >> Item.Turbofuel * 20),
        can(Item.PackagedWater, Item.Water * 60 >> Item.PackagedWater * 60),
        uncan(Item.Water, Item.PackagedWater * 120 >> Item.Water * 120),
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
        convert("Limestone#Sulfur", Item.ReanimatedSam * 10 + Item.Sulfur * 20 >> Item.Limestone * 120),
        convert("NitrogenGas#Bauxite", Item.ReanimatedSam * 10 + Item.Bauxite * 100 >> Item.NitrogenGas * 120),
        convert("NitrogenGas#Caterium", Item.ReanimatedSam * 10 + Item.CateriumOre * 120 >> Item.NitrogenGas * 120),
        convert("RawQuartz#Bauxite", Item.ReanimatedSam * 10 + Item.Bauxite * 100 >> Item.RawQuartz * 120),
        convert("RawQuartz#Coal", Item.ReanimatedSam * 10 + Item.Coal * 240 >> Item.RawQuartz * 120),
        convert("Sulfur#Coal", Item.ReanimatedSam * 10 + Item.Coal * 200 >> Item.Sulfur * 120),
        convert("Sulfur#Iron", Item.ReanimatedSam * 10 + Item.IronOre * 300 >> Item.Sulfur * 120),
        convert("Uranium#Bauxite", Item.ReanimatedSam * 10 + Item.Bauxite * 480 >> Item.Uranium * 120),
    ]


def power() -> List[Recipe]:
    return [
        bioburn(Item.Leaves, Item.Leaves * 120),
        bioburn(Item.Wood, Item.Wood * 18),
        bioburn(Item.Mycelia, Item.Mycelia * 90),
        bioburn(Item.Biomass, Item.Biomass * 10),
        bioburn(Item.SolidBiofuel, Item.SolidBiofuel * 4),
        bioburn(Item.PackagedLiquidBiofuel, Item.PackagedLiquidBiofuel * 2.4),
        coal(Item.Coal, Item.Coal * 15),
        coal(Item.CompactedCoal, Item.CompactedCoal * 7.14286),
        coal(Item.PetroleumCoke, Item.PetroleumCoke * 25),
        fuel(Item.Fuel, Item.Fuel * 20),
        fuel(Item.Turbofuel, Item.Turbofuel * 7.5),
        fuel(Item.LiquidBiofuel, Item.LiquidBiofuel * 20),
        fuel(Item.RocketFuel, Item.RocketFuel * 4.16667),
        fuel(Item.IonizedFuel, Item.IonizedFuel * 3),
        nuke(Item.PlutoniumFuelRod, Item.PlutoniumFuelRod * 0.1 >> Item.PlutoniumWaste * 1),
        nuke(Item.UraniumFuelRod, Item.UraniumFuelRod * 0.2 >> Item.UraniumWaste * 10),
        nuke(Item.FicsoniumFuelRod, Item.FicsoniumFuelRod * 1 >> Rates()),
    ]


def alternates() -> List[Recipe]:
    return [
        assy("PlasticAiLimiter", Item.Quickwire * 120 + Item.Plastic * 28 >> Item.AiLimiter * 8),
        refine("SloppyAlumina", Item.Bauxite * 200 + Item.Water * 200 >> Item.AluminaSolution * 240),
        assy("AlcladCasing", Item.AluminumIngot * 150 + Item.CopperIngot * 75 >> Item.AluminumCasing * 112.5),
        smelt("PureAluminumIngot", Item.AluminumScrap * 60 >> Item.AluminumIngot * 30),
        refine("ElectrodeAluminumScrap", Item.AluminaSolution * 180 + Item.PetroleumCoke * 60 >> Item.AluminumScrap * 300 + Item.Water * 105),
        blend("InstantScrap", Item.Bauxite * 150 + Item.Coal * 100 + Item.SulfuricAcid * 50 + Item.Water * 60 >> Item.AluminumScrap * 300 + Item.Water * 50),
        manu("AutomatedSpeedWiring", Item.Stator * 3.75 + Item.Wire * 75 + Item.HighSpeedConnector * 1.875 >> Item.AutomatedWiring * 7.5),
        manu("ClassicBattery", Item.Sulfur * 45 + Item.AlcladAluminumSheet * 52.5 + Item.Plastic * 80 + Item.Wire * 90 >> Item.Battery * 30),
        assy("FineBlackPowder", Item.Sulfur * 7.5 + Item.CompactedCoal * 15 >> Item.BlackPowder * 45),
        refine("CoatedCable", Item.Wire * 37.5 + Item.HeavyOilResidue * 15 >> Item.Cable * 67.5),
        assy("QuickwireCable", Item.Quickwire * 7.5 + Item.Rubber * 5 >> Item.Cable * 27.5),
        assy("InsulatedCable", Item.Wire * 45 + Item.Rubber * 30 >> Item.Cable * 100),
        refine("PureCateriumIngot", Item.CateriumOre * 24 + Item.Water * 24 >> Item.CateriumIngot * 12),
        foundry("TemperedCateriumIngot", Item.CateriumOre * 45 + Item.PetroleumCoke * 15 >> Item.CateriumIngot * 22.5),
        refine("LeachedCateriumIngot", Item.CateriumOre * 54 + Item.SulfuricAcid * 30 >> Item.CateriumIngot * 36),
        assy("ElectrodeCircuitBoard", Item.Rubber * 20 + Item.PetroleumCoke * 40 >> Item.CircuitBoard * 5),
        assy("CateriumCircuitBoard", Item.Plastic * 12.5 + Item.Quickwire * 37.5 >> Item.CircuitBoard * 8.75),
        assy("SiliconCircuitBoard", Item.CopperSheet * 27.5 + Item.Silica * 27.5 >> Item.CircuitBoard * 12.5),
        ctor("Charcoal", Item.Wood * 15 >> Item.Coal * 150),
        ctor("Biocoal", Item.Biomass * 37.5 >> Item.Coal * 45),
        assy("CompactedCoal", Item.Coal * 25 + Item.Sulfur * 25 >> Item.CompactedCoal * 25),
        assy("CrystalComputer", Item.CircuitBoard * 5 + Item.CrystalOscillator * 1.66667 >> Item.Computer * 3.33333),
        manu("CateriumComputer", Item.CircuitBoard * 15 + Item.Quickwire * 52.5 + Item.Rubber * 22.5 >> Item.Computer * 3.75),
        refine("WetConcrete", Item.Limestone * 120 + Item.Water * 100 >> Item.Concrete * 80),
        assy("RubberConcrete", Item.Limestone * 100 + Item.Rubber * 20 >> Item.Concrete * 90),
        assy("FineConcrete", Item.Silica * 15 + Item.Limestone * 60 >> Item.Concrete * 60),
        blend("CoolingDevice", Item.HeatSink * 10 + Item.Motor * 2.5 + Item.NitrogenGas * 60 >> Item.CoolingSystem * 5),
        refine("PureCopperIngot", Item.CopperOre * 15 + Item.Water * 10 >> Item.CopperIngot * 37.5),
        foundry("CopperAlloyIngot", Item.CopperOre * 50 + Item.IronOre * 50 >> Item.CopperIngot * 100),
        foundry("TemperedCopperIngot", Item.CopperOre * 25 + Item.PetroleumCoke * 40 >> Item.CopperIngot * 60),
        refine("LeachedCopperIngot", Item.CopperOre * 45 + Item.SulfuricAcid * 25 >> Item.CopperIngot * 110),
        refine("SteamedCopperSheet", Item.CopperIngot * 22.5 + Item.Water * 22.5 >> Item.CopperSheet * 22.5),
        manu("InsulatedCrystalOscillator", Item.QuartzCrystal * 18.75 + Item.Rubber * 13.125 + Item.AiLimiter * 1.875 >> Item.CrystalOscillator * 1.875),
        accel("DarkMatterTrap", Item.TimeCrystal * 30 + Item.DarkMatterResidue * 150 >> Item.DarkMatterCrystal * 60),
        accel("DarkMatterCrystallization", Item.DarkMatterResidue * 200 >> Item.DarkMatterCrystal * 20),
        accel("TurboDiamonds", Item.Coal * 600 + Item.PackagedTurbofuel * 40 >> Item.Diamonds * 60),
        convert("PinkDiamonds", Item.Coal * 120 + Item.QuartzCrystal * 45 >> Item.Diamonds * 15),
        accel("PetroleumDiamonds", Item.PetroleumCoke * 720 >> Item.Diamonds * 30),
        accel("OilBasedDiamonds", Item.CrudeOil * 200 >> Item.Diamonds * 40),
        accel("CloudyDiamonds", Item.Coal * 240 + Item.Limestone * 480 >> Item.Diamonds * 20),
        assy("ElectromagneticConnectionRod", Item.Stator * 8 + Item.HighSpeedConnector * 4 >> Item.ElectromagneticControlRod * 8),
        ctor("SteelCanister", Item.SteelIngot * 40 >> Item.EmptyCanister * 40),
        assy("CoatedIronCanister", Item.IronPlate * 30 + Item.CopperSheet * 15 >> Item.EmptyCanister * 60),
        assy("EncasedIndustrialPipe", Item.SteelPipe * 24 + Item.Concrete * 20 >> Item.EncasedIndustrialBeam * 4),
        accel("InstantPlutoniumCell", Item.NonFissileUranium * 75 + Item.AluminumCasing * 10 >> Item.EncasedPlutoniumCell * 10),
        manu("InfusedUraniumCell", Item.Uranium * 25 + Item.Silica * 15 + Item.Sulfur * 25 + Item.Quickwire * 75 >> Item.EncasedUraniumCell * 20),
        refine("PolyesterFabric", Item.PolymerResin * 30 + Item.Water * 30 >> Item.Fabric * 30),
        blend("DilutedFuel", Item.HeavyOilResidue * 50 + Item.Water * 100 >> Item.Fuel * 100),
        blend("HeatFusedFrame", Item.HeavyModularFrame * 3 + Item.AluminumIngot * 150 + Item.NitricAcid * 24 + Item.Fuel * 30 >> Item.FusedModularFrame * 3),
        assy("HeatExchanger", Item.AluminumCasing * 30 + Item.Rubber * 30 >> Item.HeatSink * 10),
        manu("HeavyFlexibleFrame", Item.ModularFrame * 18.75 + Item.EncasedIndustrialBeam * 11.25 + Item.Rubber * 75 + Item.Screw * 390 >> Item.HeavyModularFrame * 3.75),
        manu("HeavyEncasedFrame", Item.ModularFrame * 7.5 + Item.EncasedIndustrialBeam * 9.375 + Item.SteelPipe * 33.75 + Item.Concrete * 20.625 >> Item.HeavyModularFrame * 2.8125),
        refine(Item.HeavyOilResidue, Item.CrudeOil * 30 >> Item.HeavyOilResidue * 40 + Item.PolymerResin * 20),
        manu("SiliconHighSpeedConnector", Item.Quickwire * 90 + Item.Silica * 37.5 + Item.CircuitBoard * 3 >> Item.HighSpeedConnector * 3),
        convert("DarkIonFuel", Item.PackagedRocketFuel * 240 + Item.DarkMatterCrystal * 80 >> Item.IonizedFuel * 200 + Item.CompactedCoal * 40),
        refine("PureIronIngot", Item.IronOre * 35 + Item.Water * 20 >> Item.IronIngot * 65),
        refine("LeachedIronIngot", Item.IronOre * 50 + Item.SulfuricAcid * 10 >> Item.IronIngot * 100),
        foundry("BasicIronIngot", Item.IronOre * 25 + Item.Limestone * 40 >> Item.IronIngot * 50),
        foundry("IronAlloyIngot", Item.IronOre * 40 + Item.CopperOre * 10 >> Item.IronIngot * 75),
        assy("CoatedIronPlate", Item.IronIngot * 37.5 + Item.Plastic * 7.5 >> Item.IronPlate * 75),
        foundry("SteelCastPlate", Item.IronIngot * 15 + Item.SteelIngot * 15 >> Item.IronPlate * 45),
        ctor("SteelRod", Item.SteelIngot * 12 >> Item.IronRod * 48),
        ctor("AluminumRod", Item.AluminumIngot * 7.5 >> Item.IronRod * 52.5),
        assy("BoltedFrame", Item.ReinforcedIronPlate * 7.5 + Item.Screw * 140 >> Item.ModularFrame * 5),
        assy("SteeledFrame", Item.ReinforcedIronPlate * 2 + Item.SteelPipe * 10 >> Item.ModularFrame * 3),
        assy("ElectricMotor", Item.ElectromagneticControlRod * 3.75 + Item.Rotor * 7.5 >> Item.Motor * 7.5),
        manu("RigorMotor", Item.Rotor * 3.75 + Item.Stator * 3.75 + Item.CrystalOscillator * 1.25 >> Item.Motor * 7.5),
        blend("FertileUranium", Item.Uranium * 25 + Item.UraniumWaste * 25 + Item.NitricAcid * 15 + Item.SulfuricAcid * 25 >> Item.NonFissileUranium * 100 + Item.Water * 40),
        refine("DilutedPackagedFuel", Item.HeavyOilResidue * 30 + Item.PackagedWater * 60 >> Item.PackagedFuel * 60),
        refine("RecycledPlastic", Item.Rubber * 30 + Item.Fuel * 30 >> Item.Plastic * 60),
        assy("PlutoniumFuelUnit", Item.EncasedPlutoniumCell * 10 + Item.PressureConversionCube * 0.5 >> Item.PlutoniumFuelRod * 0.5),
        refine(Item.PolymerResin, Item.CrudeOil * 60 >> Item.PolymerResin * 130 + Item.HeavyOilResidue * 20),
        assy("AutomatedMiner", Item.SteelPipe * 4 + Item.IronPlate * 4 >> Item.PortableMiner * 1),
        refine("PureQuartzCrystal", Item.RawQuartz * 67.5 + Item.Water * 37.5 >> Item.QuartzCrystal * 52.5),
        refine("QuartzPurification", Item.RawQuartz * 120 + Item.NitricAcid * 10 >> Item.QuartzCrystal * 75 + Item.DissolvedSilica * 60),
        foundry("FusedQuartzCrystal", Item.RawQuartz * 75 + Item.Coal * 36 >> Item.QuartzCrystal * 54),
        assy("FusedQuickwire", Item.CateriumIngot * 7.5 + Item.CopperIngot * 37.5 >> Item.Quickwire * 90),
        manu("RadioControlSystem", Item.CrystalOscillator * 1.5 + Item.CircuitBoard * 15 + Item.AluminumCasing * 90 + Item.Rubber * 45 >> Item.RadioControlUnit * 4.5),
        manu("RadioConnectionUnit", Item.HeatSink * 15 + Item.HighSpeedConnector * 7.5 + Item.QuartzCrystal * 45 >> Item.RadioControlUnit * 3.75),
        assy("AdheredIronPlate", Item.IronPlate * 11.25 + Item.Rubber * 3.75 >> Item.ReinforcedIronPlate * 3.75),
        assy("StitchedIronPlate", Item.IronPlate * 18.75 + Item.Wire * 37.6 >> Item.ReinforcedIronPlate * 5.625),
        assy("BoltedIronPlate", Item.IronPlate * 90 + Item.Screw * 250 >> Item.ReinforcedIronPlate * 15),
        blend("NitroRocketFuel", Item.Fuel * 120 + Item.NitrogenGas * 90 + Item.Sulfur * 120 + Item.Coal * 60 >> Item.RocketFuel * 180 + Item.CompactedCoal * 30),
        assy("CopperRotor", Item.CopperSheet * 22.5 + Item.Screw * 195 >> Item.Rotor * 11.25),
        assy("SteelRotor", Item.SteelPipe * 10 + Item.Wire * 30 >> Item.Rotor * 5),
        refine("RecycledRubber", Item.Plastic * 30 + Item.Fuel * 30 >> Item.Rubber * 60),
        ctor("SteelScrew", Item.SteelBeam * 5 >> Item.Screw * 260),
        ctor("CastScrew", Item.IronIngot * 12.5 >> Item.Screw * 50),
        blend("DistilledSilica", Item.DissolvedSilica * 120 + Item.Limestone * 50 + Item.Water * 100 >> Item.Silica * 270 + Item.Water * 80),
        assy("CheapSilica", Item.RawQuartz * 22.5 + Item.Limestone * 37.5 >> Item.Silica * 52.5),
        manu("PlasticSmartPlating", Item.ReinforcedIronPlate * 2.5 + Item.Rotor * 2.5 + Item.Plastic * 7.5 >> Item.SmartPlating * 5),
        assy("QuickwireStator", Item.SteelPipe * 16 + Item.Quickwire * 60 >> Item.Stator * 8),
        foundry("MoldedBeam", Item.SteelIngot * 120 + Item.Concrete * 80 >> Item.SteelBeam * 45),
        ctor("AluminumBeam", Item.AluminumIngot * 22.5 >> Item.SteelBeam * 22.5),
        foundry("CokeSteelIngot", Item.IronOre * 75 + Item.PetroleumCoke * 75 >> Item.SteelIngot * 100),
        foundry("CompactedSteelIngot", Item.IronOre * 5 + Item.CompactedCoal * 2.5 >> Item.SteelIngot * 10),
        foundry("SolidSteelIngot", Item.IronIngot * 40 + Item.Coal * 40 >> Item.SteelIngot * 60),
        foundry("MoldedSteelPipe", Item.SteelIngot * 50 + Item.Concrete * 30 >> Item.SteelPipe * 50),
        ctor("IronPipe", Item.IronIngot * 100 >> Item.SteelPipe * 25),
        manu("SuperStateComputer", Item.Computer * 7.2 + Item.ElectromagneticControlRod * 2.4 + Item.Battery * 24 + Item.Wire * 60 >> Item.Supercomputer * 2.4),
        assy("OcSupercomputer", Item.RadioControlUnit * 6 + Item.CoolingSystem * 6 >> Item.Supercomputer * 3),
        manu("TurboPressureMotor", Item.Motor * 7.5 + Item.PressureConversionCube * 1.875 + Item.PackagedNitrogenGas * 45 + Item.Stator * 15 >> Item.TurboMotor * 3.75),
        manu("TurboElectricMotor", Item.Motor * 6.5625 + Item.RadioControlUnit * 8.4375 + Item.ElectromagneticControlRod * 4.6875 + Item.Rotor * 6.5625 >> Item.TurboMotor * 2.8125),
        refine("TurboHeavyFuel", Item.HeavyOilResidue * 37.5 + Item.CompactedCoal * 30 >> Item.Turbofuel * 30),
        blend("TurboBlendFuel", Item.Fuel * 15 + Item.HeavyOilResidue * 30 + Item.Sulfur * 22.5 + Item.PetroleumCoke * 22.5 >> Item.Turbofuel * 45),
        manu("UraniumFuelUnit", Item.EncasedUraniumCell * 20 + Item.ElectromagneticControlRod * 2 + Item.CrystalOscillator * 0.6 + Item.Rotor * 2 >> Item.UraniumFuelRod * 0.6),
        manu("FlexibleFramework", Item.ModularFrame * 3.75 + Item.SteelBeam * 22.5 + Item.Rubber * 30 >> Item.VersatileFramework * 7.5),
        assy("FusedWire", Item.CopperIngot * 12 + Item.CateriumIngot * 3 >> Item.Wire * 90),
        ctor("CateriumWire", Item.CateriumIngot * 15 >> Item.Wire * 120),
        ctor("IronWire", Item.IronIngot * 12.5 >> Item.Wire * 22.5),
    ]


def awesome_sink() -> List[Recipe]:
    return [sink(item) for item in Item if sinkable(item)]

def raw() -> List[Recipe]:
    return [
        recipe(Item.Bauxite, Building.Miner, Rates() >> Item.Bauxite * 1),
        recipe(Item.CateriumOre, Building.Miner, Rates() >> Item.CateriumOre * 1),
        recipe(Item.Coal, Building.Miner, Rates() >> Item.Coal * 1),
        recipe(Item.CopperOre, Building.Miner, Rates() >> Item.CopperOre * 1),
        recipe(Item.CrudeOil, Building.OilExtractor, Rates() >> Item.CrudeOil * 1),
        recipe(Item.IronOre, Building.Miner, Rates() >> Item.IronOre * 1),
        recipe(Item.Limestone, Building.Miner, Rates() >> Item.Limestone * 1),
        recipe(Item.NitrogenGas, Building.ResourceWell, Rates() >> Item.NitrogenGas * 1),
        recipe(Item.RawQuartz, Building.Miner, Rates() >> Item.RawQuartz * 1),
        recipe(Item.Sam, Building.Miner, Rates() >> Item.Sam * 1),
        recipe(Item.Sulfur, Building.Miner, Rates() >> Item.Sulfur * 1),
        recipe(Item.Uranium, Building.Miner, Rates() >> Item.Uranium * 1),
        recipe(Item.Water, Building.WaterExtractor, Rates() >> Item.Water * 1),
    ]

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


def bioburn(name: str | Item, input: Rates) -> Recipe:
    return recipe(f"BiomassBurner#{name}", Building.BiomassBurner, input >> Item.MwPower * 30)


def coal(name: str | Item, input: Rates) -> Recipe:
    return recipe(f"CoalGenerator#{name}", Building.CoalGenerator, input + Item.Water * 45 >> Item.MwPower * 75)


def fuel(name: str | Item, input: Rates) -> Recipe:
    return recipe(f"FuelGenerator#{name}", Building.FuelGenerator, input >> Item.MwPower * 250)


def nuke(name: str | Item, inout: tuple[Rates, Rates]) -> Recipe:
    return recipe(f"NuclearPowerPlant#{name}", Building.NuclearPowerPlant, inout[0] + Item.Water * 240 >> inout[1] + Item.MwPower * 2500)
