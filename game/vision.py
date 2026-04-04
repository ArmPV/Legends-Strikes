from typing import List
from game.towers import Tower
from game.creatures import Creature
from game.turnPlayer import TurnPlayer
import math


class VisionSystem:
    def __init__(self, turn_player: TurnPlayer):
        self.turn_player = turn_player

    def getVisibleTowersForAttacker(self) -> List[Tower]:
        if self.turn_player.board.defender:
            if self.turn_player.scout_active:
                return self.turn_player.board.defender.towers

            visible_towers = []
            for tower in self.turn_player.board.defender.towers:
                fake_tower = Tower(
                    damage=0,
                    range=0,
                    level=0,
                    cost=0,
                    position=tower.position,
                    tower_type="unknown"
                )
                visible_towers.append(fake_tower)
            return visible_towers
        return []

    def getVisibleCreaturesForDefender(self) -> List[Creature]:
        if self.turn_player.board:
            visible_creatures = []
            for creature in self.turn_player.board.creatures:
                if creature.alive and creature.is_visible:
                    visible_creatures.append(creature)
            return visible_creatures
        return []

    def isCreatureVisibleToDefender(self, creature: Creature) -> bool:
        if not creature.alive:
            return False

        if self.turn_player.board.defender:
            for tower in self.turn_player.board.defender.towers:
                if tower.tower_type == "detector":
                    dist = math.hypot(tower.position.x - creature.position.x,
                                      tower.position.y - creature.position.y)
                    if dist <= tower.range:
                        return True

        return creature.is_visible or self.isDetected(creature)

    def isDetected(self, creature):
        for tower in self.turn_player.board.defender.towers:
            if tower.tower_type == "detector":
                dist = math.hypot(tower.position.x - creature.position.x,
                                  tower.position.y - creature.position.y)
                if dist <= tower.range:
                    return True
        return False