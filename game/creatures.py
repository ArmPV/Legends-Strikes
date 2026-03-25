from dataclasses import dataclass
from typing import Optional, List
from game.utils import Point
from game.effects import Effect
from game.path import Waypoint


@dataclass
class Creature:
    hp: int
    speed: float
    cost: int
    position: Point
    maxHP: int
    effect: Optional[Effect] = None  # 0..1 effect
    color: tuple = (0, 255, 0)  # <--- COULEUR PAR DÉFAUT

    path = None
    current_wp = None
    alive: bool = True

    def set_path(self, path):
        """Assigne un chemin à la créature."""
        self.path = path.waypoints
        if not self.path:
            self.alive = False
            return
        self.current_wp = self.path[0]
        self.position = Point(self.current_wp.x, self.current_wp.y)

    def apply_effect(self, effect: Effect):
        self.effect = effect

    def update(self):
        """Avance de waypoint en waypoint."""
        if not self.alive or not self.current_wp:
            return

        nxt = self.current_wp.getNext()
        if nxt is None:
            # Arrivé au bout du chemin
            self.alive = False
            return

        self.current_wp = nxt
        self.position = Point(nxt.x, nxt.y)

        if self.effect:
            self.effect.apply(self)
