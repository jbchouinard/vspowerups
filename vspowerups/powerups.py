from collections import defaultdict
from pprint import pprint


def upgrade_cost(base_cost, tiers, n_upgrades):
    cost = base_cost / 10
    n = 10 + n_upgrades
    if tiers == 0:
        return 0
    elif tiers == 1:
        return n * cost
    elif tiers == 2:
        return (3 * n + 2) * cost
    elif tiers == 3:
        return (6 * n + 8) * cost
    elif tiers == 4:
        return (10 * n + 20) * cost
    else:
        return (15 * n + 40) * cost


class PowerUp:
    MAX_TIER = 0
    BASE_COST = 0

    def __init__(self):
        self.current_tier = 0

    @property
    def name(self):
        return self.__class__.__name__

    def upgrade_max(self):
        self.current_tier = self.MAX_TIER

    def upgrade(self):
        if self.current_tier == self.MAX_TIER:
            raise ValueError("already max tier")
        self.current_tier += 1

    def upgrade_cost(self, n_upgrades):
        return (1 + (0.1 * n_upgrades)) * self.current_tier * self.BASE_COST

    def score(self):
        return (self.current_tier + 1) * self.BASE_COST

    @classmethod
    def full_upgrade_cost(cls, n_upgrades):
        return upgrade_cost(cls.BASE_COST, cls.MAX_TIER, n_upgrades)

    def __repr__(self):
        return f"{self.name}({self.current_tier})"

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__
            and self.current_tier == other.current_tier
        )


POWER_UPS = []


def power_up(max_tier, base_cost, name):
    kls = type(name, (PowerUp,), {"BASE_COST": base_cost, "MAX_TIER": max_tier})
    POWER_UPS.append(kls)
    return kls


Might = power_up(5, 200, "Might")
Armor = power_up(3, 600, "Armor")
MaxHealth = power_up(3, 200, "MaxHealth")
Recovery = power_up(5, 200, "Recovery")
Cooldown = power_up(2, 900, "Cooldown")
Area = power_up(2, 300, "Area")
Speed = power_up(2, 300, "Speed")
Duration = power_up(2, 300, "Duration")
Amount = power_up(1, 5000, "Amount")
MoveSpeed = power_up(2, 300, "MoveSpeed")
Magnet = power_up(2, 300, "Magnet")
Luck = power_up(3, 600, "Luck")
Growth = power_up(5, 900, "Growth")
Greed = power_up(5, 200, "Greed")


def optimize(powerups):
    pups = sorted(powerups, key=lambda p: p.score(), reverse=True)
    n_upgrades = 0
    total_cost = 0
    for pup in pups:
        total_cost += upgrade_cost(pup.BASE_COST, pup.current_tier, n_upgrades)
        n_upgrades += pup.current_tier
    return total_cost, pups


if __name__ == "__main__":
    pups = []
    for p in POWER_UPS:
        pup = p()
        pup.upgrade_max()
        pups.append(pup)
    pprint(optimize(pups))
