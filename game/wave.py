from typing import List
from game.creatures import Creature
from game.effects import Effect


class Wave:
    def __init__(self, delay=20):
        self.creatures: List[Creature] = []
        self.bonuses: List[Effect] = []

        self.active: List[Creature] = []
        self.delay = delay
        self.timer = 0
        self.finished = False

    def add_creature(self, creature: Creature):
        self.creatures.append(creature)

    def set_path(self, path):
        for c in self.creatures:
            c.set_path(path)

    def update(self):
        if self.finished:
            return

        # Envoi progressif
        if self.timer <= 0 and self.creatures:
            c = self.creatures.pop(0)
            self.active.append(c)
            self.timer = self.delay
        else:
            self.timer -= 1

        # Mise à jour des créatures actives
        for c in self.active:
            c.update()

        # Nettoyage
        self.active = [c for c in self.active if c.alive]

        # Fin de vague
        if not self.creatures and not self.active:
            self.finished = True
