"""
Gestion des phases de jeu et des interfaces
=========================================
Système de phases du jeu Tower Defense:
  - Phase de préparation (attaquant choisit ses créatures)
  - Phase d'attaque (défenseur place ses tours)
  - Synchronisation et envoi de la vague
"""

import pygame


def _prix_reduit(prix_base, multiplicateur):
    """Calcule un prix réduit avec un plancher à 1."""
    return max(1, int(prix_base * multiplicateur))


# ══════════════════════════════════════════════════════════════════════════
#  CONSTANTES
# ══════════════════════════════════════════════════════════════════════════

# Phases du jeu
PHASE_PREPARATION_ATTAQUE = "preparation_attaque"
PHASE_ATTAQUE = "attaque"
PHASE_PREPARATION_DEFENSE = "preparation_defense"
PHASE_VAGUE = "vague"


# ══════════════════════════════════════════════════════════════════════════
#  EXTENSION JOUEUR - AMÉLIORATIONS ET INTÉRÊT
# ══════════════════════════════════════════════════════════════════════════

class AmeliorationsJoueur:
    """Gère les améliorations d'un joueur."""
    
    def __init__(self, type_joueur="attaquant"):
        """
        Args:
            type_joueur: "attaquant" ou "defenseur"
        """
        self.type_joueur = type_joueur
        
        if type_joueur == "attaquant":
            # Améliorations pour l'attaquant
            self.pv = 0  # Nombre de rangs d'amélioration PV
            self.vitesse = 0  # Rangs vitesse
            self.cout_reduction = 0  # Rangs réduction coût
            
            # Multiplicateurs appliqués
            self.mult_pv = 1.0
            self.mult_vitesse = 1.0
            self.mult_cout = 1.0
            
            # Coûts d'amélioration (en or)
            self.cout_pv = 50
            self.cout_vitesse = 40
            self.cout_reduction = 60
            
        else:  # defenseur
            # Améliorations pour le défenseur
            self.degats = 0
            self.portee = 0
            self.vitesse = 0
            self.pv_base = 0
            self.interet = 0
            
            self.mult_degats = 1.0
            self.mult_portee = 1.0
            self.mult_vitesse = 1.0
            self.mult_pv_base = 1.0
            
            self.cout_degats = 50
            self.cout_portee = 40
            self.cout_vitesse = 60
            self.cout_pv_base = 50
            self.cout_interet = 70
    
    def acheter_amelioration(self, type_am, joueur):
        """
        Achète une amélioration si possible.
        Retourne True si achat réussi.
        """
        if self.type_joueur == "attaquant":
            if type_am == "pv":
                cout = self.cout_pv
                if joueur.or_disponible >= cout:
                    joueur.or_disponible -= cout
                    self.pv += 1
                    self.mult_pv = 1.0 + (self.pv * 0.2)  # +20% par rang
                    return True
            
            elif type_am == "vitesse":
                cout = self.cout_vitesse
                if joueur.or_disponible >= cout:
                    joueur.or_disponible -= cout
                    self.vitesse += 1
                    self.mult_vitesse = 1.0 + (self.vitesse * 0.15)  # +15% par rang
                    return True
            
            elif type_am == "reduction_cout":
                cout = self.cout_reduction
                if joueur.or_disponible >= cout:
                    joueur.or_disponible -= cout
                    self.cout_reduction += 1
                    self.mult_cout = 1.0 - (self.cout_reduction * 0.1)  # -10% par rang
                    return True
        
        else:  # defenseur
            if type_am == "degats":
                cout = self.cout_degats
                if joueur.or_disponible >= cout:
                    joueur.or_disponible -= cout
                    self.degats += 1
                    self.mult_degats = 1.0 + (self.degats * 0.2)
                    return True
            
            elif type_am == "portee":
                cout = self.cout_portee
                if joueur.or_disponible >= cout:
                    joueur.or_disponible -= cout
                    self.portee += 1
                    self.mult_portee = 1.0 + (self.portee * 0.1)
                    return True
            
            elif type_am == "vitesse":
                cout = self.cout_vitesse
                if joueur.or_disponible >= cout:
                    joueur.or_disponible -= cout
                    self.vitesse += 1
                    self.mult_vitesse = 1.0 + (self.vitesse * 0.15)
                    return True

            elif type_am == "pv":
                cout = self.cout_pv_base
                if joueur.or_disponible >= cout:
                    joueur.or_disponible -= cout
                    self.pv_base += 1
                    self.mult_pv_base = 1.0 + (self.pv_base * 0.2)
                    return True

            elif type_am == "interet":
                cout = self.cout_interet
                if joueur.or_disponible >= cout:
                    joueur.or_disponible -= cout
                    self.interet += 1
                    joueur.augmenter_interet(0.01)
                    return True
        
        return False


