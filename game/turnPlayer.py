from game.board import GameBoard
from game.wave import Wave
from game.utils import Point
from game.creatures import CreatureFactory
from game.constants import (
    WAVE_SPAWN_DELAY,
    DEFENDER_KILL_ZONE_MULTIPLIERS,
    ATTACKER_LATE_REWARD_RATIO,
    SUMMONED_REWARD_RATIO,
    SUMMONED_DAMAGE_RATIO,
)
import math
import pygame


class TurnPlayer:
    def __init__(self, board: GameBoard):
        self.board = board
        self.current_wave = None
        self.wave_active = False
        self.spawn_timer = 0
        self.spawn_index = 0
        self.pending_spawns = []
        self.sound_enabled = True
        self.scout_active = False
        self.damage_events = []

        self.impact_sound = pygame.mixer.Sound("assets/musics/impactMetal.ogg")
        self.eliminated_sound = pygame.mixer.Sound("assets/musics/eliminated.ogg")
        self.impact_sound.set_volume(0.5)
        self.eliminated_sound.set_volume(0.5)

    def set_sound_enabled(self, enabled: bool):
        self.sound_enabled = enabled
        volume = 0.5 if enabled else 0.0
        self.impact_sound.set_volume(volume)
        self.eliminated_sound.set_volume(volume)

    def _get_progress_index(self, creature, path_points):
        if not path_points:
            return 0

        max_index = max(0, len(path_points) - 1)

        if creature.movement_type == "flying":
            start_point = path_points[0]
            end_point = path_points[-1]
            total_distance = math.hypot(end_point[0] - start_point[0], end_point[1] - start_point[1])
            if total_distance <= 0:
                return max_index

            traveled = math.hypot(creature.position.x - start_point[0], creature.position.y - start_point[1])
            progress_ratio = max(0.0, min(1.0, traveled / total_distance))
            return int(round(progress_ratio * max_index))

        return max(0, min(creature.__dict__.get('target_index', 1) - 1, max_index))

    def _get_progress_zone(self, progress_index):
        if progress_index < 5:
            return 1
        if progress_index < 9:
            return 2
        return 3

    def _get_attacker_base_reward(self, creature):
        return max(10, creature.cost // 3)

    def _get_defender_kill_reward(self, creature, zone):
        amount = int(round(creature.reward * DEFENDER_KILL_ZONE_MULTIPLIERS.get(zone, 0.20)))
        return max(1, amount) if creature.reward > 0 else 0

    def _get_attacker_progress_reward(self, creature, zone):
        if zone != 3:
            return 0
        return max(1, int(round(self._get_attacker_base_reward(creature) * ATTACKER_LATE_REWARD_RATIO)))

    def startAttackerPhase(self):
        self.wave_active = False
        self.scout_active = False

    def startDefenserPhase(self):
        self.wave_active = False

    def resolveWave(self, wave: Wave):
        self.current_wave = wave
        self.wave_active = True
        self.spawn_timer = 0
        self.spawn_index = 0
        self.pending_spawns = []
        self.damage_events = []

        if "scout" in wave.active_bonuses:
            self.scout_active = True

        start_point = self.board.get_path_points()[0]

        for i, creature in enumerate(wave.creatures):
            creature.position = Point(start_point[0], start_point[1] - i * 10)
            creature.__dict__['target_index'] = 1

            if "regen" in wave.active_bonuses:
                creature.regen_rate = 2
            if "armor" in wave.active_bonuses:
                creature.armor = min(0.8, creature.armor + 0.3)
            if "immunity" in wave.active_bonuses:
                creature.slow_immune = True

            for bonus in wave.bonuses:
                creature.apply_effect(bonus)

            self.pending_spawns.append(creature)

    def calculate_auras(self):
        if not self.board.defender:
            return

        for tower in self.board.defender.towers:
            tower.bonus_damage = 0

        for tower in self.board.defender.towers:
            if tower.aura_type == "damage_boost":
                for other in self.board.defender.towers:
                    if other is not tower and other.damage > 0:
                        dist = math.hypot(tower.position.x - other.position.x,
                                          tower.position.y - other.position.y)
                        if dist <= tower.aura_range:
                            other.bonus_damage += tower.aura_value

            elif tower.aura_type == "detection":
                for creature in self.board.creatures:
                    if creature.alive and not creature.underground:
                        dist = math.hypot(tower.position.x - creature.position.x,
                                          tower.position.y - creature.position.y)
                        if dist <= tower.aura_range:
                            creature.is_visible = True

    def update_wave(self):
        if not self.wave_active or not self.current_wave:
            return False

        if self.spawn_index < len(self.pending_spawns):
            self.spawn_timer += 1
            if self.spawn_timer >= WAVE_SPAWN_DELAY:
                self.spawn_timer = 0
                creature_to_spawn = self.pending_spawns[self.spawn_index]
                self.board.creatures.append(creature_to_spawn)
                self.spawn_index += 1

        path_points = self.board.get_path_points()
        end_point = path_points[-1]

        self.calculate_auras()

        for creature in self.board.creatures[:]:
            if not creature.alive:
                if self.sound_enabled:
                    self.eliminated_sound.play()

                progress_index = self._get_progress_index(creature, path_points)
                zone = self._get_progress_zone(progress_index)
                defender_reward = self._get_defender_kill_reward(creature, zone)
                attacker_reward = self._get_attacker_progress_reward(creature, zone)

                if self.board.defender:
                    self.board.defender.gold += defender_reward

                if self.board.attacker and attacker_reward > 0:
                    self.board.attacker.gold += attacker_reward

                self.damage_events.append({
                    'x': creature.position.x,
                    'y': creature.position.y,
                    'text': f"+{defender_reward}g DEF",
                    'color': (245, 209, 88),
                    'life': 40
                })

                if attacker_reward > 0:
                    self.damage_events.append({
                        'x': creature.position.x,
                        'y': creature.position.y - 22,
                        'text': f"+{attacker_reward}g ATK",
                        'color': (235, 120, 90),
                        'life': 40
                    })

                if creature.creature_type == "summoner":
                    factory = CreatureFactory()
                    for _ in range(2):
                        summoned = factory.create_normal(creature.position.x, creature.position.y)
                        summoned.__dict__['target_index'] = creature.__dict__.get('target_index', 1)
                        summoned.reward = max(4, int(round(summoned.reward * SUMMONED_REWARD_RATIO)))
                        summoned.damage_to_base = max(6, int(round(summoned.damage_to_base * SUMMONED_DAMAGE_RATIO)))
                        self.board.creatures.append(summoned)

                self.board.creatures.remove(creature)
                continue

            current_speed = creature.update()

            if creature.movement_type == "flying":
                dx = end_point[0] - creature.position.x
                dy = end_point[1] - creature.position.y
                distance = math.hypot(dx, dy)
                if distance > current_speed:
                    creature.position.x += (dx / distance) * current_speed
                    creature.position.y += (dy / distance) * current_speed
                else:
                    creature.position.x = end_point[0]
                    creature.position.y = end_point[1]

            elif creature.movement_type == "tunnel":
                target_index = creature.__dict__.get('target_index', 1)

                if creature.underground and target_index >= len(path_points) // 2:
                    creature.underground = False
                    creature.is_visible = True

                if target_index < len(path_points):
                    target = path_points[target_index]
                    dx = target[0] - creature.position.x
                    dy = target[1] - creature.position.y
                    distance = math.hypot(dx, dy)
                    if distance < current_speed:
                        creature.position.x = target[0]
                        creature.position.y = target[1]
                        creature.__dict__['target_index'] = target_index + 1
                    elif distance > 0:
                        creature.position.x += (dx / distance) * current_speed
                        creature.position.y += (dy / distance) * current_speed

            else:
                target_index = creature.__dict__.get('target_index', 1)
                if target_index < len(path_points):
                    target = path_points[target_index]
                    dx = target[0] - creature.position.x
                    dy = target[1] - creature.position.y
                    distance = math.hypot(dx, dy)
                    if distance < current_speed:
                        creature.position.x = target[0]
                        creature.position.y = target[1]
                        creature.__dict__['target_index'] = target_index + 1
                    elif distance > 0:
                        creature.position.x += (dx / distance) * current_speed
                        creature.position.y += (dy / distance) * current_speed

            if creature.tower_damage > 0 and creature.alive and self.board.defender:
                for tower in self.board.defender.towers[:]:
                    dist = math.hypot(creature.position.x - tower.position.x,
                                      creature.position.y - tower.position.y)
                    if dist < 50:
                        tower.hp -= creature.tower_damage
                        self.damage_events.append({
                            'x': tower.position.x,
                            'y': tower.position.y,
                            'text': f"-{creature.tower_damage}",
                            'color': (255, 80, 80),
                            'life': 30
                        })
                        if tower.hp <= 0:
                            # Destroy tower
                            grid_x = int((tower.position.x) // self.board.cell_size)
                            grid_y = int((tower.position.y) // self.board.cell_size)
                            if 0 <= grid_y < self.board.height and 0 <= grid_x < self.board.width:
                                cell = self.board.cells[grid_y][grid_x]
                                cell.tower = None
                                cell.occupied = False
                            self.board.defender.towers.remove(tower)

            if creature.reached_end(Point(end_point[0], end_point[1])):
                if self.sound_enabled:
                    self.impact_sound.play()

                if self.board.defender:
                    self.board.defender.baseHP -= creature.damage_to_base

                if self.board.attacker:
                    self.board.attacker.gold += self._get_attacker_base_reward(creature)

                self.board.creatures.remove(creature)

        if len(self.board.creatures) == 0 and self.spawn_index >= len(self.pending_spawns):
            self.wave_active = False
            return True

        return False
