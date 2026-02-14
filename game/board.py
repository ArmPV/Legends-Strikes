from typing import List, Optional # Importation de List et Optional pour les annotations de type
from game.players import Attacker, Defender 
from game.path import Path
from game.creatures import Creature
from game.towers import Tower


class Cell:
    def __init__(self, type: str, x: float, y: float):
        self.type = type
        self.x = x
        self.y = y
        self.occupied = False
        self.tower: Optional[Tower] = None # Référence à la tour placée sur cette cellule, si elle existe


class GameBoard:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.cells: List[Cell] = []
        self.path: Optional[Path] = None
        self.attacker: Optional[Attacker] = None
        self.defender: Optional[Defender] = None

    def add_cell(self, cell: Cell):
        self.cells.append(cell)

    def set_path(self, path: Path):
        self.path = path

    def set_players(self, attacker: Attacker, defender: Defender):
        self.attacker = attacker
        self.defender = defender
