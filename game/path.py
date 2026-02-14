from typing import Optional, List


class Waypoint:
    def __init__(self, x: float, y: float, index: int):
        self.x = x
        self.y = y
        self.index = index
        self.next_waypoint: Optional["Waypoint"] = None # Référence au prochain waypoint dans le chemin

    def getNext(self):
        return self.next_waypoint # Retourne le prochain waypoint dans le chemin


class Path:
    def __init__(self):
        self.waypoints: List[Waypoint] = [] # Liste des waypoints qui composent le chemin

    def add_waypoint(self, waypoint: Waypoint):
        self.waypoints.append(waypoint) # Ajouter le waypoint à la liste des waypoints du chemin
