import os
import math
import pygame
from game.constants import CELL_SIZE


class AssetManager:
    def __init__(self):
        self.creatures = {}
        self.towers = {}
        self.tiles = {}
        self.bases = {}
        self.ui = {}
        self.loaded = False
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    def load_all(self):
        print("Chargement des assets...")

        creature_types = ['normal', 'fast', 'tank', 'summoner', 'invisible']
        for creature in creature_types:
            path = f"assets/creatures/creature_{creature}.png"
            self.creatures[creature] = self.load_image(path, (40, 40), fit=True)

        tower_types = ['basic', 'sniper', 'slow', 'aoe', 'detector']
        for tower in tower_types:
            path = f"assets/towers/tower_{tower}.png"
            self.towers[tower] = self.load_image(path, (44, 44), fit=True)

        tile_types = ['path', 'tower', 'grass']
        for tile in tile_types:
            path = f"assets/tiles/tile_{tile}.png"
            self.tiles[tile] = self.load_image(path, (CELL_SIZE, CELL_SIZE))

        self.bases['attacker'] = self.load_image("assets/bases/base_attacker.png", (64, 64), fit=True)
        self.bases['defender'] = self.load_image("assets/bases/base_defender.png", (64, 64), fit=True)

        ui_elements = ['panel_bg', 'button_normal', 'button_hover', 'button_selected',
                       'gold_icon', 'hp_icon', 'tower_icon', 'creature_icon']
        for ui in ui_elements:
            path = f"assets/ui/{ui}.png"
            target_size = None
            fit = False
            if ui in {'gold_icon', 'hp_icon', 'tower_icon', 'creature_icon'}:
                target_size = (24, 24)
                fit = True
            self.ui[ui] = self.load_image(path, target_size, fit=fit)

        self._generate_new_sprites()

        self.loaded = True
        print("Tous les assets charges !")

    def _generate_new_sprites(self):
        """Create programmatic sprites for new creatures and towers."""
        self.creatures['flyer'] = self._make_flyer_sprite(40)
        self.creatures['tunneler'] = self._make_tunneler_sprite(40)
        self.creatures['destroyer'] = self._make_destroyer_sprite(40)
        self.towers['buffer'] = self._make_buffer_sprite(44)
        self.towers['radar'] = self._make_radar_sprite(44)

    def _make_flyer_sprite(self, size):
        s = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2
        # Body
        pygame.draw.ellipse(s, (60, 180, 160), (cx - 6, cy - 4, 12, 8))
        # Wings
        pts_l = [(cx - 6, cy), (cx - 18, cy - 10), (cx - 12, cy + 2)]
        pts_r = [(cx + 6, cy), (cx + 18, cy - 10), (cx + 12, cy + 2)]
        pygame.draw.polygon(s, (80, 210, 190), pts_l)
        pygame.draw.polygon(s, (80, 210, 190), pts_r)
        pygame.draw.polygon(s, (40, 150, 130), pts_l, 2)
        pygame.draw.polygon(s, (40, 150, 130), pts_r, 2)
        # Head
        pygame.draw.circle(s, (100, 230, 210), (cx, cy - 6), 5)
        # Eyes
        pygame.draw.circle(s, (255, 255, 200), (cx - 2, cy - 7), 2)
        pygame.draw.circle(s, (255, 255, 200), (cx + 2, cy - 7), 2)
        # Tail
        pygame.draw.line(s, (50, 160, 140), (cx, cy + 4), (cx, cy + 14), 2)
        pygame.draw.line(s, (50, 160, 140), (cx, cy + 14), (cx - 4, cy + 18), 2)
        pygame.draw.line(s, (50, 160, 140), (cx, cy + 14), (cx + 4, cy + 18), 2)
        return s

    def _make_tunneler_sprite(self, size):
        s = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2
        # Body
        pygame.draw.ellipse(s, (140, 100, 60), (cx - 10, cy - 7, 20, 14))
        pygame.draw.ellipse(s, (110, 80, 45), (cx - 10, cy - 7, 20, 14), 2)
        # Drill head
        pts = [(cx + 10, cy), (cx + 18, cy - 4), (cx + 18, cy + 4)]
        pygame.draw.polygon(s, (180, 180, 180), pts)
        pygame.draw.polygon(s, (140, 140, 140), pts, 2)
        # Drill lines
        pygame.draw.line(s, (200, 200, 200), (cx + 12, cy - 2), (cx + 16, cy - 3), 1)
        pygame.draw.line(s, (200, 200, 200), (cx + 12, cy + 2), (cx + 16, cy + 3), 1)
        # Claws
        pygame.draw.line(s, (160, 120, 70), (cx - 6, cy + 7), (cx - 10, cy + 14), 3)
        pygame.draw.line(s, (160, 120, 70), (cx + 2, cy + 7), (cx + 2, cy + 14), 3)
        # Eyes
        pygame.draw.circle(s, (255, 200, 50), (cx - 3, cy - 3), 3)
        pygame.draw.circle(s, (0, 0, 0), (cx - 3, cy - 3), 1)
        # Dirt particles
        for angle in range(0, 360, 45):
            dx = int(math.cos(math.radians(angle)) * 16)
            dy = int(math.sin(math.radians(angle)) * 12)
            pygame.draw.circle(s, (120, 90, 50, 120), (cx + dx, cy + dy), 2)
        return s

    def _make_destroyer_sprite(self, size):
        s = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2
        # Armored body
        body_pts = [
            (cx, cy - 14), (cx + 12, cy - 4), (cx + 10, cy + 10),
            (cx, cy + 14), (cx - 10, cy + 10), (cx - 12, cy - 4)
        ]
        pygame.draw.polygon(s, (120, 40, 40), body_pts)
        pygame.draw.polygon(s, (180, 60, 60), body_pts, 2)
        # Inner armor plate
        inner_pts = [
            (cx, cy - 8), (cx + 6, cy - 2), (cx + 5, cy + 6),
            (cx, cy + 8), (cx - 5, cy + 6), (cx - 6, cy - 2)
        ]
        pygame.draw.polygon(s, (160, 50, 50), inner_pts)
        # Eyes (menacing)
        pygame.draw.circle(s, (255, 80, 30), (cx - 4, cy - 4), 3)
        pygame.draw.circle(s, (255, 80, 30), (cx + 4, cy - 4), 3)
        pygame.draw.circle(s, (255, 255, 100), (cx - 4, cy - 4), 1)
        pygame.draw.circle(s, (255, 255, 100), (cx + 4, cy - 4), 1)
        # Spikes
        for dx, dy in [(-14, -2), (14, -2), (-8, -14), (8, -14)]:
            pygame.draw.circle(s, (200, 70, 70), (cx + dx, cy + dy), 3)
            pygame.draw.circle(s, (140, 40, 40), (cx + dx, cy + dy), 3, 1)
        return s

    def _make_buffer_sprite(self, size):
        s = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2
        # Base platform
        pygame.draw.rect(s, (160, 130, 50), (cx - 14, cy + 4, 28, 12), border_radius=3)
        pygame.draw.rect(s, (200, 170, 70), (cx - 14, cy + 4, 28, 12), 2, border_radius=3)
        # Tower body
        pygame.draw.rect(s, (190, 160, 60), (cx - 8, cy - 10, 16, 16), border_radius=2)
        pygame.draw.rect(s, (220, 190, 80), (cx - 8, cy - 10, 16, 16), 2, border_radius=2)
        # Star on top
        star_y = cy - 14
        for i in range(5):
            angle = math.radians(i * 72 - 90)
            x = cx + int(math.cos(angle) * 7)
            y = star_y + int(math.sin(angle) * 7)
            pygame.draw.line(s, (255, 220, 80), (cx, star_y), (x, y), 2)
        pygame.draw.circle(s, (255, 230, 100), (cx, star_y), 4)
        # Aura rings
        pygame.draw.circle(s, (255, 220, 80, 60), (cx, cy), 18, 1)
        pygame.draw.circle(s, (255, 220, 80, 30), (cx, cy), 21, 1)
        return s

    def _make_radar_sprite(self, size):
        s = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2
        # Base
        pygame.draw.rect(s, (50, 120, 110), (cx - 10, cy + 6, 20, 10), border_radius=3)
        pygame.draw.rect(s, (70, 160, 150), (cx - 10, cy + 6, 20, 10), 2, border_radius=3)
        # Pole
        pygame.draw.line(s, (80, 180, 160), (cx, cy + 6), (cx, cy - 6), 3)
        # Dish
        pygame.draw.arc(s, (100, 220, 200), (cx - 14, cy - 18, 28, 20), 0.3, math.pi - 0.3, 3)
        pygame.draw.arc(s, (60, 180, 160), (cx - 10, cy - 14, 20, 14), 0.5, math.pi - 0.5, 2)
        # Signal waves
        for r in [8, 12, 16]:
            pygame.draw.arc(s, (100, 240, 220, 120), (cx - r, cy - 18 - r, r * 2, r * 2),
                            math.pi * 0.8, math.pi * 1.2, 1)
        # Center dot
        pygame.draw.circle(s, (150, 255, 240), (cx, cy - 10), 3)
        return s

    def _resolve_path(self, path):
        return path if os.path.isabs(path) else os.path.join(self.base_dir, path)

    def _trim_transparent_bounds(self, image):
        rect = image.get_bounding_rect()
        if rect.width == 0 or rect.height == 0:
            return image.copy()
        trimmed = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        trimmed.blit(image, (0, 0), rect)
        return trimmed

    def _fit_surface(self, image, size):
        target_w, target_h = size
        source_w, source_h = image.get_size()
        if source_w == 0 or source_h == 0:
            return pygame.Surface(size, pygame.SRCALPHA)

        scale = min(target_w / source_w, target_h / source_h)
        new_size = (max(1, int(source_w * scale)), max(1, int(source_h * scale)))
        scaled = pygame.transform.smoothscale(image, new_size)
        canvas = pygame.Surface(size, pygame.SRCALPHA)
        canvas.blit(scaled, ((target_w - new_size[0]) // 2, (target_h - new_size[1]) // 2))
        return canvas

    def load_image(self, path, size=None, fit=False):
        real_path = self._resolve_path(path)
        try:
            if os.path.exists(real_path):
                image = pygame.image.load(real_path).convert_alpha()
                if size:
                    if fit:
                        image = self._fit_surface(self._trim_transparent_bounds(image), size)
                    else:
                        image = pygame.transform.smoothscale(image, size)
                return image
            print(f"Image non trouvee: {real_path}")
            return None
        except Exception as e:
            print(f"Erreur chargement {real_path}: {e}")
            return None

    def get_creature_sprite(self, creature_type):
        return self.creatures.get(creature_type)

    def get_tower_sprite(self, tower_type):
        return self.towers.get(tower_type)

    def get_tile_sprite(self, tile_type):
        return self.tiles.get(tile_type)

    def get_base_sprite(self, base_type):
        return self.bases.get(base_type)

    def get_ui_sprite(self, ui_element):
        return self.ui.get(ui_element)
