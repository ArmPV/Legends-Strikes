from dataclasses import dataclass
from typing import Optional, List
from game.utils import Point
from game.effects import Effect
from game.creatures import Creature
from game.constants import TOWERS_STATS, MAX_TOWER_LEVEL, SLOW_FACTOR, TOWER_HP
import math


@dataclass
class Tower:
    damage: int
    range: float
    level: int
    cost: int
    position: Point
    tower_type: str = "basic"
    effect: Optional[Effect] = None
    attack_speed: int = 30
    cooldown: int = 0
    upgrade_cost: int = 80
    color: tuple = (100, 150, 200)
    hp: int = 200
    max_hp: int = 200
    aura_type: Optional[str] = None
    aura_value: float = 0
    aura_range: float = 0
    bonus_damage: float = 0
    total_spent: int = 0

    def apply_effect(self, effect: Effect):
        self.effect = effect

    def upgrade(self):
        if self.level < MAX_TOWER_LEVEL:
            profiles = {
                "basic": {"damage": 1.18, "range": 8, "speed": 0.97, "hp": 14},
                "sniper": {"damage": 1.14, "range": 12, "speed": 0.99, "hp": 10},
                "slow": {"damage": 1.08, "range": 8, "speed": 0.95, "hp": 12},
                "aoe": {"damage": 1.12, "range": 6, "speed": 0.96, "hp": 12},
                "detector": {"damage": 1.08, "range": 10, "speed": 0.96, "hp": 12},
                "buffer": {"damage": 1.0, "range": 0, "speed": 1.0, "hp": 12, "aura_range": 10, "aura_value": 0.04},
                "radar": {"damage": 1.06, "range": 10, "speed": 0.95, "hp": 12, "aura_range": 12},
            }
            profile = profiles.get(self.tower_type, {"damage": 1.12, "range": 8, "speed": 0.97, "hp": 12})

            self.total_spent += self.upgrade_cost
            self.level += 1
            if self.damage > 0:
                self.damage = max(self.damage + 1, int(round(self.damage * profile["damage"])))
            self.range += profile.get("range", 0)
            if self.attack_speed > 0:
                self.attack_speed = max(12, int(self.attack_speed * profile.get("speed", 0.9)))

            hp_gain = profile.get("hp", 0)
            self.max_hp += hp_gain
            self.hp = min(self.max_hp, self.hp + hp_gain)

            if self.aura_type == "damage_boost":
                self.aura_value = min(0.55, self.aura_value + profile.get("aura_value", 0.05))
            if self.aura_type:
                self.aura_range += profile.get("aura_range", 0)

            self.upgrade_cost = int(self.upgrade_cost * 1.95)
            return True
        return False

    def attack(self, creatures: List[Creature]) -> Optional[Creature]:
        if self.cooldown > 0:
            self.cooldown -= 1
            return None

        if self.damage <= 0 and self.aura_type:
            return None

        effective_damage = int(self.damage * (1 + self.bonus_damage))

        closest = None
        closest_dist = self.range

        for creature in creatures:
            if not creature.alive:
                continue

            if getattr(creature, 'underground', False):
                continue

            if not creature.is_visible and self.tower_type not in ("detector", "radar"):
                continue

            dist = math.hypot(self.position.x - creature.position.x,
                              self.position.y - creature.position.y)
            if dist < closest_dist:
                closest_dist = dist
                closest = creature

        if closest:
            closest.take_damage(effective_damage)
            if self.tower_type == "sniper" and closest.alive:
                closest.take_damage(max(1, effective_damage // 4))
            self.cooldown = self.attack_speed

            if self.tower_type == "slow" and closest.alive:
                slow_duration = 28 + self.level * 10
                closest.apply_effect(Effect("slow", slow_duration, True, "tower"))

            if self.tower_type == "aoe" and closest.alive:
                splash_radius = 32 + (self.level - 1) * 6
                for creature in creatures:
                    if creature != closest and creature.alive:
                        dist = math.hypot(closest.position.x - creature.position.x,
                                          closest.position.y - creature.position.y)
                        if dist < splash_radius:
                            creature.take_damage(effective_damage // 2)

            return closest
        return None


class TowerFactory:

    @staticmethod
    def _create(tower_type: str, x: float, y: float) -> Tower:
        stats = TOWERS_STATS[tower_type]
        hp = TOWER_HP.get(tower_type, 200)
        return Tower(
            damage=stats['damage'],
            range=stats['range'],
            level=1,
            cost=stats['cost'],
            upgrade_cost=stats['upgrade_cost'],
            position=Point(x, y),
            tower_type=tower_type,
            attack_speed=stats['attack_speed'],
            color=stats['color'],
            hp=hp,
            max_hp=hp,
            aura_type=stats.get('aura_type'),
            aura_value=stats.get('aura_value', 0),
            aura_range=stats.get('aura_range', 0),
            total_spent=stats['cost']
        )

    @staticmethod
    def create_basic(x: float, y: float) -> Tower:
        return TowerFactory._create("basic", x, y)

    @staticmethod
    def create_sniper(x: float, y: float) -> Tower:
        return TowerFactory._create("sniper", x, y)

    @staticmethod
    def create_slow(x: float, y: float) -> Tower:
        return TowerFactory._create("slow", x, y)

    @staticmethod
    def create_aoe(x: float, y: float) -> Tower:
        return TowerFactory._create("aoe", x, y)

    @staticmethod
    def create_detector(x: float, y: float) -> Tower:
        return TowerFactory._create("detector", x, y)

    @staticmethod
    def create_buffer(x: float, y: float) -> Tower:
        return TowerFactory._create("buffer", x, y)

    @staticmethod
    def create_radar(x: float, y: float) -> Tower:
        return TowerFactory._create("radar", x, y)
