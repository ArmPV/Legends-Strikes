from dataclasses import dataclass

@dataclass
class Effect:
    type: str
    intensity: float
    isActive: bool
    source: str
