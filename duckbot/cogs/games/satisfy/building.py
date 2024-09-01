from enum import Enum, auto, unique


@unique
class Building(Enum):
    Miner = auto()
    WaterExtractor = auto()
    OilExtractor = auto()
    ResourceWell = auto()
    Smelter = auto()
    Constructor = auto()
    Assembler = auto()
    Manufacturer = auto()
    Refinery = auto()
    Packager = auto()
    Blender = auto()
    BiomassBurner = auto()
    AwesomeSink = auto()
    CoalGenerator = auto()
    Foundry = auto()
    ParticleAccelerator = auto()
    FuelGenerator = auto()
    NuclearPowerPlant = auto()

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name
