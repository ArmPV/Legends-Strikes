import pygame
import sys
import math
import random
import os
from game.board import GameBoard
from game.players import Attacker, Defender
from game.turnPlayer import TurnPlayer
from game.wave import Wave
from game.vision import VisionSystem
from game.ui import UI
from game.constants import *
from game.assets import AssetManager


class TowerDefenseGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        window_icon_path = os.path.join(os.path.dirname(__file__), "assets", "creatures", "creature_normal.png")
        try:
            window_icon = pygame.image.load(window_icon_path)
            pygame.display.set_icon(window_icon)
        except Exception as e:
            print(f"Impossible de charger l'icone de fenetre: {e}")

        self.jingle_sound = pygame.mixer.Sound("assets/musics/jingles.ogg")
        self.jingle_sound.set_volume(0.7)
        self.jingle_played = False

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Legends Strikes")

        self.menu_background = pygame.image.load("assets/ui/background_acceuil.png").convert()
        self.menu_background = pygame.transform.scale(
            self.menu_background, (SCREEN_WIDTH, SCREEN_HEIGHT)
        )

        # Icône son du menu
        self.sound_icon = pygame.image.load("assets/ui/sound.png").convert_alpha()
        self.sound_icon = pygame.transform.smoothscale(self.sound_icon, (28, 28))

        # Sons
        self.click_sound = pygame.mixer.Sound("assets/musics/click1.ogg")
        self.battle_mode_sound = pygame.mixer.Sound("assets/musics/battle_mode.ogg")

        self.click_sound.set_volume(0.35)
        self.battle_mode_sound.set_volume(0.8)

        self.current_music = None
        self.sound_enabled = True
        self.sound_button = pygame.Rect(SCREEN_WIDTH - 72, 18, 50, 50)

        self.clock = pygame.time.Clock()
        self.running = True

        self.assets = AssetManager()
        self.assets.load_all()

        self.particles = []
        self.flash_effect = 0
        self.screen_shake = 0
        self.animations = []

        self._bg_surface = None
        self._font_level = pygame.font.Font(None, 20)

        self.board = None
        self.attacker = None
        self.defender = None
        self.turn_player = None
        self.vision = None
        self.ui = None

        self.game_state = "main_menu"
        self.selected_tower_type = "basic"
        self.selected_defense_tower = None
        self.current_wave = Wave()
        self.winner = None
        self.phase_transition = 0

        self.camera_x = 0
        self.camera_y = 0
        self.dragging = False
        self.drag_start = (0, 0)

        self.background_offset = 0
        self.time = 0

        self.menu_buttons = {
            "start": pygame.Rect(SCREEN_WIDTH // 2 - 170, 300, 340, 70),
            "quit": pygame.Rect(SCREEN_WIDTH // 2 - 170, 390, 340, 70),
        }

        self.play_game_music()

    def set_sound_enabled(self, enabled: bool):
        self.sound_enabled = enabled

        music_volume = 1.0 if enabled else 0.0
        fx_volume = 1.0 if enabled else 0.0

        pygame.mixer.music.set_volume(music_volume)
        self.click_sound.set_volume(0.35 * fx_volume)
        self.battle_mode_sound.set_volume(0.8 * fx_volume)

        if self.turn_player is not None:
            self.turn_player.set_sound_enabled(enabled)

    def play_music(self, music_path, volume=1.0):
        if self.current_music != music_path:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play(-1)
            self.current_music = music_path

        pygame.mixer.music.set_volume(volume if self.sound_enabled else 0.0)

    def play_game_music(self):
        self.play_music("assets/musics/song_jeux.mpeg", 1.0)

    def play_battle_music(self):
        # volume augmenté pour la musique de bataille
        self.play_music("assets/musics/song_bataille.mpeg", 1.25)

    def start_new_game(self):
        self.particles = []
        self.flash_effect = 0
        self.screen_shake = 0
        self.animations = []
        self.jingle_played = False

        self.board = GameBoard(BOARD_WIDTH, BOARD_HEIGHT, CELL_SIZE)
        self.attacker = Attacker(1, "Attaquant", STARTING_GOLD['attacker'], 0)
        self.defender = Defender(2, "Défenseur", STARTING_GOLD['defender'], STARTING_BASE_HP)
        self.board.set_players(self.attacker, self.defender)
        self.board.set_assets(self.assets)

        self.turn_player = TurnPlayer(self.board)
        self.turn_player.set_sound_enabled(self.sound_enabled)

        self.vision = VisionSystem(self.turn_player)
        self.ui = UI(self)
        self.damage_texts = []

        self.selected_tower_type = "basic"
        self.selected_defense_tower = None
        self.current_wave = Wave()
        self.winner = None
        self.phase_transition = 0

        self.camera_x = 0
        self.camera_y = 0
        self.dragging = False
        self.drag_start = (0, 0)

        self.play_game_music()
        self.game_state = "attacker_phase"

    def create_particles(self, x, y, color, count=10, size_range=(2, 5)):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 4)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            self.particles.append({
                'x': x, 'y': y, 'vx': vx, 'vy': vy,
                'life': random.randint(20, 40),
                'color': color,
                'size': random.randint(size_range[0], size_range[1]),
                'initial_life': 40
            })

    def add_explosion(self, x, y):
        self.create_particles(x, y, (255, 100, 50), 20, (3, 8))
        self.screen_shake = 8
        self.flash_effect = 3
        self.animations.append({
            'type': 'explosion',
            'x': x, 'y': y,
            'frame': 0,
            'max_frames': 8
        })

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.sound_enabled:
                        self.click_sound.play()
                    self.handle_click(event.pos)
                elif event.button == 3:
                    self.handle_right_click(event.pos)
                elif event.button == 2 and self.game_state != "main_menu":
                    self.dragging = True
                    self.drag_start = event.pos

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 2:
                    self.dragging = False

            elif event.type == pygame.MOUSEMOTION:
                if self.dragging and self.game_state != "main_menu":
                    dx = event.pos[0] - self.drag_start[0]
                    dy = event.pos[1] - self.drag_start[1]
                    self.camera_x -= dx
                    self.camera_y -= dy
                    self.drag_start = event.pos

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_state == "game_over":
                        self.game_state = "main_menu"
                        self.play_game_music()
                    elif self.game_state != "main_menu":
                        self.game_state = "main_menu"
                        self.play_game_music()

    def handle_click(self, pos):
        mouse_x, mouse_y = pos

        if self.game_state == "main_menu":
            if self.sound_button.collidepoint(pos):
                self.set_sound_enabled(not self.sound_enabled)
                return

            if self.menu_buttons["start"].collidepoint(pos):
                self.start_new_game()
            elif self.menu_buttons["quit"].collidepoint(pos):
                self.running = False
            return

        if self.ui is None:
            return

        action = self.ui.handle_click(pos, self.game_state)

        if action == "add_creature":
            self.add_creature_to_wave(self.ui.selected_creature_type)
            self.create_particles(mouse_x, mouse_y, (255, 215, 0), 5, (2, 4))

        elif action == "launch_wave":
            self.launch_wave()

        elif action == "end_phase":
            self.end_phase()
            self.phase_transition = 10

        elif action == "select_tower":
            self.selected_tower_type = self.ui.selected_tower_type
            self.selected_defense_tower = None

        elif action == "place_tower":
            self.place_tower_at_mouse(mouse_x, mouse_y)

        elif action == "upgrade_tower":
            self.upgrade_selected_tower()

    def handle_right_click(self, pos):
        if self.game_state != "defender_phase" or self.board is None:
            return

        mouse_x, mouse_y = pos
        if mouse_x >= SCREEN_WIDTH - UI_PANEL_WIDTH:
            return

        offset_x, offset_y = self.board.get_draw_offset()
        grid_x = int((mouse_x - offset_x + self.camera_x) // self.board.cell_size)
        grid_y = int((mouse_y - offset_y + self.camera_y) // self.board.cell_size)

        if 0 <= grid_x < self.board.width and 0 <= grid_y < self.board.height:
            cell = self.board.cells[grid_y][grid_x]
            if cell.tower is not None:
                self.remove_tower(grid_x, grid_y)

    def add_creature_to_wave(self, creature_type):
        from game.creatures import CreatureFactory
        factory = CreatureFactory()
        start_point = self.board.get_path_points()[0]

        creatures = {
            "normal": factory.create_normal,
            "fast": factory.create_fast,
            "tank": factory.create_tank,
            "summoner": factory.create_summoner,
            "invisible": factory.create_invisible,
            "flyer": factory.create_flyer,
            "tunneler": factory.create_tunneler,
            "destroyer": factory.create_destroyer,
        }

        if creature_type in creatures:
            creature = creatures[creature_type](start_point[0], start_point[1])
            if self.attacker.gold >= creature.cost:
                self.attacker.gold -= creature.cost
                self.current_wave.creatures.append(creature)
                self.create_particles(start_point[0], start_point[1], (100, 200, 100), 3, (2, 3))

    def can_launch_current_wave(self):
        wave_cost = sum(creature.cost for creature in self.current_wave.creatures)
        
        if self.current_wave.get_creature_count() == 0:
            return False

        if wave_cost <= 0:
            return False

        if self.attacker.gold >= WAVE_MIN_COST:
            return wave_cost >= WAVE_MIN_COST

        return True

    def get_wave_requirement_text(self):
        wave_cost = sum(creature.cost for creature in self.current_wave.creatures)

        if wave_cost <= 0:
            return "Ajoute au moins une créature"
        if self.attacker.gold >= WAVE_MIN_COST and wave_cost < WAVE_MIN_COST:
            return f"La vague doit couter au moins {WAVE_MIN_COST} or"
        return ""

    def launch_wave(self):
        if not self.can_launch_current_wave():
            if self.current_wave.get_creature_count() == 0:
                self.turn_player.startAttackerPhase()
                self.game_state = "attacker_phase"
                self.ui.reset_bonuses()

        if len(self.current_wave.creatures) > 0:
            if self.sound_enabled:
                self.battle_mode_sound.play()

            self.play_battle_music()

            # Transfer active bonuses from UI to wave
            if self.ui:
                self.current_wave.active_bonuses = self.ui.get_active_bonuses()
                self.ui.reset_bonuses()

            self.turn_player.resolveWave(self.current_wave)
            self.game_state = "battle"
            self.current_wave = Wave()
            self.screen_shake = 5
            self.flash_effect = 5
            start_point = self.board.get_path_points()[0]
            self.create_particles(start_point[0], start_point[1], (255, 100, 100), 30, (3, 8))

    def place_tower_at_mouse(self, mouse_x, mouse_y):
        offset_x, offset_y = self.board.get_draw_offset()

        grid_x = int((mouse_x - offset_x + self.camera_x) // self.board.cell_size)
        grid_y = int((mouse_y - offset_y + self.camera_y) // self.board.cell_size)

        if 0 <= grid_x < self.board.width and 0 <= grid_y < self.board.height:
            cell = self.board.cells[grid_y][grid_x]

            if cell.tower is not None and self.game_state == "defender_phase":
                self.selected_defense_tower = cell.tower
                return

            if cell.type == "tower" and not cell.occupied:
                self.place_tower(grid_x, grid_y)

    def remove_tower(self, grid_x, grid_y):
        cell = self.board.cells[grid_y][grid_x]

        if cell.tower is None:
            return

        tower = cell.tower
        refund = int(round(tower.total_spent * TOWER_SELL_REFUND_RATIO))
        self.defender.gold += refund
        if self.selected_defense_tower is tower:
            self.selected_defense_tower = None

        if tower in self.defender.towers:
            self.defender.towers.remove(tower)

        cell.tower = None
        cell.occupied = False

        x = grid_x * self.board.cell_size + self.board.cell_size // 2
        y = grid_y * self.board.cell_size + self.board.cell_size // 2
        self.create_particles(x, y, (255, 180, 100), 12, (2, 4))

    def place_tower(self, grid_x, grid_y):
        from game.towers import TowerFactory
        factory = TowerFactory()
        x = grid_x * self.board.cell_size + self.board.cell_size // 2
        y = grid_y * self.board.cell_size + self.board.cell_size // 2

        towers = {
            "basic": factory.create_basic,
            "sniper": factory.create_sniper,
            "slow": factory.create_slow,
            "aoe": factory.create_aoe,
            "detector": factory.create_detector,
            "buffer": factory.create_buffer,
            "radar": factory.create_radar,
        }

        if self.selected_tower_type in towers:
            tower = towers[self.selected_tower_type](x, y)
            if self.defender.gold >= tower.cost:
                self.defender.gold -= tower.cost
                cell = self.board.cells[grid_y][grid_x]
                cell.occupied = True
                cell.tower = tower
                self.defender.towers.append(tower)
                self.selected_defense_tower = tower
                self.create_particles(x, y, tower.color, 15, (2, 5))
                self.screen_shake = 3
                self.animations.append({
                    'type': 'build',
                    'x': x, 'y': y,
                    'frame': 0,
                    'max_frames': 6
                })

    def end_phase(self):
        if self.game_state == "attacker_phase":
            self.game_state = "defender_phase"
            self.turn_player.startDefenserPhase()
        elif self.game_state == "defender_phase":
            self.selected_defense_tower = None
            if not self.turn_player.wave_active:
                self.game_state = "battle"
                self.launch_wave()

    def upgrade_selected_tower(self):
        tower = self.selected_defense_tower
        if self.game_state != "defender_phase" or tower is None:
            return
        if tower.level >= MAX_TOWER_LEVEL:
            return
        if self.defender.gold < tower.upgrade_cost:
            return

        self.defender.gold -= tower.upgrade_cost
        old_level = tower.level
        if tower.upgrade():
            self.create_particles(tower.position.x, tower.position.y, (255, 220, 120), 18, (2, 5))
            self.flash_effect = 2
            self.screen_shake = 2
        else:
            tower.level = old_level

    def update(self):
        self.time += 1
        self.background_offset += 0.5

        if self.game_state == "main_menu":
            return

        if (
            self.selected_defense_tower is not None
            and self.defender is not None
            and self.selected_defense_tower not in self.defender.towers
        ):
            self.selected_defense_tower = None

        if self.phase_transition > 0:
            self.phase_transition -= 1
        if self.screen_shake > 0:
            self.screen_shake -= 1
        if self.flash_effect > 0:
            self.flash_effect -= 1

        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.2
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.particles.remove(particle)

        for anim in self.animations[:]:
            anim['frame'] += 1
            if anim['frame'] >= anim['max_frames']:
                self.animations.remove(anim)

        if self.game_state == "battle":
            wave_finished = self.turn_player.update_wave()

            if wave_finished:
                self.flash_effect = 5
                self.play_game_music()

                if self.defender.baseHP <= 0:
                    self.game_state = "game_over"
                    self.winner = "Attaquant"

                    if self.sound_enabled and not self.jingle_played:
                        self.jingle_sound.play()
                        self.jingle_played = True

                elif self.attacker.gold < 50:
                    self.game_state = "game_over"
                    self.winner = "Défenseur"

                    if self.sound_enabled and not self.jingle_played:
                        self.jingle_sound.play()
                        self.jingle_played = True
                        
                else:
                    self.game_state = "attacker_phase"
                    self.turn_player.startAttackerPhase()

            for tower in self.defender.towers:
                target = tower.attack(self.board.creatures)
                if target:
                    self.create_particles(target.position.x, target.position.y, (255, 255, 100), 5, (2, 4))
                    self.animations.append({
                        'type': 'shot',
                        'x': tower.position.x,
                        'y': tower.position.y,
                        'tx': target.position.x,
                        'ty': target.position.y,
                        'frame': 0,
                        'max_frames': 5
                    })

    def draw_background(self):
        if self._bg_surface is None:
            self._bg_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            for y in range(SCREEN_HEIGHT):
                ratio = y / SCREEN_HEIGHT
                r = int(14 + ratio * 16)
                g = int(22 + ratio * 18)
                b = int(12 + ratio * 14)
                pygame.draw.line(self._bg_surface, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        self.screen.blit(self._bg_surface, (0, 0))

    def draw_main_menu(self):
        self.screen.blit(self.menu_background, (0, 0))

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 90))
        self.screen.blit(overlay, (0, 0))

        font_path = "assets/fonts/JetBrainsMono-Regular.ttf"

        title_font = pygame.font.Font(font_path, 76)
        title_font.set_bold(True)
        button_font = pygame.font.Font(font_path, 25)
        small_font = pygame.font.Font(font_path, 25)

        title_shadow = title_font.render("TOWER DEFENSE", True, (18, 26, 40))
        title = title_font.render("TOWER DEFENSE", True, (94, 132, 196))
        hint_shadow = small_font.render("Cliquez pour commencer une nouvelle partie", True, (40, 32, 24))
        hint = small_font.render("Cliquez pour commencer une nouvelle partie", True, (206, 186, 154))

        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 138))
        hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, 245))

        self.screen.blit(title_shadow, title_rect.move(3, 4))
        self.screen.blit(title, title_rect)
        self.screen.blit(hint_shadow, hint_rect.move(2, 2))
        self.screen.blit(hint, hint_rect)


        for key, rect in self.menu_buttons.items():
            hover = rect.collidepoint(pygame.mouse.get_pos())

            if key == "start":
                base_color = (60, 105, 170)
                text = "Commencer une partie"
            else:
                base_color = (150, 70, 70)
                text = "Quitter le jeu"

            color = tuple(min(255, c + 25) for c in base_color) if hover else base_color

            shadow_rect = rect.move(0, 5)
            pygame.draw.rect(self.screen, (20, 20, 30), shadow_rect, border_radius=16)
            pygame.draw.rect(self.screen, color, rect, border_radius=16)
            pygame.draw.rect(self.screen, (235, 235, 245), rect, 2, border_radius=16)

            txt = button_font.render(text, True, (255, 255, 255))
            self.screen.blit(txt, txt.get_rect(center=rect.center))

        # Bouton son
        hover_sound = self.sound_button.collidepoint(pygame.mouse.get_pos())
        button_color = (70, 85, 120) if hover_sound else (45, 55, 85)

        pygame.draw.rect(self.screen, button_color, self.sound_button, border_radius=12)
        pygame.draw.rect(self.screen, (235, 235, 245), self.sound_button, 2, border_radius=12)

        icon_rect = self.sound_icon.get_rect(center=self.sound_button.center)
        self.screen.blit(self.sound_icon, icon_rect)

        if not self.sound_enabled:
            pygame.draw.line(
                self.screen,
                (255, 70, 70),
                (self.sound_button.left + 10, self.sound_button.top + 10),
                (self.sound_button.right - 10, self.sound_button.bottom - 10),
                4
            )

    def draw_animations(self, shake_x, shake_y):
        offset_x, offset_y = self.board.get_draw_offset()
        for anim in self.animations:
            if anim['type'] == 'explosion':
                frame = anim['frame']
                size = 28 - frame * 3
                if size > 0:
                    alpha = min(255, 255 - frame * 30)
                    cx = anim['x'] - self.camera_x + shake_x
                    cy = anim['y'] - self.camera_y + shake_y
                    surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(surf, (255, 140, 50, alpha), (size, size), size)
                    pygame.draw.circle(surf, (255, 220, 100, alpha // 2), (size, size), size * 2 // 3)
                    self.screen.blit(surf, (cx - size, cy - size))

            elif anim['type'] == 'shot':
                progress = anim['frame'] / anim['max_frames']
                sx = anim['x'] + offset_x - self.camera_x + shake_x
                sy = anim['y'] + offset_y - self.camera_y + shake_y
                tx = anim['tx'] + offset_x - self.camera_x + shake_x
                ty = anim['ty'] + offset_y - self.camera_y + shake_y
                cx = sx + (tx - sx) * progress
                cy = sy + (ty - sy) * progress
                prev = max(0, progress - 0.3)
                px = sx + (tx - sx) * prev
                py = sy + (ty - sy) * prev
                pygame.draw.line(self.screen, (255, 200, 80),
                                 (int(px), int(py)), (int(cx), int(cy)), 2)
                pygame.draw.circle(self.screen, (255, 255, 200), (int(cx), int(cy)), 4)
                glow = pygame.Surface((16, 16), pygame.SRCALPHA)
                pygame.draw.circle(glow, (255, 255, 150, 80), (8, 8), 8)
                self.screen.blit(glow, (int(cx) - 8, int(cy) - 8))

            elif anim['type'] == 'build':
                frame = anim['frame']
                size = 20 - frame * 2
                if size > 0:
                    alpha = min(255, 140 - frame * 20)
                    cx = anim['x'] - self.camera_x + shake_x
                    cy = anim['y'] - self.camera_y + shake_y
                    surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(surf, (100, 200, 255, max(0, alpha)), (size, size), size)
                    pygame.draw.circle(surf, (180, 230, 255, max(0, alpha // 2)), (size, size), size, 2)
                    self.screen.blit(surf, (cx - size, cy - size))

    def draw(self):
        if self.game_state == "main_menu":
            self.draw_main_menu()
            pygame.display.flip()
            return

        self.draw_background()

        shake_x = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        shake_y = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0

        self.board.draw(self.screen, self.camera_x + shake_x, self.camera_y + shake_y)

        offset_x, offset_y = self.board.get_draw_offset()

        # Draw all creatures (including underground with special rendering)
        visible_creatures = self.vision.getVisibleCreaturesForDefender()
        for creature in self.board.creatures if self.board else []:
            if creature.alive:
                screen_x = creature.position.x - self.camera_x + shake_x + offset_x
                screen_y = creature.position.y - self.camera_y + shake_y + offset_y

                if getattr(creature, 'underground', False):
                    # Underground tunneler: dirt particles only
                    dirt = pygame.Surface((24, 24), pygame.SRCALPHA)
                    pygame.draw.circle(dirt, (100, 80, 50, 80), (12, 12), 10)
                    pygame.draw.circle(dirt, (130, 100, 60, 50), (12, 12), 12, 2)
                    self.screen.blit(dirt, (screen_x - 12, screen_y - 12))
                elif creature in visible_creatures:
                    self.draw_creature(screen_x, screen_y, creature)

        if self.game_state == "attacker_phase":
            towers_to_draw = self.vision.getVisibleTowersForAttacker()
        else:
            towers_to_draw = self.defender.towers

        for tower in towers_to_draw:
            screen_x = tower.position.x - self.camera_x + shake_x + offset_x
            screen_y = tower.position.y - self.camera_y + shake_y + offset_y
            self.draw_tower(screen_x, screen_y, tower)

        self.draw_animations(shake_x, shake_y)

        for particle in self.particles:
            alpha = int(255 * (particle['life'] / particle['initial_life']))
            color = particle['color']
            size = particle['size']
            surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*color, alpha), (size, size), size)
            self.screen.blit(surf, (particle['x'] - self.camera_x + shake_x - size,
                                    particle['y'] - self.camera_y + shake_y - size))

        if self.flash_effect > 0:
            flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            alpha = int(80 * (self.flash_effect / 5))
            flash_surface.fill((255, 255, 255))
            flash_surface.set_alpha(alpha)
            self.screen.blit(flash_surface, (0, 0))

        # Damage floaters
        if self.turn_player and hasattr(self.turn_player, 'damage_events'):
            font_dmg = self._font_level
            for evt in self.turn_player.damage_events[:]:
                evt['life'] -= 1
                if evt['life'] <= 0:
                    self.turn_player.damage_events.remove(evt)
                    continue
                alpha = int(255 * (evt['life'] / 40))
                ex = evt['x'] - self.camera_x + offset_x
                ey = evt['y'] - self.camera_y + offset_y - (40 - evt['life']) * 0.8
                txt = font_dmg.render(evt['text'], True, evt['color'])
                txt.set_alpha(alpha)
                self.screen.blit(txt, txt.get_rect(center=(ex, ey)))

        self.ui.draw(self.screen, self)

        if self.phase_transition > 0:
            transition_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            alpha = int(120 * (self.phase_transition / 10))
            transition_surface.fill((0, 0, 0))
            transition_surface.set_alpha(alpha)
            self.screen.blit(transition_surface, (0, 0))

        pygame.display.flip()

    def draw_creature(self, x, y, creature):
        sprite = self.assets.get_creature_sprite(creature.creature_type)

        # Flying creatures: dashed line to destination
        if creature.movement_type == "flying" and self.board:
            offset_x, offset_y = self.board.get_draw_offset()
            end = self.board.get_path_points()[-1]
            ex = end[0] - self.camera_x + offset_x
            ey = end[1] - self.camera_y + offset_y
            # Dashed line
            dx, dy = ex - x, ey - y
            dist = max(1, math.hypot(dx, dy))
            segments = int(dist / 12)
            for i in range(0, segments, 2):
                t1 = i / max(1, segments)
                t2 = min(1, (i + 1) / max(1, segments))
                pygame.draw.line(self.screen, (80, 200, 180, 100),
                                 (int(x + dx * t1), int(y + dy * t1)),
                                 (int(x + dx * t2), int(y + dy * t2)), 1)

        # Shadow (elevated for flyers)
        shadow_y_offset = 20 if creature.movement_type == "flying" else 14
        shadow = pygame.Surface((30, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 50), shadow.get_rect())
        self.screen.blit(shadow, (x - 15, y + shadow_y_offset))

        if sprite:
            sprite_to_draw = sprite.copy()

            if not creature.is_visible:
                sprite_to_draw.set_alpha(70)
            else:
                sprite_to_draw.set_alpha(255)

            if creature.slow_timer > 0:
                slow_surf = pygame.Surface((48, 48), pygame.SRCALPHA)
                pygame.draw.circle(slow_surf, (100, 180, 255, 60), (24, 24), 24)
                pygame.draw.circle(slow_surf, (140, 210, 255, 120), (24, 24), 24, 2)
                self.screen.blit(slow_surf, (x - 24, y - 24))

            # Destroyer glow when active
            if creature.tower_damage > 0 and self.game_state == "battle":
                pulse = abs(math.sin(self.time / 8)) * 0.5 + 0.5
                glow = pygame.Surface((48, 48), pygame.SRCALPHA)
                pygame.draw.circle(glow, (255, 60, 30, int(40 * pulse)), (24, 24), 24)
                self.screen.blit(glow, (x - 24, y - 24))

            # Regen visual
            if creature.regen_rate > 0 and creature.hp < creature.maxHP:
                heal_surf = pygame.Surface((8, 8), pygame.SRCALPHA)
                pygame.draw.line(heal_surf, (100, 255, 100, 180), (4, 0), (4, 8), 2)
                pygame.draw.line(heal_surf, (100, 255, 100, 180), (0, 4), (8, 4), 2)
                self.screen.blit(heal_surf, (x + 10, y - 18))

            self.screen.blit(sprite_to_draw, (x - 20, y - 20))
        else:
            color = self.get_creature_color(creature)
            pygame.draw.circle(self.screen, color, (int(x), int(y)), 14)

        self.draw_health_bar(x, y - 26, creature.hp / creature.maxHP)

    def draw_tower(self, x, y, tower):
        if tower.tower_type == "unknown":
            pygame.draw.rect(self.screen, (80, 120, 200), (x - 14, y - 14, 28, 28), border_radius=4)
            pygame.draw.rect(self.screen, (120, 160, 240), (x - 14, y - 14, 28, 28), 2, border_radius=4)
            txt = self._font_level.render("?", True, (200, 220, 255))
            self.screen.blit(txt, txt.get_rect(center=(x, y)))
            return

        sprite = self.assets.get_tower_sprite(tower.tower_type)

        # Range circle only during battle so tower coverage is readable in action.
        if self.game_state == "battle":
            diameter = int(tower.range * 2)
            if diameter > 0:
                range_surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
                pygame.draw.circle(
                    range_surface,
                    (*tower.color[:3], 38),
                    (diameter // 2, diameter // 2),
                    int(tower.range)
                )
                pygame.draw.circle(
                    range_surface,
                    (*tower.color[:3], 95),
                    (diameter // 2, diameter // 2),
                    int(tower.range),
                    3
                )
                self.screen.blit(range_surface, (x - tower.range, y - tower.range))
        elif self.game_state == "defender_phase" and tower is self.selected_defense_tower:
            diameter = int(tower.range * 2)
            if diameter > 0:
                range_surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
                pygame.draw.circle(
                    range_surface,
                    (*tower.color[:3], 26),
                    (diameter // 2, diameter // 2),
                    int(tower.range)
                )
                pygame.draw.circle(
                    range_surface,
                    (255, 230, 150, 140),
                    (diameter // 2, diameter // 2),
                    int(tower.range),
                    3
                )
                self.screen.blit(range_surface, (x - tower.range, y - tower.range))

                select_glow = pygame.Surface((66, 66), pygame.SRCALPHA)
                pygame.draw.circle(select_glow, (255, 220, 120, 70), (33, 33), 31, 4)
                self.screen.blit(select_glow, (x - 33, y - 33))

        if sprite:
            self.screen.blit(sprite, (x - 22, y - 22))
        else:
            pygame.draw.rect(self.screen, tower.color, (x - 18, y - 18, 36, 36), border_radius=4)

        # Aura visualization for buffer/radar towers
        if tower.aura_type and tower.aura_range > 0:
            aura_d = int(tower.aura_range * 2)
            aura_surf = pygame.Surface((aura_d, aura_d), pygame.SRCALPHA)
            pulse = abs(math.sin(self.time / 30)) * 0.4 + 0.6
            if tower.aura_type == "damage_boost":
                aura_color = (255, 200, 60, int(18 * pulse))
                border_color = (255, 210, 80, int(35 * pulse))
            else:
                aura_color = (60, 220, 200, int(18 * pulse))
                border_color = (80, 240, 220, int(35 * pulse))
            pygame.draw.circle(aura_surf, aura_color, (aura_d // 2, aura_d // 2), int(tower.aura_range))
            pygame.draw.circle(aura_surf, border_color, (aura_d // 2, aura_d // 2), int(tower.aura_range), 1)
            self.screen.blit(aura_surf, (x - tower.aura_range, y - tower.aura_range))

        # Level badge (top-right corner)
        if tower.level > 1:
            badge_x, badge_y = x + 14, y - 16
            pygame.draw.circle(self.screen, (30, 30, 50), (badge_x, badge_y), 9)
            pygame.draw.circle(self.screen, (255, 200, 50), (badge_x, badge_y), 8)
            level_text = self._font_level.render(str(tower.level), True, (40, 30, 10))
            self.screen.blit(level_text, level_text.get_rect(center=(badge_x, badge_y)))

        # Tower HP bar (only when damaged)
        if hasattr(tower, 'hp') and hasattr(tower, 'max_hp') and tower.hp < tower.max_hp:
            self.draw_health_bar(x, y + 20, tower.hp / tower.max_hp)

    def draw_health_bar(self, x, y, percent):
        percent = max(0, min(1, percent))

        bar_width = 34
        bar_height = 5
        bx = x - bar_width // 2

        pygame.draw.rect(self.screen, (0, 0, 0), (bx - 1, y - 1, bar_width + 2, bar_height + 2), border_radius=3)

        fill_width = int(bar_width * percent)
        if percent > 0.6:
            color = (70, 210, 70)
        elif percent > 0.3:
            color = (240, 190, 60)
        else:
            color = (240, 70, 70)

        if fill_width > 0:
            pygame.draw.rect(self.screen, color, (bx, y, fill_width, bar_height), border_radius=2)

    def get_creature_color(self, creature):
        colors = {
            "normal": (220, 140, 100),
            "fast": (100, 220, 100),
            "tank": (100, 100, 220),
            "summoner": (180, 100, 240),
            "invisible": (180, 180, 180),
            "flyer": (80, 210, 190),
            "tunneler": (140, 100, 60),
            "destroyer": (180, 50, 50),
        }
        return colors.get(creature.creature_type, (180, 100, 80))

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.mixer.music.stop()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = TowerDefenseGame()
    game.run()
