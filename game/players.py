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
        super().__init__(id_player, name, "Attacker", gold, baseHP) # Appel du constructeur de la classe parente
        self.waves: List[Wave] = []  # 1..n waves

    def composeVague(self) -> Wave:
        wave = Wave()
        self.waves.append(wave)
        return wave

    def launchWave(self, wave: Wave):
        pass


class Defender(Player):
    def __init__(self, id_player, name, gold, baseHP):
        super().__init__(id_player, name, "Defender", gold, baseHP) 
        self.towers: List[Tower] = []  # 1..n towers

    def placeTower(self, tower: Tower, cell: Cell):
        if not cell.occupied: # Vérifier que la cellule n'est pas déjà occupée
            cell.tower = tower
            cell.occupied = True
            self.towers.append(tower) # Ajouter la tour à la liste des tours du défenseur

    def upgradeTower(self, tower: Tower):
        tower.level += 1 # Amélioration simple : augmenter le niveau de la tour
