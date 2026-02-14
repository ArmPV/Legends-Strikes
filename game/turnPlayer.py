from game.board import GameBoard
from game.wave import Wave


class TurnPlayer:
    def __init__(self, board: GameBoard):
        self.board = board

    def startAttackerPhase(self):
        pass

    def startDefenserPhase(self):
        pass

    def resolveWave(self, wave: Wave):
        pass