# ══════════════════════════════════════════════════════════════════════════
#  GESTIONNAIRE DE PHASES
# ══════════════════════════════════════════════════════════════════════════

class GestionnairePhases:
    """Gère les phases du jeu."""
    
    def __init__(self):
        self.phase_actuelle = PHASE_PREPARATION_ATTAQUE
        self.tour = 1
        self.difficuté_modifiée_par_ameliorations = 1.0
    
    def obtenir_phase(self):
        """Retourne la phase actuelle."""
        return self.phase_actuelle
    
    def changer_phase(self, nouvelle_phase):
        """Change la phase actuelle."""
        self.phase_actuelle = nouvelle_phase
    
    def sequence_phases(self):
        """Retourne la séquence de phases."""
        return [PHASE_PREPARATION_ATTAQUE, PHASE_PREPARATION_DEFENSE, PHASE_VAGUE]
    
    def calculer_difficulte(self, joueur_atk):
        """
        Calcule la difficulté en fonction des améliorations de l'attaquant.
        Les améliorations augmentent le reward du défenseur.
        """
        ameliorations = joueur_atk.ameliorations
        total_rangs = ameliorations.pv + ameliorations.vitesse + ameliorations.cout_reduction
        
        # +20% reward par rang d'amélioration total
        self.difficuté_modifiée_par_ameliorations = 1.0 + (total_rangs * 0.2)
        return self.difficuté_modifiée_par_ameliorations


# ══════════════════════════════════════════════════════════════════════════
#  INTERFACES - AFFICHAGE ET INTERACTION
# ══════════════════════════════════════════════════════════════════════════

