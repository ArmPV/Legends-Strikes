import pygame

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60
CELL_SIZE = 44

BOARD_WIDTH = 18
BOARD_HEIGHT = 14

COLORS = {
    'BACKGROUND': (10, 10, 20),
    'BACKGROUND_GRADIENT_END': (30, 30, 50),
    'UI_BG': (20, 20, 35, 220),
    'UI_TEXT': (240, 240, 255),
    'UI_GOLD': (255, 215, 0),
    'UI_GOLD_DARK': (180, 150, 0),
    'UI_HP': (255, 80, 80),
    'UI_HP_DARK': (180, 40, 40),
    'BUTTON': (45, 45, 65),
    'BUTTON_HOVER': (70, 70, 95),
    'BUTTON_SELECTED': (100, 100, 150),
    'BUTTON_GLOW': (255, 215, 0),
    'PATH': (35, 35, 55),
    'PATH_GLOW': (55, 55, 85),
    'GRASS': (25, 35, 30),
    'TOWER_PLACEMENT': (50, 50, 70),
    'TOWER_RANGE': (100, 150, 255, 60),
    'ATTACKER_BASE': (220, 60, 60),
    'DEFENDER_BASE': (60, 150, 220),
    'HP_BAR_BG': (60, 30, 30),
    'HP_BAR_FG': (80, 220, 80),
    'HP_BAR_FG_MID': (255, 200, 80),
    'HP_BAR_FG_LOW': (255, 80, 80),
    'CREATURE_NORMAL': (240, 140, 100),
    'CREATURE_FAST': (100, 240, 100),
    'CREATURE_TANK': (100, 100, 240),
    'CREATURE_SUMMONER': (200, 100, 240),
    'CREATURE_INVISIBLE': (180, 180, 200),
    'CREATURE_GLOW': (255, 255, 200),
    'TOWER_BASIC': (100, 150, 220),
    'TOWER_SNIPER': (80, 200, 100),
    'TOWER_SLOW': (200, 100, 200),
    'TOWER_AOE': (240, 180, 80),
    'TOWER_DETECTOR': (100, 200, 200),
    'EFFECT_SLOW': (100, 200, 255),
    'EFFECT_INVISIBLE': (180, 180, 220),
    'EFFECT_PARTICLE': (255, 220, 100),
    'EFFECT_EXPLOSION': (255, 100, 50),
}

CREATURES_STATS = {
    'normal': {
        'hp': 100,
        'speed': 2.0,
        'cost': 50,
        'reward': 35,
        'damage_to_base': 20,
        'name': 'Créature Normale',
        'icon': '🐉'
    },
    'fast': {
        'hp': 50,
        'speed': 4.0,
        'cost': 60,
        'reward': 40,
        'damage_to_base': 15,
        'name': 'Créature Rapide',
        'icon': '⚡'
    },
    'tank': {
        'hp': 300,
        'speed': 1.0,
        'cost': 100,
        'reward': 65,
        'damage_to_base': 40,
        'name': 'Créature Tank',
        'icon': '🛡️'
    },
    'summoner': {
        'hp': 80,
        'speed': 1.5,
        'cost': 90,
        'reward': 55,
        'damage_to_base': 20,
        'name': 'Invocateur',
        'icon': '🪄'
    },
    'invisible': {
        'hp': 60,
        'speed': 2.5,
        'cost': 80,
        'reward': 50,
        'damage_to_base': 25,
        'name': 'Créature Invisible',
        'icon': '👻',
        'invisible_time': 60
    },
    'flyer': {
        'hp': 70,
        'speed': 1.8,
        'cost': 120,
        'reward': 60,
        'damage_to_base': 30,
        'name': 'Créature Volante',
        'icon': '🦅',
        'movement': 'flying'
    },
    'tunneler': {
        'hp': 90,
        'speed': 1.5,
        'cost': 110,
        'reward': 55,
        'damage_to_base': 25,
        'name': 'Tunnelier',
        'icon': '🕳️',
        'movement': 'tunnel'
    },
    'destroyer': {
        'hp': 150,
        'speed': 1.2,
        'cost': 140,
        'reward': 70,
        'damage_to_base': 35,
        'name': 'Destructeur',
        'icon': '💀',
        'tower_damage': 30
    }
}

