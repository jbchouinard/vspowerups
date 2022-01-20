from collections import defaultdict
from pprint import pprint

from vspowerups.optimize import full_upgrade_cost, optimize_cost


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

    @classmethod
    def full_upgrade_cost(cls, n_upgrades):
        return full_upgrade_cost(cls.BASE_COST, cls.MAX_TIER, n_upgrades)

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
    by_cost = defaultdict(list)
    all_costs = []
    for pup in powerups:
        cost = (pup.BASE_COST, pup.current_tier)
        all_costs.append(cost)
        by_cost[cost].append(pup)

    total_cost, optimized = optimize_cost(all_costs)
    sorted_powerups = []
    for cost in optimized:
        sorted_powerups.append(by_cost[cost].pop())
    return total_cost, sorted_powerups


if __name__ == "__main__":
    pups = []
    for p in POWER_UPS:
        pup = p()
        pup.upgrade_max()
        pups.append(pup)
    pprint(optimize(pups))
