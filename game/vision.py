from typing import List
from game.towers import Tower
from game.creatures import Creature
from game.turnPlayer import TurnPlayer


class VisionSystem:
    def __init__(self, turn_player: TurnPlayer):
        self.turn_player = turn_player

    def getVisibleTowersForAttacker(self) -> List[Tower]:
        return []

    def getVisibleCreaturesForDefender(self) -> List[Creature]:
        return []
