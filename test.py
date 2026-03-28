import pygame
import sys
import math
from plateau import Plateau, Joueur, LARGEUR_FENETRE, HAUTEUR_FENETRE, NOIR, ZONE_PLACE, dessiner_plateau, dessiner_infos_partie
from phases import GestionnairePhases, InterfaceAttaquant, InterfaceDefenseur, PHASE_PREPARATION_ATTAQUE, PHASE_PREPARATION_DEFENSE, PHASE_VAGUE
from unites import CREATURES_DISPONIBLES, TOURS_DISPONIBLES, EVOLUTIONS_PAR_TOUR

# Initialisation de Pygame
pygame.init()

# Configuration de la fenetre
LARGEUR = 1280
HAUTEUR = 720
ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Legends Strikes - Menu")

# Couleurs ameliorees
BLANC = (255, 255, 255)
NOIR_MENU = (5, 5, 15)
GRIS_FONCE = (25, 30, 40)
GRIS_MOYEN = (60, 70, 85)
BLEU_FONCE = (15, 30, 60)
BLEU_PRINCIPAL = (70, 150, 255)
BLEU_CLAIR = (100, 180, 255)
BLEU_SURVOL = (120, 200, 255)
VIOLET_FONCE = (80, 40, 140)
VIOLET_PRINCIPAL = (150, 80, 255)
ROUGE_ACCENT = (255, 80, 100)
OR_ACCENT = (255, 200, 60)

# Polices ameliorees
police_petit = pygame.font.Font(None, 36)
police = pygame.font.Font(None, 50)
police_titre = pygame.font.Font(None, 100)
police_sous_titre = pygame.font.Font(None, 32)

def dessiner_gradient(surface, couleur1, couleur2, direction='vertical'):
    """Dessine un degrade de couleur sur la surface."""
    if direction == 'vertical':
        for y in range(surface.get_height()):
            ratio = y / surface.get_height()
            r = int(couleur1[0] * (1 - ratio) + couleur2[0] * ratio)
            g = int(couleur1[1] * (1 - ratio) + couleur2[1] * ratio)
            b = int(couleur1[2] * (1 - ratio) + couleur2[2] * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (surface.get_width(), y))

class Bouton:
    def __init__(self, x, y, largeur, hauteur, texte, couleur, couleur_survol, couleur_ombre=(0,0,0)):
        self.rect = pygame.Rect(x, y, largeur, hauteur)
        self.texte = texte
        self.couleur = couleur
        self.couleur_survol = couleur_survol
        self.couleur_ombre = couleur_ombre
        self.est_survole = False
        self.echelle = 1.0
        self.offset_y = 0
    
    def dessiner(self, surface):
        # Effet d'echelle au survol
        if self.est_survole:
            self.echelle = min(1.05, self.echelle + 0.05)
            self.offset_y = -5
        else:
            self.echelle = max(1.0, self.echelle - 0.05)
            self.offset_y = 0
        
        # Ombre portee
        ombre_rect = pygame.Rect(
            self.rect.x + 4,
            self.rect.y + self.offset_y + 6,
            self.rect.width,
            self.rect.height
        )
        pygame.draw.rect(surface, (0, 0, 0, 100), ombre_rect, border_radius=12)
        
        # Bouton avec bordure brillante
        couleur = self.couleur_survol if self.est_survole else self.couleur
        rect = pygame.Rect(
            self.rect.x,
            self.rect.y + self.offset_y,
            self.rect.width,
            self.rect.height
        )
        
        pygame.draw.rect(surface, couleur, rect, border_radius=12)
        pygame.draw.rect(surface, BLANC, rect, 3, border_radius=12)
        
        # Bordure superieure brillante
        pygame.draw.line(surface, (255, 255, 255, 50), 
                        (rect.x + 5, rect.y + 3),
                        (rect.x + rect.width - 5, rect.y + 3), 2)
        
        # Texte
        texte_surface = police.render(self.texte, True, BLANC)
        texte_rect = texte_surface.get_rect(center=rect.center)
        surface.blit(texte_surface, texte_rect)
    
    def verifier_survol(self, pos):
        self.est_survole = self.rect.collidepoint(pos)
        return self.est_survole
    
    def est_clique(self, pos, clic):
        return self.rect.collidepoint(pos) and clic

