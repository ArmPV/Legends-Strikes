from typing import Optional, List


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
        if self.waypoints:
            self.waypoints[-1].next_waypoint = waypoint
        self.waypoints.append(waypoint)

    def get_start(self) -> Optional[Waypoint]:
        return self.waypoints[0] if self.waypoints else None