import math
import pygame
from game.constants import *


class UI:
    def __init__(self, game):
        self.game = game
        font_path = "assets/fonts/JetBrainsMono-Regular.ttf"
        self.font_title = pygame.font.Font(font_path, 36)
        self.font_large = pygame.font.Font(font_path, 28)
        self.font_medium = pygame.font.Font(font_path, 20)
        self.font_small = pygame.font.Font(font_path, 15)
        self.font_tiny = pygame.font.Font(font_path, 12)

        self.selected_creature_type = "normal"
        self.selected_tower_type = "basic"
        self.animation_offset = 0
        self.attacker_tab = 0  # 0 = creatures, 1 = bonus
        self.active_bonuses = set()

        self._panel_bg = pygame.Surface((UI_PANEL_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(18 + ratio * 10)
            g = int(34 + ratio * 20)
            b = int(22 + ratio * 12)
            pygame.draw.line(self._panel_bg, (r, g, b, 242), (0, y), (UI_PANEL_WIDTH, y))

        self.setup_buttons()

    def setup_buttons(self):
        panel_x = SCREEN_WIDTH - UI_PANEL_WIDTH
        center_x = panel_x + UI_PANEL_WIDTH // 2
        btn_w = BUTTON_WIDTH
        button_x = center_x - btn_w // 2

        self.end_phase_button = pygame.Rect(button_x, SCREEN_HEIGHT - 66, btn_w, 42)
        self.launch_wave_button = pygame.Rect(button_x, SCREEN_HEIGHT - 118, btn_w, 42)

        tab_w = (UI_PANEL_WIDTH - 44) // 2
        self.tab_creatures_btn = pygame.Rect(panel_x + 18, 140, tab_w, 30)
        self.tab_bonus_btn = pygame.Rect(panel_x + 22 + tab_w, 140, tab_w, 30)

        self.creature_buttons = {}
        creature_types = ['normal', 'fast', 'tank', 'summoner', 'invisible', 'flyer', 'tunneler', 'destroyer']
        y = 180
        for i, ctype in enumerate(creature_types):
            self.creature_buttons[ctype] = pygame.Rect(button_x, y + i * 50, btn_w, 48)

        self.bonus_buttons = {}
        bonus_types = ['regen', 'armor', 'immunity', 'scout']
        y = 180
        for i, btype in enumerate(bonus_types):
            self.bonus_buttons[btype] = pygame.Rect(button_x, y + i * 50, btn_w, 42)

        # Tower buttons (7 types now)
        self.tower_buttons = {}
        tower_types = ['basic', 'sniper', 'slow', 'aoe', 'detector', 'buffer', 'radar']
        y = 200
        for i, ttype in enumerate(tower_types):
            self.tower_buttons[ttype] = pygame.Rect(button_x, y + i * 50, btn_w, 48)

        self.upgrade_button = pygame.Rect(button_x, SCREEN_HEIGHT - 116, btn_w, 44)

    def handle_click(self, pos, game_state):
        mouse_x, mouse_y = pos

        if self.end_phase_button.collidepoint(mouse_x, mouse_y):
            return "end_phase"

        if game_state == "attacker_phase":
            if self.tab_creatures_btn.collidepoint(mouse_x, mouse_y):
                self.attacker_tab = 0
                return None
            if self.tab_bonus_btn.collidepoint(mouse_x, mouse_y):
                self.attacker_tab = 1
                return None

            if self.attacker_tab == 0:
                for creature_type, rect in self.creature_buttons.items():
                    if rect.collidepoint(mouse_x, mouse_y):
                        self.selected_creature_type = creature_type
                        return "add_creature"
            elif self.attacker_tab == 1:
                for bonus_type, rect in self.bonus_buttons.items():
                    if rect.collidepoint(mouse_x, mouse_y):
                        cost = WAVE_BONUSES[bonus_type]['cost']
                        if bonus_type in self.active_bonuses:
                            self.active_bonuses.discard(bonus_type)
                            self.game.attacker.gold += cost
                        elif self.game.attacker.gold >= cost:
                            self.active_bonuses.add(bonus_type)
                            self.game.attacker.gold -= cost
                        return None

            if self.launch_wave_button.collidepoint(mouse_x, mouse_y):
                return "launch_wave"

        elif game_state == "defender_phase":
            for tower_type, rect in self.tower_buttons.items():
                if rect.collidepoint(mouse_x, mouse_y):
                    self.selected_tower_type = tower_type
                    return "select_tower"
            if self.game.selected_defense_tower is not None:
                if self.upgrade_button.collidepoint(mouse_x, mouse_y):
                    return "upgrade_tower"
            if mouse_x < SCREEN_WIDTH - UI_PANEL_WIDTH:
                return "place_tower"

        return None

    def get_active_bonuses(self):
        return list(self.active_bonuses)

    def reset_bonuses(self):
        self.active_bonuses.clear()


    def draw(self, screen, game):
        self.animation_offset += 0.05
        panel_x = SCREEN_WIDTH - UI_PANEL_WIDTH

        screen.blit(self._panel_bg, (panel_x, 0))

        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(104 + ratio * 20)
            g = int(144 + ratio * 26)
            b = int(92 + ratio * 14)
            pygame.draw.line(screen, (r, g, b), (panel_x, y), (panel_x + 1, y))

        self._draw_header(screen, game)

        self._draw_resources(screen, game)

        if game.game_state == "attacker_phase":
            self._draw_attacker_phase(screen, game)
        elif game.game_state == "defender_phase":
            self._draw_defender_phase(screen, game)
        elif game.game_state == "battle":
            self._draw_battle_phase(screen, game)

        if game.game_state in ("attacker_phase", "defender_phase"):
            button_text = "PRET" if game.game_state == "defender_phase" else "CHANGER DE PHASE"
            self._draw_action_button(screen, self.end_phase_button, button_text, (86, 126, 64))

        self._draw_phase_indicator(screen, game.game_state)

        if game.game_state == "game_over":
            self._draw_game_over(screen, game.winner)

    def _draw_header(self, screen, game):
        panel_x = SCREEN_WIDTH - UI_PANEL_WIDTH

        header_rect = pygame.Rect(panel_x, 0, UI_PANEL_WIDTH, 44)
        header_bg = pygame.Surface((UI_PANEL_WIDTH, 44), pygame.SRCALPHA)
        header_bg.fill((18, 38, 20, 214))
        screen.blit(header_bg, (panel_x, 0))

        title = self.font_medium.render("TOWER DEFENSE", True, (236, 214, 150))
        screen.blit(title, title.get_rect(center=(panel_x + UI_PANEL_WIDTH // 2, 22)))

        pygame.draw.line(screen, (96, 132, 72), (panel_x + 16, 44), (panel_x + UI_PANEL_WIDTH - 16, 44), 1)

    def _draw_resources(self, screen, game):
        panel_x = SCREEN_WIDTH - UI_PANEL_WIDTH

        card = pygame.Rect(panel_x + 14, 52, UI_PANEL_WIDTH - 28, 80)
        self._draw_card(screen, card)

        gold_icon = game.assets.get_ui_sprite('gold_icon') if game.assets else None
        hp_icon = game.assets.get_ui_sprite('hp_icon') if game.assets else None

        y_start = card.y + 4
        entries = [
            (gold_icon, 'ATTAQUANT', str(game.attacker.gold), (235, 200, 75)),
            (gold_icon, 'DEFENSEUR', str(game.defender.gold), (235, 200, 75)),
            (hp_icon, 'BASE', str(game.defender.baseHP), (225, 95, 95)),
        ]
        for i, (icon, label, value, vcolor) in enumerate(entries):
            y = y_start + i * 24
            if icon:
                icon_size = 16
                icon_small = pygame.transform.smoothscale(icon, (icon_size, icon_size))
                screen.blit(icon_small, (panel_x + 24, y + 4))

            lbl = self.font_tiny.render(label, True, (184, 198, 170))
            val = self.font_small.render(value, True, vcolor)
            screen.blit(lbl, (panel_x + 52, y + 2))
            screen.blit(val, (panel_x + UI_PANEL_WIDTH - 50, y + 1))

    def _draw_attacker_phase(self, screen, game):
        panel_x = SCREEN_WIDTH - UI_PANEL_WIDTH

        # Tabs
        self._draw_tab(screen, self.tab_creatures_btn, "Creatures", self.attacker_tab == 0)
        self._draw_tab(screen, self.tab_bonus_btn, "Bonus", self.attacker_tab == 1)

        if self.attacker_tab == 0:
            self._draw_creatures_tab(screen, game)
        else:
            self._draw_bonus_tab(screen, game)

        # Launch wave button
        can_launch = game.can_launch_current_wave()
        btn_color = (140, 70, 45) if can_launch else (60, 60, 60)
        self._draw_action_button(screen, self.launch_wave_button, "LANCER LA VAGUE", btn_color)

        total_cost = sum(c.cost for c in game.current_wave.creatures)
        total_creatures = len(game.current_wave.creatures)
        bonus_cost = sum(WAVE_BONUSES[b]['cost'] for b in self.active_bonuses)

        summary_y = SCREEN_HEIGHT - 190
        summary = pygame.Rect(panel_x + 14, summary_y, UI_PANEL_WIDTH - 28, 62)
        self._draw_card(screen, summary)

        screen.blit(
            self.font_tiny.render(f"Creatures: {total_creatures}  |  Bonus: {len(self.active_bonuses)}", True, (206, 220, 190)),
            (panel_x + 26, summary_y + 10)
        )


        requirement = game.get_wave_requirement_text()
        if requirement:
            warn = self.font_tiny.render(requirement, True, (225, 100, 100))
            text_width = warn.get_width()
            screen.blit(warn, (panel_x + (UI_PANEL_WIDTH - text_width) // 2, summary_y - 22))

    def _draw_creatures_tab(self, screen, game):
        creature_data = {
            'normal': ('Normale', 50, '100 PV'),
            'fast': ('Rapide', 60, '50 PV 4x'),
            'tank': ('Tank', 100, '300 PV'),
            'summoner': ('Invocateur', 90, 'x2 on death'),
            'invisible': ('Invisible', 80, 'Furtif'),
            'flyer': ('Volante', 120, 'Vol direct'),
            'tunneler': ('Tunnelier', 110, 'Souterrain'),
            'destroyer': ('Destructeur', 140, 'Casse tours'),
        }

        for ctype, (name, cost, desc) in creature_data.items():
            rect = self.creature_buttons[ctype]
            icon = game.assets.get_creature_sprite(ctype) if game.assets else None
            hovered = rect.collidepoint(pygame.mouse.get_pos())
            selected = self.selected_creature_type == ctype
            affordable = game.attacker.gold >= cost
            self._draw_unit_card(screen, rect, name, cost, desc, icon, hovered, selected, affordable)

    def _draw_bonus_tab(self, screen, game):
        panel_x = SCREEN_WIDTH - UI_PANEL_WIDTH

        for bonus_type, rect in self.bonus_buttons.items():
            info = WAVE_BONUSES[bonus_type]
            active = bonus_type in self.active_bonuses
            hovered = rect.collidepoint(pygame.mouse.get_pos())
            affordable = game.attacker.gold >= info['cost'] or active

            # Card background
            if active:
                bg = (48, 44, 24)
                border = (170, 186, 88)
            elif hovered and affordable:
                bg = (56, 36, 28)
                border = (170, 118, 76)
            else:
                bg = (30, 21, 17)
                border = (86, 62, 44)

            pygame.draw.rect(screen, bg, rect, border_radius=8)
            pygame.draw.rect(screen, border, rect, 2, border_radius=8)

            # Text
            name_txt = self.font_small.render(info['name'], True, (236, 225, 208))
            desc_txt = self.font_tiny.render(info['description'], True, (176, 146, 118))

            screen.blit(name_txt, (rect.x + 14, rect.y + 5))
            screen.blit(cost_txt, (rect.x + rect.width + -33, rect.y + 10))
            screen.blit(desc_txt, (rect.x + 14, rect.y + 24))

            # Active indicator
            if active:
                check_x = rect.x + rect.width - 22
                check_y = rect.y + 24
                pygame.draw.circle(screen, (166, 188, 92), (check_x, check_y), 6)
                pygame.draw.line(screen, (255, 255, 255), (check_x - 3, check_y), (check_x - 1, check_y + 3), 2)
                pygame.draw.line(screen, (255, 255, 255), (check_x - 1, check_y + 3), (check_x + 4, check_y - 3), 2)

    def _draw_defender_phase(self, screen, game):
        panel_x = SCREEN_WIDTH - UI_PANEL_WIDTH
        title = self.font_medium.render("Placer les tours", True, (226, 236, 214))
        screen.blit(title, (panel_x + 60, 150))

        tower_data = {
            'basic': ('Basique', 100, 'Equilibree'),
            'sniper': ('Sniper', 150, 'Longue portee'),
            'slow': ('Ralentir', 120, 'Ralentit'),
            'aoe': ('AoE', 130, 'Degats zone'),
            'detector': ('Detecteur', 140, 'Voit invisibles'),
            'buffer': ('Ampli', 160, '+25% voisins'),
            'radar': ('Radar', 170, 'Large detection'),
        }

        for ttype, (name, cost, desc) in tower_data.items():
            rect = self.tower_buttons[ttype]
            icon = game.assets.get_tower_sprite(ttype) if game.assets else None
            hovered = rect.collidepoint(pygame.mouse.get_pos())
            selected = self.selected_tower_type == ttype
            affordable = game.defender.gold >= cost
            self._draw_unit_card(screen, rect, name, cost, desc, icon, hovered, selected, affordable)

        selected_tower = game.selected_defense_tower
        info_y = 558
        info_card = pygame.Rect(panel_x + 14, info_y, UI_PANEL_WIDTH - 28, 120)
        self._draw_card(screen, info_card, highlight=selected_tower is not None)

        if selected_tower is None:
            screen.blit(
                self.font_tiny.render("Clique une tour posee pour voir", True, (180, 194, 164)),
                (panel_x + 24, info_y + 16)
            )
            screen.blit(
                self.font_tiny.render("sa portee et ses upgrades.", True, (180, 194, 164)),
                (panel_x + 24, info_y + 36)
            )
            screen.blit(
                self.font_tiny.render("Clique une case libre pour poser", True, (180, 194, 164)),
                (panel_x + 24, info_y + 66)
            )
            screen.blit(
                self.font_tiny.render("la tour selectionnee.", True, (180, 194, 164)),
                (panel_x + 24, info_y + 86)
            )
            return

        names = {
            'basic': 'Tour Basique',
            'sniper': 'Tour Sniper',
            'slow': 'Tour Ralentissante',
            'aoe': 'Tour AoE',
            'detector': 'Tour Detecteur',
            'buffer': 'Tour Ampli',
            'radar': 'Tour Radar',
        }
        title = self.font_small.render(names.get(selected_tower.tower_type, selected_tower.tower_type), True, (236, 238, 226))
        level = self.font_tiny.render(f"Niveau {selected_tower.level}/{MAX_TOWER_LEVEL}", True, (235, 200, 75))
        screen.blit(title, (panel_x + 24, info_y + 12))
        screen.blit(level, (panel_x + UI_PANEL_WIDTH - 110, info_y + 16))

        stats_left = [
            f"Degats: {selected_tower.damage}",
            f"Portee: {int(selected_tower.range)}",
            f"Recharge: {selected_tower.attack_speed}",
        ]
        stats_right = [
            f"PV: {int(selected_tower.hp)}/{int(selected_tower.max_hp)}",
            f"Aura: {int(selected_tower.aura_range)}" if selected_tower.aura_range > 0 else "Aura: -",
            f"Boost: {int(selected_tower.aura_value * 100)}%" if selected_tower.aura_type == "damage_boost" else "Boost: -",
        ]
        for i, text in enumerate(stats_left):
            screen.blit(self.font_tiny.render(text, True, (190, 202, 176)), (panel_x + 24, info_y + 40 + i * 18))
        for i, text in enumerate(stats_right):
            screen.blit(self.font_tiny.render(text, True, (190, 202, 176)), (panel_x + 156, info_y + 40 + i * 18))


        can_upgrade = selected_tower.level < MAX_TOWER_LEVEL and game.defender.gold >= selected_tower.upgrade_cost
        upgrade_text = "AMELIORER (MAX)" if selected_tower.level >= MAX_TOWER_LEVEL else f"AMELIORER ({selected_tower.upgrade_cost}g)"
        self._draw_action_button(
            screen,
            self.upgrade_button,
            upgrade_text,
            (108, 142, 74) if can_upgrade else (66, 72, 60)
        )

    def _draw_battle_phase(self, screen, game):
        panel_x = SCREEN_WIDTH - UI_PANEL_WIDTH

        title = self.font_medium.render("Combat en cours", True, (244, 154, 92))
        screen.blit(title, (panel_x + 24, 150))

        alive_count = sum(1 for c in game.board.creatures if c.alive)
        pending = max(0, len(game.turn_player.pending_spawns) - game.turn_player.spawn_index)
        total = len(game.turn_player.pending_spawns)
        spawned = game.turn_player.spawn_index

        # Battle card
        card = pygame.Rect(panel_x + 14, 185, UI_PANEL_WIDTH - 28, 140)
        self._draw_card(screen, card)

        screen.blit(
            self.font_small.render(f"Creatures actives: {alive_count}", True, (232, 238, 224)),
            (panel_x + 30, 200)
        )
        screen.blit(
            self.font_tiny.render(f"En attente: {pending}", True, (176, 188, 164)),
            (panel_x + 30, 226)
        )

        # Spawn progress bar
        bar_x = panel_x + 30
        bar_y = 258
        bar_w = UI_PANEL_WIDTH - 60
        bar_h = 8
        pygame.draw.rect(screen, (28, 20, 16), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
        if total > 0:
            fill = int(bar_w * spawned / total)
            if fill > 0:
                pygame.draw.rect(screen, (200, 100, 70), (bar_x, bar_y, fill, bar_h), border_radius=4)

        progress_txt = self.font_tiny.render(f"Vague: {spawned}/{total}", True, (174, 186, 160))
        screen.blit(progress_txt, (bar_x, bar_y + 14))

        # Active bonuses display
        if hasattr(game, 'current_wave') and game.turn_player.current_wave:
            bonuses = game.turn_player.current_wave.active_bonuses if game.turn_player.current_wave else []
            if bonuses:
                bonus_y = 300
                screen.blit(
                    self.font_tiny.render("Bonus actifs:", True, (214, 210, 136)),
                    (panel_x + 30, bonus_y)
                )
                for i, b in enumerate(bonuses):
                    name = WAVE_BONUSES.get(b, {}).get('name', b)
                    screen.blit(
                        self.font_tiny.render(f"  {name}", True, (192, 196, 124)),
                        (panel_x + 30, bonus_y + 18 + i * 16)
                    )

    # ── Component Drawing ────────────────────────────────────

    def _draw_card(self, screen, rect, highlight=False):
        bg = (28, 44, 26) if not highlight else (40, 58, 34)
        border = (78, 106, 60) if not highlight else (144, 176, 98)
        pygame.draw.rect(screen, bg, rect, border_radius=10)
        pygame.draw.rect(screen, border, rect, 1, border_radius=10)

    def _draw_tab(self, screen, rect, text, active):
        if active:
            bg = (56, 88, 42)
            txt_color = (242, 224, 166)
        else:
            bg = (22, 34, 20)
            txt_color = (168, 180, 156)

        pygame.draw.rect(screen, bg, rect, border_radius=6)
        if active:
            pygame.draw.line(screen, (232, 190, 94), (rect.x + 4, rect.bottom - 1),
                             (rect.right - 4, rect.bottom - 1), 2)

        txt = self.font_tiny.render(text, True, txt_color)
        screen.blit(txt, txt.get_rect(center=rect.center))

    def _draw_unit_card(self, screen, rect, name, cost, desc, icon, hovered, selected, affordable):
        # Background
        if selected:
            bg = (54, 88, 40)
            border = (228, 188, 96)
        elif hovered and affordable:
            bg = (38, 64, 30)
            border = (116, 154, 86)
        else:
            bg = (22, 34, 20)
            border = (64, 88, 50)

        if not affordable and not selected:
            bg = (20, 24, 18)
            border = (44, 52, 40)

        pygame.draw.rect(screen, bg, rect, border_radius=8)
        pygame.draw.rect(screen, border, rect, 2 if selected else 1, border_radius=8)

        content_left = rect.x + 68
        content_top = rect.y + 8
        content_right = rect.right - 18
        icon_center_x = rect.x + 30

        # Icon
        if icon:
            icon_size = 24
            icon_small = pygame.transform.smoothscale(icon, (icon_size, icon_size))
            icon_rect = icon_small.get_rect(center=(icon_center_x, rect.centery))
            screen.blit(icon_small, icon_rect)

        # Name + cost on same line
        # Name + cost on same line
        txt_alpha = 255 if affordable else 120
        name_color = (236, 238, 226) if affordable else (118, 122, 114)
        cost_color = (235, 200, 75) if affordable else (120, 100, 50)

        name_txt = self.font_small.render(name, True, name_color)
        cost_txt = self.font_tiny.render(f"{cost}g", True, cost_color)
        desc_txt = self.font_tiny.render(desc, True, (168, 182, 150) if affordable else (88, 94, 84))

        screen.blit(name_txt, (content_left, content_top))
        cost_rect = cost_txt.get_rect(midright=(content_right, rect.y + 18))
        screen.blit(cost_txt, cost_rect)
        screen.blit(desc_txt, (content_left, rect.y + 29))


    def _draw_action_button(self, screen, rect, text, color):
        hovered = rect.collidepoint(pygame.mouse.get_pos())
        fill = tuple(min(255, c + 20) for c in color) if hovered else color

        # Shadow
        shadow = rect.move(0, 3)
        pygame.draw.rect(screen, (8, 10, 16), shadow, border_radius=8)

        # Button
        pygame.draw.rect(screen, fill, rect, border_radius=8)

        # Top highlight
        hl = pygame.Rect(rect.x + 2, rect.y + 1, rect.width - 4, 1)
        pygame.draw.rect(screen, tuple(min(255, c + 40) for c in fill), hl)

        # Border
        pygame.draw.rect(screen, tuple(min(255, c + 30) for c in fill), rect, 1, border_radius=8)

        # Text
        txt = self.font_small.render(text, True, (245, 245, 250))
        screen.blit(txt, txt.get_rect(center=rect.center))

    def _draw_phase_indicator(self, screen, game_state):
        phase_names = {
            "attacker_phase": "PHASE ATTAQUANT",
            "defender_phase": "PHASE DEFENSEUR",
            "battle": "COMBAT EN COURS",
            "game_over": "PARTIE TERMINEE",
        }
        text = phase_names.get(game_state, "")

        pulse = abs(math.sin(self.animation_offset * 2)) * 0.15 + 0.85
        color = (int(232 * pulse), int(236 * pulse), int(224 * pulse))

        phase_colors = {
            "attacker_phase": (180, 80, 60),
            "defender_phase": (104, 156, 86),
            "battle": (204, 142, 72),
            "game_over": (140, 60, 60),
        }
        accent = phase_colors.get(game_state, (100, 100, 100))

        indicator = pygame.Rect(16, SCREEN_HEIGHT - 50, 220, 30)
        pygame.draw.rect(screen, (18, 28, 18), indicator, border_radius=6)
        pygame.draw.rect(screen, accent, indicator, 2, border_radius=6)

        # Accent dot
        pygame.draw.circle(screen, accent, (30, SCREEN_HEIGHT - 35), 4)

        txt = self.font_tiny.render(text, True, color)
        screen.blit(txt, (42, SCREEN_HEIGHT - 44))

    def _draw_game_over(self, screen, winner):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 195))
        screen.blit(overlay, (0, 0))

        card_w, card_h = 520, 320
        card_x = SCREEN_WIDTH // 2 - card_w // 2
        card_y = SCREEN_HEIGHT // 2 - card_h // 2

        is_attacker = winner == "Attaquant"
        accent = (220, 95, 85) if is_attacker else (85, 150, 220)
        accent_dim = (140, 55, 50) if is_attacker else (50, 90, 140)

        # Card
        card = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        pygame.draw.rect(card, (24, 34, 20, 244), (0, 0, card_w, card_h), border_radius=16)
        pygame.draw.rect(card, accent, (0, 0, card_w, card_h), 2, border_radius=16)

        # Top accent bar
        pygame.draw.rect(card, accent_dim, (0, 0, card_w, 4), border_radius=2)

        screen.blit(card, (card_x, card_y))

        # Title
        title = "VICTOIRE DE L'ATTAQUANT" if is_attacker else "VICTOIRE DU DEFENSEUR"
        title_surf = self.font_large.render(title, True, accent)
        screen.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, card_y + 55)))

        # Separator
        pygame.draw.line(screen, (82, 108, 62),
                         (card_x + 40, card_y + 90), (card_x + card_w - 40, card_y + 90), 1)

        # Stats
        stats = [
            (f"Or restant attaquant: {self.game.attacker.gold}", (235, 200, 75)),
            (f"Or restant defenseur: {self.game.defender.gold}", (235, 200, 75)),
            (f"PV base restants: {self.game.defender.baseHP}", (200, 110, 110)),
        ]
        for i, (text, color) in enumerate(stats):
            surf = self.font_medium.render(text, True, color)
            screen.blit(surf, surf.get_rect(center=(SCREEN_WIDTH // 2, card_y + 125 + i * 35)))

        # Separator
        pygame.draw.line(screen, (82, 108, 62),
                         (card_x + 40, card_y + 240), (card_x + card_w - 40, card_y + 240), 1)

        # Instructions
        sub = self.font_medium.render("Echap pour revenir au menu", True, (170, 182, 156))
        screen.blit(sub, sub.get_rect(center=(SCREEN_WIDTH // 2, card_y + 275)))
