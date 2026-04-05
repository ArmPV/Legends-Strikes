from dataclasses import dataclass
from typing import List
from game.wave import Wave
from game.towers import Tower
from game.board import Cell

@dataclass
class Player:
    id_player: int
    name: str
    role: str
    gold: int
    baseHP: int

class Attacker(Player):
    def __init__(self, id_player, name, gold, baseHP):
        super().__init__(id_player, name, "Attacker", gold, baseHP)
        self.waves: List[Wave] = []

    def composeVague(self) -> Wave:
        wave = Wave()
        self.waves.append(wave)
        return wave

    def launchWave(self, wave: Wave):
        pass

class Defender(Player):
    def __init__(self, id_player, name, gold, baseHP):
        super().__init__(id_player, name, "Defender", gold, baseHP)
        self.towers: List[Tower] = []

    def placeTower(self, tower: Tower, cell: Cell):
        if not cell.occupied:
            cell.tower = tower
            cell.occupied = True
            self.towers.append(tower)

    def upgradeTower(self, tower: Tower):
        if tower.level < 3:
            tower.level += 1
            tower.upgrade()