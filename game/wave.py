from typing import List
from game.creatures import Creature
from game.effects import Effect


class Wave:
    def __init__(self):
        self.creatures: List[Creature] = []
        self.bonuses: List[Effect] = []