class InterfaceAttaquant:
    """Interface pour la phase de préparation de l'attaquant."""
    
    def __init__(self, largeur, hauteur):
        self.largeur = largeur
        self.hauteur = hauteur
        self.boutons = {}
        self.creer_boutons()
        self.creatures_selectionnees = []
        self.credits_restants = 0

    def _layout(self):
        """Retourne la zone du shop à droite."""
        # Le panneau démarre au bord droit de la grille pour supprimer l'espace vide.
        panel_x = 20 + (20 * 40)
        panel_y = 108
        panel_w = self.largeur - panel_x
        panel_h = self.hauteur - panel_y
        return panel_x, panel_y, panel_w, panel_h
    
    def creer_boutons(self):
        """Crée les boutons d'interface."""
        panel_x, panel_y, panel_w, panel_h = self._layout()
        base_x = panel_x + 8
        base_y = panel_y + 88
        col_w = (panel_w - 28) // 3
        col_gap = 6
        row_h = 58
        row_gap = 6
        self.boutons = {
            "creature_legere": {"rect": pygame.Rect(base_x, base_y, col_w, row_h), "text": "Legere\n10", "type": "legere", "couleur": (200, 100, 100)},
            "creature_lourd": {"rect": pygame.Rect(base_x + col_w + col_gap, base_y, col_w, row_h), "text": "Lourde\n25", "type": "lourd", "couleur": (150, 50, 50)},
            "creature_camouflee": {"rect": pygame.Rect(base_x + (2 * (col_w + col_gap)), base_y, col_w, row_h), "text": "Camou\n20", "type": "camouflee", "couleur": (100, 150, 100)},
            "amelioration_pv": {"rect": pygame.Rect(base_x, base_y + row_h + row_gap, col_w, 52), "text": "PV\n50", "type": "am_pv", "couleur": (100, 200, 100)},
            "amelioration_vitesse": {"rect": pygame.Rect(base_x + col_w + col_gap, base_y + row_h + row_gap, col_w, 52), "text": "Vit\n40", "type": "am_vitesse", "couleur": (100, 200, 100)},
            "amelioration_cout": {"rect": pygame.Rect(base_x + (2 * (col_w + col_gap)), base_y + row_h + row_gap, col_w, 52), "text": "Cout\n60", "type": "am_cout", "couleur": (100, 200, 100)},
            "valider": {"rect": pygame.Rect(panel_x + 8, panel_y + panel_h - 52, panel_w - 16, 42), "text": "ENVOYER", "type": "valider", "couleur": (180, 140, 60)},
        }
    
    def dessiner(self, surface, joueur_atk, police):
        """Dessine l'interface."""
        # Panneau semi-transparent
        panel_x, panel_y, panel_w, panel_h = self._layout()
        panel = pygame.Surface((panel_w, panel_h))
        panel.set_alpha(220)
        panel.fill((20, 20, 40))
        surface.blit(panel, (panel_x, panel_y))
        
        # Titre
        titre = pygame.font.Font(None, 28)
        txt_titre = titre.render("PERIODE D'ATTAQUE", True, (200, 100, 200))
        surface.blit(txt_titre, (panel_x + 24, panel_y + 8))
        
        # Ressources avec couleur or
        police_small = pygame.font.Font(None, 18)
        txt_or = police_small.render(f"Or {joueur_atk.or_disponible}", True, (255, 200, 0))
        surface.blit(txt_or, (panel_x + 15, panel_y + 38))
        
        txt_unites = police_small.render(f"U {len(joueur_atk.unites)}", True, (200, 100, 150))
        surface.blit(txt_unites, (panel_x + panel_w - txt_unites.get_width() - 15, panel_y + 38))
        
        # Améliorations actuelles
        poly = joueur_atk.ameliorations
        ams = police_small.render(f"A PV:{poly.pv} V:{poly.vitesse} C:{poly.cout_reduction}", 
                           True, (150, 200, 255))
        surface.blit(ams, (panel_x + 15, panel_y + 58))
        
        # Boutons
        for nom, data in self.boutons.items():
            couleur_base = data["couleur"]
            rect = data["rect"]
            
            # Bouton avec bordure
            pygame.draw.rect(surface, couleur_base, rect)
            pygame.draw.rect(surface, (255, 255, 100), rect, 3)
            
            # Texte
            lines = data["text"].split("\n")
            for i, line in enumerate(lines):
                txt = police_small.render(line, True, (255, 255, 255))
                x = rect.centerx - txt.get_width() // 2
                y = rect.y + 4 + (i * 16)
                surface.blit(txt, (x, y))
    
    def traiter_clic(self, pos, joueur_atk):
        """Traite un clic sur l'interface."""
        for nom, data in self.boutons.items():
            if data["rect"].collidepoint(pos):
                type_action = data["type"]
                
                if type_action == "legere":
                    cout = _prix_reduit(10, joueur_atk.ameliorations.mult_cout)
                    if joueur_atk.or_disponible >= cout:
                        joueur_atk.or_disponible -= cout
                        joueur_atk.unites.append({"type": "legere", "pv": 50})
                        return "creature_ajoutee"
                
                elif type_action == "lourd":
                    cout = _prix_reduit(25, joueur_atk.ameliorations.mult_cout)
                    if joueur_atk.or_disponible >= cout:
                        joueur_atk.or_disponible -= cout
                        joueur_atk.unites.append({"type": "lourd", "pv": 200})
                        return "creature_ajoutee"
                
                elif type_action == "camouflee":
                    cout = _prix_reduit(20, joueur_atk.ameliorations.mult_cout)
                    if joueur_atk.or_disponible >= cout:
                        joueur_atk.or_disponible -= cout
                        joueur_atk.unites.append({"type": "camouflee", "pv": 60})
                        return "creature_ajoutee"
                
                elif type_action == "am_pv":
                    if len(joueur_atk.unites) > 0 and joueur_atk.ameliorations.acheter_amelioration("pv", joueur_atk):
                        return "amelioration_achetee"
                
                elif type_action == "am_vitesse":
                    if len(joueur_atk.unites) > 0 and joueur_atk.ameliorations.acheter_amelioration("vitesse", joueur_atk):
                        return "amelioration_achetee"
                
                elif type_action == "am_cout":
                    if len(joueur_atk.unites) > 0 and joueur_atk.ameliorations.acheter_amelioration("reduction_cout", joueur_atk):
                        return "amelioration_achetee"
                
                elif type_action == "valider":
                    if len(joueur_atk.unites) > 0:
                        return "attaque_validee"
        
        return None


