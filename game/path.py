from typing import Optional, List
from game.utils import Point


class Waypoint:
    def __init__(self, x: float, y: float, index: int):
        self.x = x
        self.y = y
        self.index = index
        self.next_waypoint: Optional["Waypoint"] = None

    def getNext(self):
        return self.next_waypoint


class Path:
    def __init__(self):
        self.waypoints: List[Waypoint] = []

    def add_waypoint(self, waypoint: Waypoint):
        self.waypoints.append(waypoint)

    def link_waypoints(self):
        for i in range(len(self.waypoints) - 1):
            self.waypoints[i].next_waypoint = self.waypoints[i + 1]

    @staticmethod
    def chemin_simple():
        path = Path()
        # Chemin horizontal au milieu (y = 7)
        for i in range(20):
            wp = Waypoint(x=i, y=7, index=i)
            path.add_waypoint(wp)
        path.link_waypoints()
        return path
