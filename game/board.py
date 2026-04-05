import pygame
import random
from game.constants import COLORS, CELL_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, UI_PANEL_WIDTH


class Cell:
    def __init__(self, type, x, y, width=CELL_SIZE, height=CELL_SIZE):
        self.type = type
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.occupied = False
        self.tower = None
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, screen, camera_x=0, camera_y=0, assets=None, offset_x=0, offset_y=0):
        screen_x = self.x - camera_x + offset_x
        screen_y = self.y - camera_y + offset_y

        if assets and assets.loaded:
            sprite = None
            if self.type in ("path", "start", "end"):
                sprite = assets.get_tile_sprite("path")
            else:
                sprite = assets.get_tile_sprite("grass")

            if sprite:
                screen.blit(sprite, (screen_x, screen_y))
                if self.type == "tower" and not self.occupied:
                    pygame.draw.rect(screen, (35, 50, 30), (screen_x, screen_y, self.width, self.height), 1)
                return

        if self.type in ("path", "start", "end"):
            color = COLORS['PATH']
        elif self.type == "tower":
            color = COLORS['TOWER_PLACEMENT']
        else:
            color = COLORS['GRASS']

        pygame.draw.rect(screen, color, (screen_x, screen_y, self.width, self.height))
        pygame.draw.rect(screen, (50, 60, 45), (screen_x, screen_y, self.width, self.height), 1)


class GameBoard:
    def __init__(self, width, height, cell_size=CELL_SIZE):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.cells = []
        self.attacker = None
        self.defender = None
        self.creatures = []
        self.path_cells = []
        self.assets = None
        self.init_board()

    def set_assets(self, assets):
        self.assets = assets

    def get_draw_offset(self):
        board_pixel_width = self.width * self.cell_size
        board_pixel_height = self.height * self.cell_size
        playable_width = SCREEN_WIDTH - UI_PANEL_WIDTH

        offset_x = max(0, (playable_width - board_pixel_width) // 2)
        offset_y = max(0, (SCREEN_HEIGHT - board_pixel_height) // 2)

        return offset_x, offset_y

    def init_board(self):
        self.cells = []
        for row in range(self.height):
            cell_row = []
            for col in range(self.width):
                x = col * self.cell_size
                y = row * self.cell_size

                cell_type = "tower"
                cell = Cell(cell_type, x, y, self.cell_size, self.cell_size)
                cell_row.append(cell)
            self.cells.append(cell_row)

        self.generate_path()

    def generate_path(self):
        self.path_cells = []
        start_col = self.width // 2
        current_col = start_col

        for row in range(self.height):
            if row % 3 == 0 and row > 0:
                current_col += random.choice([-1, 0, 1])
                current_col = max(1, min(self.width - 2, current_col))

            cell = self.cells[row][current_col]
            cell.type = "path"
            self.path_cells.append(cell)

        if self.path_cells:
            start_cell = self.path_cells[0]
            end_cell = self.path_cells[-1]
            start_cell.type = "start"
            end_cell.type = "end"

    def set_players(self, attacker, defender):
        self.attacker = attacker
        self.defender = defender

    def get_path_points(self):
        return [(cell.x + cell.width // 2, cell.y + cell.height // 2) for cell in self.path_cells]

    def draw(self, screen, camera_x=0, camera_y=0):
        offset_x, offset_y = self.get_draw_offset()

        for row in self.cells:
            for cell in row:
                cell.draw(screen, camera_x, camera_y, self.assets, offset_x, offset_y)

        if self.assets and self.assets.loaded and self.path_cells:
            start_cell = self.path_cells[0]
            end_cell = self.path_cells[-1]

            attacker_base = self.assets.get_base_sprite('attacker')
            defender_base = self.assets.get_base_sprite('defender')

            if attacker_base:
                start_center_x = start_cell.x - camera_x + offset_x + start_cell.width // 2
                start_center_y = start_cell.y - camera_y + offset_y + start_cell.height // 2
                attacker_rect = attacker_base.get_rect(center=(start_center_x, start_center_y))
                screen.blit(attacker_base, attacker_rect)

            if defender_base:
                end_center_x = end_cell.x - camera_x + offset_x + end_cell.width // 2
                end_center_y = end_cell.y - camera_y + offset_y + end_cell.height // 2
                defender_rect = defender_base.get_rect(center=(end_center_x, end_center_y))
                screen.blit(defender_base, defender_rect)