# Creation des boutons avec couleurs et styles differents
largeur_bouton = 280
hauteur_bouton = 70
x_centre = LARGEUR // 2 - largeur_bouton // 2

bouton_jouer = Bouton(x_centre, 280, largeur_bouton, hauteur_bouton, 
                      "JOUER", BLEU_PRINCIPAL, BLEU_SURVOL)
bouton_parametres = Bouton(x_centre, 390, largeur_bouton, hauteur_bouton, 
                           "PARAMETRES", VIOLET_PRINCIPAL, (200, 120, 255))
bouton_quitter = Bouton(x_centre, 500, largeur_bouton, hauteur_bouton, 
                        "QUITTER", ROUGE_ACCENT, (255, 120, 140))

boutons = [bouton_jouer, bouton_parametres, bouton_quitter]


def lancer_plateau():
    """Lance la fenetre du plateau avec placement dynamique et vague animee."""
    ecran_jeu = pygame.display.set_mode((LARGEUR_FENETRE, HAUTEUR_FENETRE))
    pygame.display.set_caption("Legends Strikes - Plateau")

    plateau = Plateau()
    joueur_atk = Joueur("Attaquant", "attaquant", or_initial=150)
    joueur_def = Joueur("Defenseur", "defenseur", or_initial=150)
    joueur_atk.interet = 0.08

    gestionnaire = GestionnairePhases()
    interface_atk = InterfaceAttaquant(LARGEUR_FENETRE, HAUTEUR_FENETRE)
    interface_def = InterfaceDefenseur(LARGEUR_FENETRE, HAUTEUR_FENETRE)

    tour = 1
    recompense_base_tour = 35
    clock_jeu = pygame.time.Clock()
    en_jeu = True
    police_interface = pygame.font.Font(None, 24)

    tours_placees = []
    tours_a_placer = []
    creatures_actives = []
    creatures_en_attente_spawn = []
    effets_tirs = []
    texte_vague = ""
    debut_vague_ms = 0
    vague_terminee = False
    arrivees_base = 0
    degats_base_vague = 0
    tour_selectionnee = None
    boutons_evolution = []
    message_action = ""
    message_timer = 0

    def _charger_sprite(nom_fichier, taille):
        try:
            image = pygame.image.load(nom_fichier).convert_alpha()
            return pygame.transform.smoothscale(image, taille)
        except Exception:
            return None

    sprites_creatures = [
        _charger_sprite("s1.png", (26, 26)),
        _charger_sprite("s2.png", (26, 26)),
        _charger_sprite("s3.png", (26, 26)),
    ]

    sprites_creatures_camouflage = [
        _charger_sprite("s1_camouflage.png", (26, 26)),
        _charger_sprite("s2_camouflage.png", (26, 26)),
        _charger_sprite("s3_camouflage.png", (26, 26)),
    ]

    sprites_creatures_renforce = [
        _charger_sprite("s1_str.png", (26, 26)),
        _charger_sprite("s2_str.png", (26, 26)),
        _charger_sprite("s3_str.png", (26, 26)),
    ]

    sprite_defense_base = _charger_sprite("defense.png", (34, 34))

    sprites_tours = {
        "fleche": _charger_sprite("defense1.png", (30, 30)),
        "epee": _charger_sprite("defense2.png", (30, 30)),
        "eau": _charger_sprite("defense3.png", (30, 30)),
    }

    sprites_tours_lvl = {
        1: _charger_sprite("defense_lvl1.png", (32, 32)),
        2: _charger_sprite("defense_lvl2.png", (34, 34)),
        3: _charger_sprite("defense_lvl3.png", (36, 36)),
    }

    base_def_pv_base = 500
    base_def_pv_max = base_def_pv_base
    base_def_pv = base_def_pv_max

    def _tour_sur_case(col, ligne):
        for t in tours_placees:
            if t.col == col and t.ligne == ligne:
                return t
        return None

    def _portee_pixels_tour(tour_obj):
        # Source unique de vérité pour éviter l'écart affichage/logique.
        bonus_epee = 28 if getattr(tour_obj, "type_id", "") == "epee" else 0
        return int((tour_obj.portee * 52) + bonus_epee)

    def _degats_base_par_type(type_unite):
        if type_unite == "lourd":
            return 55
        if type_unite == "camouflee":
            return 40
        return 30

    def _compensation_defenseur_selon_richesse(or_actuel, degats_subis):
        # Plus le défenseur est riche, moins il reçoit de compensation.
        base = max(0, int(140 - (or_actuel * 0.35)))
        bonus_degats = degats_subis // 8
        return max(0, base + bonus_degats)

    def _dessiner_tours():
        # Cette boucle parcourt chaque tour posée et applique l'ordre de rendu:
        # 1) base visuelle, 2) sprite de type, 3) overlays de niveau, 4) portée si sélectionnée.
        couleurs = {
            "fleche": (250, 220, 90),
            "epee": (255, 130, 110),
            "eau": (90, 190, 255),
        }
        for t in tours_placees:
            couleur = couleurs.get(getattr(t, "type_id", "fleche"), (255, 255, 120))
            evol_count = len(getattr(t, "evolutions_appliquees", []))
            niveau = min(3, evol_count)
            sprite_type = sprites_tours.get(getattr(t, "type_id", "fleche"))

            if sprite_defense_base is not None:
                rect_base = sprite_defense_base.get_rect(center=(int(t.x), int(t.y)))
                ecran_jeu.blit(sprite_defense_base, rect_base)

            if sprite_type is not None:
                rect_type = sprite_type.get_rect(center=(int(t.x), int(t.y)))
                ecran_jeu.blit(sprite_type, rect_type)

            # Superposition cumulative des niveaux: lvl1 puis lvl2 puis lvl3.
            # Si aucune amélioration n'est achetée, aucun overlay lvl n'est affiché.
            for n in range(1, niveau + 1):
                sprite_lvl_n = sprites_tours_lvl.get(n)
                if sprite_lvl_n is not None:
                    rect_lvl = sprite_lvl_n.get_rect(center=(int(t.x), int(t.y)))
                    ecran_jeu.blit(sprite_lvl_n, rect_lvl)

            if sprite_defense_base is None and sprite_type is None:
                t.dessiner(ecran_jeu, couleur)

            if tour_selectionnee is t:
                pygame.draw.circle(ecran_jeu, (255, 255, 140), (int(t.x), int(t.y)), _portee_pixels_tour(t), 2)

            badge_x, badge_y = int(t.x) + 13, int(t.y) - 14
            pygame.draw.circle(ecran_jeu, (20, 30, 45), (badge_x, badge_y), 10)
            pygame.draw.circle(ecran_jeu, (220, 235, 255), (badge_x, badge_y), 10, 2)
            txt = pygame.font.Font(None, 18).render(str(niveau), True, (255, 255, 255))
            ecran_jeu.blit(txt, (badge_x - txt.get_width() // 2, badge_y - txt.get_height() // 2))

    def _dessiner_creatures():
        # Cette boucle gère l'affichage dynamique des unités attaquantes:
        # sprite animé, overlays d'état (camouflage/renforcé), puis barre de vie.
        couleurs = {
            "legere": (240, 240, 130),
            "lourd": (220, 90, 90),
            "camouflee": (120, 240, 150),
        }
        for c in creatures_actives:
            if getattr(c, "a_atteint_base", False) or c.est_morte():
                continue

            type_id = getattr(c, "type_id", "legere")
            frame_index = int((pygame.time.get_ticks() / 120) % 3)
            sprite = sprites_creatures[frame_index]
            if sprite is not None:
                rect = sprite.get_rect(center=(int(c.x), int(c.y)))
                ecran_jeu.blit(sprite, rect)

                # Superposition camouflage/renforce selon l'etat réel de l'unité.
                if getattr(c, "est_camoufle", False):
                    overlay_cam = sprites_creatures_camouflage[frame_index]
                    if overlay_cam is not None:
                        ecran_jeu.blit(overlay_cam, overlay_cam.get_rect(center=(int(c.x), int(c.y))))

                if getattr(c, "est_resistant", False):
                    overlay_str = sprites_creatures_renforce[frame_index]
                    if overlay_str is not None:
                        ecran_jeu.blit(overlay_str, overlay_str.get_rect(center=(int(c.x), int(c.y))))
            else:
                couleur = couleurs.get(type_id, (240, 240, 130))
                pygame.draw.circle(ecran_jeu, couleur, (int(c.x), int(c.y)), 8)
                pygame.draw.circle(ecran_jeu, (40, 40, 40), (int(c.x), int(c.y)), 8, 1)

            ratio = 0 if c.pv_max == 0 else max(0, c.pv / c.pv_max)
            largeur = 18
            bx = int(c.x - largeur // 2)
            by = int(c.y - 16)
            pygame.draw.rect(ecran_jeu, (90, 20, 20), (bx, by, largeur, 4))
            pygame.draw.rect(ecran_jeu, (80, 220, 120), (bx, by, int(largeur * ratio), 4))

    def _dessiner_effets_tirs(dt):
        # Chaque itération décrémente le temps de vie visuel d'un tir.
        # Si l'effet est encore actif, on le redessine et on le conserve.
        restant = []
        for effet in effets_tirs:
            effet["ttl"] -= dt
            if effet["ttl"] > 0:
                sx, sy = effet["start"]
                ex, ey = effet["end"]
                pygame.draw.line(ecran_jeu, effet["color"], (int(sx), int(sy)), (int(ex), int(ey)), 2)
                pygame.draw.circle(ecran_jeu, (255, 245, 180), (int(ex), int(ey)), 3)
                restant.append(effet)
        effets_tirs[:] = restant

    def _cible_plus_proche(tour_obj, creatures):
        # Cette recherche sélectionne la cible la plus proche dans la portée utile.
        # Elle est appelée à chaque cycle d'attaque des tours.
        cible = None
        meilleure_dist = 10**18
        portee_pixels = _portee_pixels_tour(tour_obj)
        portee2 = portee_pixels * portee_pixels

        for c in creatures:
            if c.est_morte() or c.a_atteint_base:
                continue
            dx = c.x - tour_obj.x
            dy = c.y - tour_obj.y
            d2 = dx * dx + dy * dy
            if d2 <= portee2 and d2 < meilleure_dist:
                meilleure_dist = d2
                cible = c
        return cible

    def _spawn_creatures_vague():
        # Génère les créatures achetées pendant la phase attaque.
        # Chaque unité reçoit ses multiplicateurs d'amélioration avant le spawn.
        creatures_actives.clear()
        creatures_en_attente_spawn.clear()
        mults = {
            "pv": joueur_atk.ameliorations.mult_pv,
            "vitesse": joueur_atk.ameliorations.mult_vitesse,
            "cout": joueur_atk.ameliorations.mult_cout,
        }
        depart_x, depart_y = plateau.case_vers_centre(*plateau.base_attaquant)
        compteur_par_type = {}

        for unite in joueur_atk.unites:
            cls = CREATURES_DISPONIBLES.get(unite["type"])
            if cls is None:
                continue
            type_id = unite["type"]
            rang_type = compteur_par_type.get(type_id, 0)
            compteur_par_type[type_id] = rang_type + 1

            creature = cls(multiplicateurs=mults)
            creature.type_id = type_id
            creature.progression = 0.0
            creature.a_atteint_base = False
            creature.x = depart_x
            creature.y = depart_y
            creatures_en_attente_spawn.append(
                {
                    "delai_ms": rang_type * 500,
                    "creature": creature,
                }
            )

    def _ouvrir_menu_amelioration(tour_obj):
        nonlocal tour_selectionnee, boutons_evolution
        tour_selectionnee = tour_obj
        boutons_evolution = []

        options = EVOLUTIONS_PAR_TOUR.get(getattr(tour_obj, "type_id", "fleche"), [])
        evols = getattr(tour_obj, "evolutions_appliquees", [])
        base_x = LARGEUR_FENETRE - 275
        base_y = 430
        for i, opt in enumerate(options):
            rect = pygame.Rect(base_x, base_y + i * 38, 260, 32)
            prix = 80 + (len(evols) * 20)
            boutons_evolution.append({"rect": rect, "texte": opt, "prix": prix})

    def _appliquer_evolution_choisie(evolution_nom, prix_evolution):
        # Ce bloc valide d'abord les préconditions (sélection, coût, doublon),
        # puis applique l'effet concret de l'évolution choisie sur la tour.
        nonlocal message_action, message_timer, tour_selectionnee
        if tour_selectionnee is None:
            return

        cout_evolution = prix_evolution
        if joueur_def.or_disponible < cout_evolution:
            message_action = "Or insuffisant pour evolution"
            message_timer = pygame.time.get_ticks() + 1600
            return

        evols = getattr(tour_selectionnee, "evolutions_appliquees", [])
        if evolution_nom in evols:
            message_action = "Evolution deja appliquee"
            message_timer = pygame.time.get_ticks() + 1600
            return

        # Une tour peut cumuler plusieurs evolutions.
        joueur_def.or_disponible -= cout_evolution
        evols.append(evolution_nom)
        tour_selectionnee.evolutions_appliquees = evols

        if evolution_nom == "Sniper":
            tour_selectionnee.portee = min(9, tour_selectionnee.portee * 1.4)
        elif evolution_nom == "Flèches perforantes":
            tour_selectionnee.degats = int(tour_selectionnee.degats * 1.25)
        elif evolution_nom == "Mitrailleuse":
            tour_selectionnee.vitesse_attaque *= 1.35
            tour_selectionnee.degats = int(tour_selectionnee.degats * 0.9)
        elif evolution_nom == "Lame lourde":
            tour_selectionnee.degats = int(tour_selectionnee.degats * 1.35)
        elif evolution_nom == "Coup circulaire":
            tour_selectionnee.portee = min(9, tour_selectionnee.portee + 0.9)
        elif evolution_nom == "Lame toxique":
            tour_selectionnee.vitesse_attaque *= 1.2
        elif evolution_nom == "Gel profond":
            tour_selectionnee.vitesse_attaque *= 1.15
        elif evolution_nom == "Tsunami":
            tour_selectionnee.portee = min(9, tour_selectionnee.portee + 1.0)
        elif evolution_nom == "Eau révélatrice":
            tour_selectionnee.degats = int(tour_selectionnee.degats * 1.2)

        # Le niveau visuel suit strictement le nombre d'evolutions: 0..3.
        tour_selectionnee.niveau = min(3, len(evols))
        message_action = f"Evolution ajoutee: {evolution_nom}"
        message_timer = pygame.time.get_ticks() + 1600

    # Boucle principale de la partie:
    # - lecture des entrées joueur,
    # - mise à jour de l'état de simulation,
    # - rendu de la phase active.
    while en_jeu:
        dt = clock_jeu.tick(60) / 1000.0

        # Boucle événementielle Pygame: traite fermeture, clavier et clics.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                en_jeu = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                phase = gestionnaire.obtenir_phase()

                # Branche "attaque": achats d'unités et validation d'envoi.
                if phase == PHASE_PREPARATION_ATTAQUE:
                    resultat = interface_atk.traiter_clic(pos, joueur_atk)
                    if resultat == "attaque_validee":
                        gestionnaire.changer_phase(PHASE_PREPARATION_DEFENSE)

                # Branche "défense": achats/placement/évolutions des tours.
                elif phase == PHASE_PREPARATION_DEFENSE:
                    resultat = interface_def.traiter_clic(pos, joueur_def)

                    if resultat == "tour_ajoutee" and joueur_def.unites:
                        tours_a_placer.append(joueur_def.unites.pop())

                    elif resultat == "defense_validee":
                        # Début de vague: calcul des revenus de tour et préparation du combat.
                        gestionnaire.changer_phase(PHASE_VAGUE)

                        gain_i_atk = joueur_atk.calculer_interet()
                        gain_i_def = joueur_def.calculer_interet()
                        difficulte = gestionnaire.calculer_difficulte(joueur_atk)
                        bonus_def = int(30 * (difficulte - 1.0))
                        joueur_def.or_disponible += bonus_def

                        _spawn_creatures_vague()
                        texte_vague = f"Interet A:+{gain_i_atk} D:+{gain_i_def} | Bonus D:+{bonus_def}"
                        debut_vague_ms = pygame.time.get_ticks()
                        vague_terminee = False
                        arrivees_base = 0
                        tour += 1

                    elif resultat is None:
                        # Si le clic ne concerne pas un bouton du shop, on teste:
                        # 1) menu d'évolution, 2) sélection de case grille, 3) annulation sélection.
                        # Clic menu evolution (si ouvert)
                        evolution_cliquee = False
                        for btn in boutons_evolution:
                            if btn["rect"].collidepoint(pos):
                                _appliquer_evolution_choisie(btn["texte"], btn.get("prix", 80))
                                evolution_cliquee = True
                                break

                        if evolution_cliquee:
                            continue

                        case = plateau.pixel_vers_case(pos[0], pos[1])
                        if case is not None:
                            col, ligne = case
                            tour_existante = _tour_sur_case(col, ligne)

                            if tour_existante is not None:
                                _ouvrir_menu_amelioration(tour_existante)

                            elif tours_a_placer and plateau.case_a(col, ligne) == ZONE_PLACE:
                                data = tours_a_placer.pop(0)
                                cls = TOURS_DISPONIBLES.get(data["type"])
                                if cls is not None:
                                    cx, cy = plateau.case_vers_centre(col, ligne)
                                    tour_obj = cls(col, ligne, cx, cy)
                                    tour_obj.type_id = data["type"]
                                    tour_obj.niveau = 0
                                    tour_obj.evolutions_appliquees = []
                                    if tour_obj.type_id == "epee":
                                        tour_obj.portee += 0.6
                                    tour_obj.degats = int(tour_obj.degats * joueur_def.ameliorations.mult_degats)
                                    tour_obj.portee = tour_obj.portee * joueur_def.ameliorations.mult_portee
                                    tour_obj.vitesse_attaque = tour_obj.vitesse_attaque * joueur_def.ameliorations.mult_vitesse
                                    tours_placees.append(tour_obj)
                                    _ouvrir_menu_amelioration(tour_obj)

                        else:
                            tour_selectionnee = None
                            boutons_evolution = []

        joueur_def.unites = list(tours_placees)

        # Synchronise les PV max de base avec l'amélioration "PV base".
        nv_max = int(base_def_pv_base * joueur_def.ameliorations.mult_pv_base)
        if nv_max > base_def_pv_max:
            base_def_pv += (nv_max - base_def_pv_max)
            base_def_pv_max = nv_max
        if base_def_pv > base_def_pv_max:
            base_def_pv = base_def_pv_max

        ecran_jeu.fill(NOIR)
        phase = gestionnaire.obtenir_phase()

        # Rendu conditionnel selon la phase active.
        if phase == PHASE_PREPARATION_ATTAQUE:
            dessiner_plateau(ecran_jeu, plateau, afficher_zones=True)
            _dessiner_tours()
            dessiner_infos_partie(ecran_jeu, joueur_atk, joueur_def, tour, afficher_stats_atk=True, afficher_stats_def=False)
            interface_atk.dessiner(ecran_jeu, joueur_atk, police_interface)

        elif phase == PHASE_PREPARATION_DEFENSE:
            dessiner_plateau(ecran_jeu, plateau, afficher_zones=True)
            _dessiner_tours()
            dessiner_infos_partie(ecran_jeu, joueur_atk, joueur_def, tour, afficher_stats_atk=False, afficher_stats_def=True)
            interface_def.dessiner(ecran_jeu, joueur_def, police_interface)

            txt_aide = pygame.font.Font(None, 24).render(
                f"Tours en attente: {len(tours_a_placer)} | Clique case verte: poser | Clique tour: evolutions",
                True,
                (210, 230, 255),
            )
            ecran_jeu.blit(txt_aide, (350, 56))

            if tour_selectionnee is not None and boutons_evolution:
                panel = pygame.Surface((260, 150))
                panel.set_alpha(225)
                panel.fill((18, 26, 46))
                panel_x = LARGEUR_FENETRE - 275
                panel_y = 408
                ecran_jeu.blit(panel, (panel_x, panel_y))

                titre = pygame.font.Font(None, 22).render("Ameliorations tour", True, (220, 230, 255))
                ecran_jeu.blit(titre, (panel_x + 10, panel_y + 8))

                lvl_sel = min(3, len(getattr(tour_selectionnee, "evolutions_appliquees", [])))
                txt_lvl = pygame.font.Font(None, 18).render(f"Niveau: {lvl_sel}", True, (210, 230, 255))
                ecran_jeu.blit(txt_lvl, (panel_x + 10, panel_y + 30))

                for btn in boutons_evolution:
                    deja = btn["texte"] in getattr(tour_selectionnee, "evolutions_appliquees", [])
                    fond = (60, 90, 110) if deja else (75, 110, 180)
                    pygame.draw.rect(ecran_jeu, (75, 110, 180), btn["rect"], border_radius=6)
                    pygame.draw.rect(ecran_jeu, fond, btn["rect"], border_radius=6)
                    pygame.draw.rect(ecran_jeu, (190, 220, 255), btn["rect"], 2, border_radius=6)
                    suffixe = " (OK)" if deja else ""
                    txt = pygame.font.Font(None, 18).render(f"{btn['texte']} {btn.get('prix', 80)}{suffixe}", True, (255, 255, 255))
                    ecran_jeu.blit(txt, (btn["rect"].x + 8, btn["rect"].y + 7))

        elif phase == PHASE_VAGUE:
            dessiner_plateau(ecran_jeu, plateau, afficher_zones=False)
            _dessiner_tours()

            # Spawn progressif: 0,5 s entre deux unités du même type.
            ecoule_ms = pygame.time.get_ticks() - debut_vague_ms
            restantes = []
            for item in creatures_en_attente_spawn:
                if ecoule_ms >= item["delai_ms"]:
                    creatures_actives.append(item["creature"])
                else:
                    restantes.append(item)
            creatures_en_attente_spawn[:] = restantes

            # Boucle de déplacement des créatures: progression sur le chemin et dégâts base à l'arrivée.
            for c in creatures_actives:
                if c.est_morte() or c.a_atteint_base:
                    continue

                c.progression += c.vitesse * dt
                dernier_index = len(plateau.chemin) - 1
                if c.progression >= dernier_index:
                    c.a_atteint_base = True
                    arrivees_base += 1
                    degats = _degats_base_par_type(getattr(c, "type_id", "legere"))
                    degats_base_vague += degats
                    base_def_pv = max(0, base_def_pv - degats)
                    continue

                i = int(c.progression)
                frac = c.progression - i
                x1, y1 = plateau.case_vers_centre(*plateau.chemin[i])
                x2, y2 = plateau.case_vers_centre(*plateau.chemin[i + 1])
                c.x = x1 + (x2 - x1) * frac
                c.y = y1 + (y2 - y1) * frac

            # Boucle de combat des tours: acquisition cible, tir, gain à l'élimination.
            cibles = [c for c in creatures_actives if not c.est_morte() and not c.a_atteint_base]
            for t in tours_placees:
                if t.peut_attaquer(dt):
                    cible = _cible_plus_proche(t, cibles)
                    if cible is not None:
                        etait_vivante = not cible.est_morte()
                        tuees = t.attaquer(cible)
                        effets_tirs.append(
                            {
                                "start": (t.x, t.y),
                                "end": (cible.x, cible.y),
                                "ttl": 0.08,
                                "color": (255, 230, 120),
                            }
                        )
                        if tuees > 0 and etait_vivante:
                            joueur_def.or_disponible += cible.gain_or_mort

            _dessiner_creatures()
            _dessiner_effets_tirs(dt)
            dessiner_infos_partie(ecran_jeu, joueur_atk, joueur_def, tour, afficher_stats_atk=False, afficher_stats_def=False)

            message_vague = pygame.font.Font(None, 48)
            txt_vague = message_vague.render("VAGUE EN COURS", True, (255, 100, 100))
            ecran_jeu.blit(txt_vague, (LARGEUR_FENETRE // 2 - txt_vague.get_width() // 2, 100))

            # Condition de fin de vague: plus aucune créature active sur le terrain.
            vivantes = [c for c in creatures_actives if not c.est_morte() and not c.a_atteint_base]
            if not vivantes and not creatures_en_attente_spawn and not vague_terminee:
                vague_terminee = True
                debut_vague_ms = pygame.time.get_ticks()

                if arrivees_base > 0:
                    gain_atk = recompense_base_tour + (arrivees_base * 8) + (degats_base_vague // 10)
                    joueur_atk.or_disponible += gain_atk
                    compensation_def = _compensation_defenseur_selon_richesse(joueur_def.or_disponible, degats_base_vague)
                    joueur_def.or_disponible += compensation_def
                    texte_vague = f"Percee ({arrivees_base}) : ATK +{gain_atk} or | DEF +{compensation_def} or"
                else:
                    gain_def = recompense_base_tour + (len(creatures_actives) * 3)
                    joueur_def.or_disponible += gain_def
                    texte_vague = f"Defense parfaite ! Defenseur +{gain_def} or"

                if base_def_pv <= 0:
                    texte_vague = "Base defense detruite: victoire Attaquant"
                    en_jeu = False

            if texte_vague:
                police_msg = pygame.font.Font(None, 30)
                txt_resultat = police_msg.render(texte_vague, True, (250, 220, 120))
                ecran_jeu.blit(txt_resultat, (LARGEUR_FENETRE // 2 - txt_resultat.get_width() // 2, 150))

            if vague_terminee and (pygame.time.get_ticks() - debut_vague_ms >= 1700):
                # Transition de vague: reset temporaire + progression du tour.
                gestionnaire.changer_phase(PHASE_PREPARATION_ATTAQUE)
                joueur_atk.or_disponible += 28 + (tour * 4)
                joueur_atk.unites = []
                texte_vague = ""
                creatures_actives.clear()
                creatures_en_attente_spawn.clear()
                arrivees_base = 0
                degats_base_vague = 0

                # Si la base tient jusqu'à la fin du round 10, victoire défense.
                if tour > 10 and base_def_pv > 0:
                    message_action = "Victoire Defense: base intacte au round 10"
                    message_timer = pygame.time.get_ticks() + 2000
                    en_jeu = False

        # Affiche uniquement les PV au-dessus de la base défenseur.
        bdx, bdy = plateau.case_vers_centre(*plateau.base_defenseur)
        txt_base = pygame.font.Font(None, 24).render(f"PV {base_def_pv}/{base_def_pv_max}", True, (130, 220, 255))
        ecran_jeu.blit(txt_base, (bdx - txt_base.get_width() // 2, bdy - 36))

        if message_action and pygame.time.get_ticks() < message_timer:
            msg = pygame.font.Font(None, 26).render(message_action, True, (255, 230, 120))
            ecran_jeu.blit(msg, (LARGEUR_FENETRE // 2 - msg.get_width() // 2, HAUTEUR_FENETRE - 72))

        pygame.display.flip()

    pygame.display.set_mode((LARGEUR, HAUTEUR))
    pygame.display.set_caption("Legends Strikes - Menu")


# Boucle principale
clock = pygame.time.Clock()
en_cours = True
angle_animation = 0

# Boucle principale du menu:
# mise à jour des interactions des boutons et affichage décoratif.
while en_cours:
    pos_souris = pygame.mouse.get_pos()
    clic = False
    angle_animation = (angle_animation + 1) % 360
    
    # Lecture des événements de menu (fermeture et clic gauche).
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            en_cours = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                clic = True
    
    # Verifier les survols et clics
    # Mise à jour des effets de survol de tous les boutons.
    for bouton in boutons:
        bouton.verifier_survol(pos_souris)
    
    if bouton_jouer.est_clique(pos_souris, clic):
        lancer_plateau()
    
    if bouton_parametres.est_clique(pos_souris, clic):
        print("Parametres clique !")
    
    if bouton_quitter.est_clique(pos_souris, clic):
        en_cours = False
    
    # Dessiner - Gradient de fond
    dessiner_gradient(ecran, BLEU_FONCE, NOIR_MENU, 'vertical')
    
    # Boucle décorative: cercles de fond animés selon l'angle courant.
    for i in range(3):
        rayon = 200 + i * 150 + int(50 * math.sin(angle_animation * 0.01))
        alpha_val = 10 - i * 3
        pygame.draw.circle(ecran, (100, 150, 255, alpha_val), 
                          (LARGEUR // 2 + 200, HAUTEUR // 2 - 100), rayon, 1)
    
    # Titre avec effet
    titre = police_titre.render("Legends Strikes", True, BLANC)
    titre_ombre = police_titre.render("Legends Strikes", True, (80, 150, 255))
    titre_rect = titre.get_rect(center=(LARGEUR // 2, 100))
    titre_ombre_rect = titre_ombre.get_rect(center=(LARGEUR // 2 + 3, 103))
    ecran.blit(titre_ombre, titre_ombre_rect)
    ecran.blit(titre, titre_rect)
    
    # Sous-titre
    sous_titre = police_sous_titre.render("Affrontez vos adversaires", True, BLEU_CLAIR)
    sous_titre_rect = sous_titre.get_rect(center=(LARGEUR // 2, 160))
    ecran.blit(sous_titre, sous_titre_rect)
    
    # Boutons
    for bouton in boutons:
        bouton.dessiner(ecran)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
