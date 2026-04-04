from dataclasses import dataclass
from typing import Optional
from game.utils import Point
from game.effects import Effect
from game.constants import CREATURES_STATS, EFFECT_DURATION
import math


@dataclass
class Creature:
    hp: int
    speed: float
    cost: int
    position: Point
    maxHP: int
    creature_type: str = "normal"
    effect: Optional[Effect] = None
    slow_timer: int = 0
    invisible_timer: int = 0
    is_visible: bool = True
    alive: bool = True
    reward: int = 0
    damage_to_base: int = 20
    armor: float = 0
    movement_type: str = "ground"
    underground: bool = False
    regen_rate: float = 0
    slow_immune: bool = False
    tower_damage: int = 0

    def apply_effect(self, effect: Effect):
        self.effect = effect
        if effect.type == "slow":
            if self.slow_immune:
                return
            self.slow_timer = int(effect.intensity)
        elif effect.type == "invisible":
            self.is_visible = False
            self.invisible_timer = int(effect.intensity)

    def update(self):
        current_speed = self.speed

        if self.slow_timer > 0:
            self.slow_timer -= 1
            current_speed = self.speed * 0.5

        if self.invisible_timer > 0:
            self.invisible_timer -= 1
            self.is_visible = False
            if self.invisible_timer <= 0:
                self.is_visible = True

        if self.regen_rate > 0 and self.hp < self.maxHP:
            self.hp = min(self.maxHP, self.hp + self.regen_rate)

        return current_speed

    def take_damage(self, damage: int):
        reduced_damage = max(0, damage * (1 - self.armor))

        self.hp -= reduced_damage

        if self.hp <= 0:
            self.alive = False
            return True
        return False


    def reached_end(self, end_point: Point) -> bool:
        distance = math.hypot(self.position.x - end_point.x,
                              self.position.y - end_point.y)
        return distance < 10


class CreatureFactory:

    @staticmethod
    def create_normal(x: float, y: float) -> Creature:
        stats = CREATURES_STATS['normal']
        return Creature(
            hp=stats['hp'],
            maxHP=stats['hp'],
            speed=stats['speed'],
            cost=stats['cost'],
            reward=stats['reward'],
            damage_to_base=stats['damage_to_base'],
            position=Point(x, y),
            creature_type="normal"
        )

    @staticmethod
    def create_fast(x: float, y: float) -> Creature:
        stats = CREATURES_STATS['fast']
        return Creature(
            hp=stats['hp'],
            maxHP=stats['hp'],
            speed=stats['speed'],
            cost=stats['cost'],
            reward=stats['reward'],
            damage_to_base=stats['damage_to_base'],
            position=Point(x, y),
            creature_type="fast"
        )

    @staticmethod
    def create_tank(x: float, y: float) -> Creature:
        stats = CREATURES_STATS['tank']
        creature = Creature(
            hp=stats['hp'],
            maxHP=stats['hp'],
            speed=stats['speed'],
            cost=stats['cost'],
            reward=stats['reward'],
            damage_to_base=stats['damage_to_base'],
            position=Point(x, y),
            creature_type="tank"
        )
        creature.armor = 0.5
        return creature

    @staticmethod
    def create_summoner(x: float, y: float) -> Creature:
        stats = CREATURES_STATS['summoner']
        return Creature(
            hp=stats['hp'],
            maxHP=stats['hp'],
            speed=stats['speed'],
            cost=stats['cost'],
            reward=stats['reward'],
            damage_to_base=stats['damage_to_base'],
            position=Point(x, y),
            creature_type="summoner"
        )

    @staticmethod
    def create_invisible(x: float, y: float) -> Creature:
        stats = CREATURES_STATS['invisible']
        creature = Creature(
            hp=stats['hp'],
            maxHP=stats['hp'],
            speed=stats['speed'],
            cost=stats['cost'],
            reward=stats['reward'],
            damage_to_base=stats['damage_to_base'],
            position=Point(x, y),
            creature_type="invisible"
        )
        creature.is_visible = False
        creature.invisible_timer = stats.get('invisible_time', 60)
        return creature

    @staticmethod
    def create_flyer(x: float, y: float) -> Creature:
        stats = CREATURES_STATS['flyer']
        creature = Creature(
            hp=stats['hp'],
            maxHP=stats['hp'],
            speed=stats['speed'],
            cost=stats['cost'],
            reward=stats['reward'],
            damage_to_base=stats['damage_to_base'],
            position=Point(x, y),
            creature_type="flyer",
            movement_type="flying"
        )
        return creature

    @staticmethod
    def create_tunneler(x: float, y: float) -> Creature:
        stats = CREATURES_STATS['tunneler']
        creature = Creature(
            hp=stats['hp'],
            maxHP=stats['hp'],
            speed=stats['speed'],
            cost=stats['cost'],
            reward=stats['reward'],
            damage_to_base=stats['damage_to_base'],
            position=Point(x, y),
            creature_type="tunneler",
            movement_type="tunnel",
            underground=True
        )
        creature.is_visible = False
        return creature

    @staticmethod
    def create_destroyer(x: float, y: float) -> Creature:
        stats = CREATURES_STATS['destroyer']
        creature = Creature(
            hp=stats['hp'],
            maxHP=stats['hp'],
            speed=stats['speed'],
            cost=stats['cost'],
            reward=stats['reward'],
            damage_to_base=stats['damage_to_base'],
            position=Point(x, y),
            creature_type="destroyer",
            tower_damage=stats.get('tower_damage', 30)
        )
        creature.armor = 0.3
        return creature

