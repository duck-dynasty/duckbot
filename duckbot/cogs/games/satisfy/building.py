from enum import Enum, auto, unique


@unique
class Building(Enum):
    def _generate_next_value_(name, start, count, last_values):  # noqa: N805
        return name

    AlienPowerAugmenter = (auto(), 0, 0)
    Assembler = (auto(), 3, 2)
    AwesomeSink = (auto(), 0, 0)
    BiomassBurner = (auto(), 3, 0)
    Blender = (auto(), 3, 4)
    CoalGenerator = (auto(), 3, 0)
    Constructor = (auto(), 3, 1)
    Converter = (auto(), 3, 2)
    CraftingBench = (auto(), 0, 0)
    EquipmentWorkshop = (auto(), 0, 0)
    Foundry = (auto(), 3, 2)
    FuelGenerator = (auto(), 3, 0)
    GeothermalGenerator = (auto(), 0, 0)
    Manufacturer = (auto(), 3, 4)
    Miner = (auto(), 3, 0)
    NuclearPowerPlant = (auto(), 3, 0)
    OilExtractor = (auto(), 3, 0)
    Packager = (auto(), 3, 0)
    ParticleAccelerator = (auto(), 3, 4)
    QuantumEncoder = (auto(), 3, 4)
    Refinery = (auto(), 3, 2)
    ResourceWell = (auto(), 3, 0)
    Smelter = (auto(), 3, 1)
    WaterExtractor = (auto(), 3, 0)

    def __init__(self, value, max_shards, max_sloop: int):
        self.max_shards = max_shards
        self.max_sloop = max_sloop

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name