class InterfaceDefenseur:
    """Interface pour la phase de préparation du défenseur."""
    
    def __init__(self, largeur, hauteur):
        self.largeur = largeur
        self.hauteur = hauteur
        self.boutons = {}
        self.creer_boutons()

    def _layout(self):
        """Retourne la zone du shop à droite."""
        # Le panneau démarre au bord droit de la grille pour supprimer l'espace vide.
        panel_x = 20 + (20 * 40)
        panel_y = 108
        panel_w = self.largeur - panel_x
        panel_h = self.hauteur - panel_y
        return panel_x, panel_y, panel_w, panel_h
    
    def creer_boutons(self):
        """Crée les boutons d'interface."""
        panel_x, panel_y, panel_w, panel_h = self._layout()
        base_x = panel_x + 8
        base_y = panel_y + 88
        col_w = (panel_w - 28) // 3
        col_gap = 6
        row_h = 58
        row_gap = 6
        self.boutons = {
            "tour_fleche": {"rect": pygame.Rect(base_x, base_y, col_w, row_h), "text": "Fleche\n20", "type": "fleche", "couleur": (70, 130, 200)},
            "tour_epee": {"rect": pygame.Rect(base_x + col_w + col_gap, base_y, col_w, row_h), "text": "Epee\n30", "type": "epee", "couleur": (80, 100, 185)},
            "tour_eau": {"rect": pygame.Rect(base_x + (2 * (col_w + col_gap)), base_y, col_w, row_h), "text": "Eau\n40", "type": "eau", "couleur": (40, 110, 150)},
            "amelioration_degats": {"rect": pygame.Rect(base_x, base_y + row_h + row_gap, col_w, 52), "text": "Deg\n50", "type": "am_degats", "couleur": (80, 180, 110)},
            "amelioration_portee": {"rect": pygame.Rect(base_x + col_w + col_gap, base_y + row_h + row_gap, col_w, 52), "text": "Port\n40", "type": "am_portee", "couleur": (80, 180, 110)},
            "amelioration_vitesse": {"rect": pygame.Rect(base_x + (2 * (col_w + col_gap)), base_y + row_h + row_gap, col_w, 52), "text": "Vit\n60", "type": "am_vitesse", "couleur": (80, 180, 110)},
            "amelioration_pv": {"rect": pygame.Rect(base_x, base_y + (2 * (row_h + row_gap)), col_w, 52), "text": "PV base\n50", "type": "am_pv", "couleur": (100, 175, 120)},
            "amelioration_interet": {"rect": pygame.Rect(base_x + col_w + col_gap, base_y + (2 * (row_h + row_gap)), col_w, 52), "text": "Interet\n70", "type": "am_interet", "couleur": (100, 175, 120)},
            "valider": {"rect": pygame.Rect(panel_x + 8, panel_y + panel_h - 52, panel_w - 16, 42), "text": "VALIDER", "type": "valider", "couleur": (80, 140, 190)},
        }
    
    def dessiner(self, surface, joueur_def, police):
        """Dessine l'interface."""
        # Panneau semi-transparent
        panel_x, panel_y, panel_w, panel_h = self._layout()
        panel = pygame.Surface((panel_w, panel_h))
        panel.set_alpha(220)
        panel.fill((14, 28, 42))
        surface.blit(panel, (panel_x, panel_y))

        # Titre
        titre = pygame.font.Font(None, 28)
        txt_titre = titre.render("PERIODE DE DEFENSE", True, (120, 205, 255))
        surface.blit(txt_titre, (panel_x + 20, panel_y + 8))

        # Ressources
        police_small = pygame.font.Font(None, 18)
        txt_or = police_small.render(f"Or {joueur_def.or_disponible}", True, (255, 200, 0))
        surface.blit(txt_or, (panel_x + 15, panel_y + 38))

        txt_tours = police_small.render(f"T {len(joueur_def.unites)}", True, (120, 205, 255))
        surface.blit(txt_tours, (panel_x + panel_w - txt_tours.get_width() - 15, panel_y + 38))

        # Améliorations actuelles
        poly = joueur_def.ameliorations
        ams = police_small.render(f"A D:{poly.degats} P:{poly.portee} V:{poly.vitesse} B:{poly.pv_base} I:{poly.interet}",
                           True, (150, 200, 255))
        surface.blit(ams, (panel_x + 15, panel_y + 58))
        
        # Boutons
        for nom, data in self.boutons.items():
            rect = data["rect"]

            # Bouton
            pygame.draw.rect(surface, data["couleur"], rect)
            pygame.draw.rect(surface, (200, 235, 255), rect, 3)
            
            # Texte
            lines = data["text"].split("\n")
            for i, line in enumerate(lines):
                txt = police_small.render(line, True, (255, 255, 255))
                x = rect.centerx - txt.get_width() // 2
                y = rect.y + 4 + (i * 16)
                surface.blit(txt, (x, y))
    
    def traiter_clic(self, pos, joueur_def):
        """Traite un clic sur l'interface."""
        for nom, data in self.boutons.items():
            if data["rect"].collidepoint(pos):
                type_action = data["type"]
                
                if type_action == "fleche":
                    if joueur_def.or_disponible >= 20:
                        joueur_def.or_disponible -= 20
                        joueur_def.unites.append({"type": "fleche", "degats": 15})
                        return "tour_ajoutee"
                
                elif type_action == "epee":
                    if joueur_def.or_disponible >= 30:
                        joueur_def.or_disponible -= 30
                        joueur_def.unites.append({"type": "epee", "degats": 45})
                        return "tour_ajoutee"
                
                elif type_action == "eau":
                    if joueur_def.or_disponible >= 40:
                        joueur_def.or_disponible -= 40
                        joueur_def.unites.append({"type": "eau", "degats": 5})
                        return "tour_ajoutee"
                
                elif type_action == "am_degats":
                    if joueur_def.ameliorations.acheter_amelioration("degats", joueur_def):
                        return "amelioration_achetee"
                
                elif type_action == "am_portee":
                    if joueur_def.ameliorations.acheter_amelioration("portee", joueur_def):
                        return "amelioration_achetee"
                
                elif type_action == "am_vitesse":
                    if joueur_def.ameliorations.acheter_amelioration("vitesse", joueur_def):
                        return "amelioration_achetee"

                elif type_action == "am_pv":
                    if joueur_def.ameliorations.acheter_amelioration("pv", joueur_def):
                        return "amelioration_achetee"

                elif type_action == "am_interet":
                    if joueur_def.ameliorations.acheter_amelioration("interet", joueur_def):
                        return "amelioration_achetee"
                
                elif type_action == "valider":
                    if len(joueur_def.unites) > 0:
                        return "defense_validee"
        
        return None
