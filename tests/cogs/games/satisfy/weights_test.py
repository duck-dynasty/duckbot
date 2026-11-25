from pytest import approx

from duckbot.cogs.games.satisfy.item import Item
from duckbot.cogs.games.satisfy.weights import default_weights


def test_default_weights():
    w = default_weights()
    assert w[Item.AiLimiter] == approx(12 * w[Item.CateriumOre] + 10 * w[Item.CopperOre])
    assert w[Item.BallisticWarpDrive] == approx(w[Item.ThermalPropulsionRocket] + 5 * w[Item.SingularityCell] + 2 * w[Item.SuperpositionOscillator] + 40 * w[Item.DarkMatterCrystal])
    assert 2 * w[Item.ThermalPropulsionRocket] == approx(5 * w[Item.ModularEngine] + 2 * w[Item.TurboMotor] + 6 * w[Item.CoolingSystem] + 2 * w[Item.FusedModularFrame])
    assert w[Item.ModularEngine] == approx(2 * w[Item.Motor] + 15 * w[Item.Rubber] + 2 * w[Item.SmartPlating])
    assert w[Item.SmartPlating] == approx(w[Item.ReinforcedIronPlate] + w[Item.Rotor])
    assert w[Item.ReinforcedIronPlate] == approx(6 * w[Item.IronPlate] + 12 * w[Item.Screw])
    assert 3 * w[Item.IronOre] == approx(2 * w[Item.IronPlate])
    assert w[Item.IronOre] == w[Item.IronRod]
    assert w[Item.IronOre] == w[Item.IronIngot]