TOWERS_STATS = {
    'basic': {
        'damage': 25,
        'range': 120,
        'attack_speed': 30,
        'cost': 100,
        'upgrade_cost': 80,
        'name': 'Tour Basique',
        'description': 'Tour équilibrée aux dégâts moyens',
        'color': (100, 150, 220),
        'icon': '🏰'
    },
    'sniper': {
        'damage': 60,
        'range': 200,
        'attack_speed': 60,
        'cost': 150,
        'upgrade_cost': 120,
        'name': 'Tour Sniper',
        'description': 'Longue portée, dégâts élevés',
        'color': (80, 200, 100),
        'icon': '🎯'
    },
    'slow': {
        'damage': 10,
        'range': 100,
        'attack_speed': 40,
        'cost': 120,
        'upgrade_cost': 100,
        'name': 'Tour Ralentissante',
        'description': 'Ralentit les ennemis',
        'color': (200, 100, 200),
        'icon': '❄️'
    },
    'aoe': {
        'damage': 15,
        'range': 90,
        'attack_speed': 50,
        'cost': 130,
        'upgrade_cost': 110,
        'name': 'Tour AoE',
        'description': 'Dégâts de zone',
        'color': (240, 180, 80),
        'icon': '💥'
    },
    'detector': {
        'damage': 20,
        'range': 150,
        'attack_speed': 35,
        'cost': 140,
        'upgrade_cost': 100,
        'name': 'Tour Détecteur',
        'description': 'Détecte les créatures invisibles',
        'color': (100, 200, 200),
        'icon': '👁️'
    },
    'buffer': {
        'damage': 0,
        'range': 100,
        'attack_speed': 0,
        'cost': 160,
        'upgrade_cost': 130,
        'name': 'Tour Ampli',
        'description': '+25% dégâts aux tours proches',
        'color': (220, 180, 60),
        'icon': '⚔️',
        'aura_type': 'damage_boost',
        'aura_value': 0.25,
        'aura_range': 120,
        'hp': 150
    },
    'radar': {
        'damage': 15,
        'range': 200,
        'attack_speed': 45,
        'cost': 170,
        'upgrade_cost': 140,
        'name': 'Tour Radar',
        'description': 'Large détection des invisibles',
        'color': (60, 200, 180),
        'icon': '📡',
        'aura_type': 'detection',
        'aura_range': 200,
        'hp': 160
    }
}

TOWER_HP = {
    'basic': 200,
    'sniper': 150,
    'slow': 180,
    'aoe': 170,
    'detector': 160,
    'buffer': 150,
    'radar': 160
}

WAVE_BONUSES = {
    'regen': {
        'name': 'Régénération',
        'description': '+2 PV/tick',
        'cost': 80,
        'icon': '💚'
    },
    'armor': {
        'name': 'Armure',
        'description': '+30% armure',
        'cost': 70,
        'icon': '🛡️'
    },
    'immunity': {
        'name': 'Anti-Slow',
        'description': 'Immunité ralentissement',
        'cost': 50,
        'icon': '⚡'
    },
    'scout': {
        'name': 'Reconnaissance',
        'description': 'Révèle les tours',
        'cost': 60,
        'icon': '🔍'
    }
}

STARTING_GOLD = {
    'attacker': 600,
    'defender': 350
}

STARTING_BASE_HP = 250

WAVE_SPAWN_DELAY = 24
WAVE_MIN_COST = 130
SLOW_FACTOR = 0.5
MAX_TOWER_LEVEL = 3
TOWER_SELL_REFUND_RATIO = 1
DEFENDER_KILL_ZONE_MULTIPLIERS = {
    1: 0.65,
    2: 0.40,
    3: 0.20,
}
ATTACKER_LATE_REWARD_RATIO = 0.5
SUMMONED_REWARD_RATIO = 0.4
SUMMONED_DAMAGE_RATIO = 0.6

EFFECT_DURATION = {
    'slow': 60,
    'invisible': 60
}

UI_PANEL_WIDTH = 320
BUTTON_WIDTH = 220
BUTTON_HEIGHT = 44
