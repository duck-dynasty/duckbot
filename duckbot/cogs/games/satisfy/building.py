from enum import Enum, auto, unique


@unique
class Building(Enum):
    Miner = (auto(), 3, 0)
    WaterExtractor = (auto(), 3, 0)
    OilExtractor = (auto(), 3, 0)
    ResourceWell = (auto(), 3, 0)
    Smelter = (auto(), 3, 1)
    Constructor = (auto(), 3, 1)
    Assembler = (auto(), 3, 2)
    Manufacturer = (auto(), 3, 4)
    Refinery = (auto(), 3, 2)
    Packager = (auto(), 3, 2)
    Blender = (auto(), 3, 4)
    BiomassBurner = (auto(), 3, 0)
    AwesomeSink = (auto(), 0, 0)
    CoalGenerator = (auto(), 3, 0)
    Foundry = (auto(), 3, 2)
    ParticleAccelerator = (auto(), 3, 4)
    FuelGenerator = (auto(), 3, 0)
    NuclearPowerPlant = (auto(), 3, 0)

    def _generate_next_value_(name, start, count, last_values):  # noqa: N805
        return name

    def __init__(self, value, max_shards, max_sloop: int):
        self.max_shards = max_shards
        self.max_sloop = max_sloop

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name
