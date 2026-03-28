"""
Unités du jeu - Créatures et Tours
===================================
Ce module contient :
  - Classe mère Creature et ses dérivés (créatures de l'attaquant)
  - Classe mère TourBase et ses dérivés (tours du défenseur)
  - Système d'améliorations globales
  - Animations et sprites
"""

import pygame
import math


# ══════════════════════════════════════════════════════════════════════════
#  CRÉATURES (CÔTÉ ATTAQUANT)
# ══════════════════════════════════════════════════════════════════════════

class Creature:
    """
    Classe mère pour toutes les créatures de l'attaquant.
    
    Stats de base modifiables à la volée par les améliorations globales.
    """
    
    # Stats de base (avant multiplicateurs)
    PV_BASE = 100
    VITESSE_BASE = 1.5  # cases/sec
    COUT_BASE = 15
    GAIN_OR_MORT_BASE = 5
    
    def __init__(self, nom="Créature", x=0, y=0, multiplicateurs=None):
        """
        Args:
            nom: Nom de la créature
            x, y: Position initiale
            multiplicateurs: Dict {'pv': 1.0, 'vitesse': 1.0} depuis l'Attaquant
        """
        self.nom = nom
        self.x = x
        self.y = y
        
        # Multiplicateurs globaux d'amélioration
        self.multiplicateurs = multiplicateurs or {'pv': 1.0, 'vitesse': 1.0}
        
        # Stats calculées avec multiplicateurs
        self.pv_max = int(self.PV_BASE * self.multiplicateurs['pv'])
        self.pv = self.pv_max
        self.vitesse = self.VITESSE_BASE * self.multiplicateurs['vitesse']
        self.cout = int(self.COUT_BASE * self.multiplicateurs.get('cout', 1.0))
        self.gain_or_mort = self.GAIN_OR_MORT_BASE
        
        # Attributs spéciaux
        self.est_camoufle = False
        self.est_resistant = False
        self.armure = 0  # Réduit les dégâts physiques
        
        # Animation
        self.cadre_animation = 0
        self.temps_animation = 0
        self.sprites = []  # À charger depuis les images
        
    def prendre_degats(self, degats, ignore_armure=False):
        """Applique les dégâts, en tenant compte de l'armure."""
        if self.est_resistant and not ignore_armure:
            degt_reduits = max(1, degats - self.armure)
        else:
            degt_reduits = degats
        
        self.pv -= degt_reduits
        return self.pv <= 0  # Retourne True si mort
    
    def reveler_camoufle(self):
        """Retire définitivement le camouflage."""
        self.est_camoufle = False
    
    def mettre_a_jour_animation(self, dt):
        """Met à jour l'animation (dt en secondes)."""
        if self.sprites:
            self.temps_animation += dt
            nb_frames = len(self.sprites)
            # Durée par frame (ajuster selon besoin)
            duree_frame = 0.1
            
            frame_index = int(self.temps_animation / duree_frame) % nb_frames
            self.cadre_animation = frame_index
    
    def dessiner(self, surface, pos_pixel):
        """Dessine la créature à la position donnée."""
        if self.sprites and self.cadre_animation < len(self.sprites):
            sprite = self.sprites[self.cadre_animation]
            surface.blit(sprite, pos_pixel)
    
    def est_morte(self):
        """Vérifie si la créature est morte."""
        return self.pv <= 0


# Créatures dérivées
class CreatureLegere(Creature):
    """Créature rapide et bon marché."""
    PV_BASE = 50
    VITESSE_BASE = 2.5
    COUT_BASE = 10
    GAIN_OR_MORT_BASE = 3


class CreatureLourd(Creature):
    """Créature résistante et coûteuse."""
    PV_BASE = 200
    VITESSE_BASE = 0.8
    COUT_BASE = 25
    GAIN_OR_MORT_BASE = 8
    
    def __init__(self, nom="Créature Lourde", x=0, y=0, multiplicateurs=None):
        super().__init__(nom, x, y, multiplicateurs)
        self.est_resistant = True
        self.armure = 5


class CreatureCamouflee(Creature):
    """Créature camouflée, détectable seulement par certaines tours."""
    PV_BASE = 60
    VITESSE_BASE = 1.8
    COUT_BASE = 20
    GAIN_OR_MORT_BASE = 6
    
    def __init__(self, nom="Créature Camouflée", x=0, y=0, multiplicateurs=None):
        super().__init__(nom, x, y, multiplicateurs)
        self.est_camoufle = True


# ══════════════════════════════════════════════════════════════════════════
#  TOURS (CÔTÉ DÉFENSEUR)
# ══════════════════════════════════════════════════════════════════════════

class TourBase:
    """
    Classe mère pour toutes les tours du défenseur.
    
    Gère la portée, les dégâts, le coût et le type d'attaque.
    """
    
    # Stats de base
    DEGATS_BASE = 15
    PORTEE_BASE = 4  # cases
    VITESSE_ATTAQUE_BASE = 1.0  # tirs/sec
    COUT_BASE = 20
    TYPE_TOUR = "Base"
    
    def __init__(self, col, ligne, x_pixel, y_pixel, evolution=None):
        """
        Args:
            col, ligne: Position sur la grille
            x_pixel, y_pixel: Position en pixels
            evolution: Nom de l'évolution appliquée (ou None)
        """
        self.col = col
        self.ligne = ligne
        self.x = x_pixel
        self.y = y_pixel
        
        # Stats appliquées
        self.degats = self.DEGATS_BASE
        self.portee = self.PORTEE_BASE
        self.vitesse_attaque = self.VITESSE_ATTAQUE_BASE
        self.cout = self.COUT_BASE
        self.evolution = evolution
        
        # Appliquer les modifications d'évolution
        self._appliquer_evolution()
        
        # État d'attaque
        self.temps_depuis_dernier_tir = 0
        self.cible_actuelle = None
    
    def _appliquer_evolution(self):
        """Applique les modifications selon l'évolution choisie."""
        # À surcharger dans les classes dérivées
        pass
    
    def peut_attaquer(self, dt):
        """Vérifie si la tour peut attaquer après dt secondes."""
        self.temps_depuis_dernier_tir += dt
        intervalle_attaque = 1.0 / self.vitesse_attaque
        
        if self.temps_depuis_dernier_tir >= intervalle_attaque:
            self.temps_depuis_dernier_tir = 0
            return True
        return False
    
    def chercher_cible(self, creatures):
        """
        Cherche une cible dans les créatures à portée.
        Peut être surchargée pour des logiques particulières.
        """
        for creature in creatures:
            if not creature.est_morte():
                distance = math.sqrt((creature.x - self.x)**2 + (creature.y - self.y)**2)
                if distance <= self.portee * 40:  # 40px par case
                    return creature
        return None
    
    def attaquer(self, cible):
        """Attaque une cible. Retourne le nombre de créatures tuées."""
        if cible:
            tuees = 1 if cible.prendre_degats(self.degats) else 0
            return tuees
        return 0
    
    def dessiner(self, surface, couleur=(255, 255, 0)):
        """Dessine la tour (cercle avec portée)."""
        # Base de la tour
        pygame.draw.circle(surface, couleur, (int(self.x), int(self.y)), 8)
        
        # Cercle de portée (subtil)
        pygame.draw.circle(surface, (100, 100, 100), (int(self.x), int(self.y)), 
                          int(self.portee * 40), 1)


# Tours dérivées

class TourFleche(TourBase):
    """Tour Flèche - Classique, rapide, bonne portée."""
    DEGATS_BASE = 15
    PORTEE_BASE = 4
    VITESSE_ATTAQUE_BASE = 1.0
    COUT_BASE = 20
    TYPE_TOUR = "Flèche"
    
    def _appliquer_evolution(self):
        if self.evolution == "Sniper":
            self.portee = self.PORTEE_BASE * 2
            self.degats = int(self.DEGATS_BASE * 1.2)
        elif self.evolution == "Flèches perforantes":
            self.degats = int(self.DEGATS_BASE * 1.3)
        elif self.evolution == "Mitrailleuse":
            self.vitesse_attaque = self.VITESSE_ATTAQUE_BASE * 2
            self.degats = int(self.DEGATS_BASE * 0.8)
    
    def chercher_cible(self, creatures):
        """En mode Sniper, cible les camouflés en priorité."""
        if self.evolution == "Sniper":
            # Cibles camouflées d'abord
            for creature in creatures:
                if creature.est_camoufle and not creature.est_morte():
                    distance = math.sqrt((creature.x - self.x)**2 + (creature.y - self.y)**2)
                    if distance <= self.portee * 40:
                        return creature
        
        return super().chercher_cible(creatures)
    
    def attaquer(self, cible):
        """Ignore l'armure si évolution 'Flèches perforantes'."""
        if cible:
            ignore_armure = (self.evolution == "Flèches perforantes")
            tuees = 1 if cible.prendre_degats(self.degats, ignore_armure) else 0
            return tuees
        return 0


class TourEpee(TourBase):
    """Tour Épée - Mêlée, gros dégâts, lente."""
    DEGATS_BASE = 45
    PORTEE_BASE = 1
    VITESSE_ATTAQUE_BASE = 0.5
    COUT_BASE = 30
    TYPE_TOUR = "Épée"
    
    def _appliquer_evolution(self):
        if self.evolution == "Lame lourde":
            self.degats = int(self.DEGATS_BASE * 1.8)
            self.vitesse_attaque = self.VITESSE_ATTAQUE_BASE * 0.6
        elif self.evolution == "Coup circulaire":
            self.portee = 1.5  # Zone d'effet légèrement agrandie
        elif self.evolution == "Lame toxique":
            self.degats = int(self.DEGATS_BASE * 0.9)
            # Le poison sera géré par la créature (ajout d'état)
    
    def attaquer(self, cible):
        """L'évolution 'Coup circulaire' peut toucher plusieurs créatures."""
        # Pour simplifier, on attaque juste la cible principale
        # Une implémentation complète gérerait l'AoE
        if cible:
            tuees = 1 if cible.prendre_degats(self.degats) else 0
            return tuees
        return 0


class TourEau(TourBase):
    """Tour Eau - Contrôle de zone, ralentit les ennemis."""
    DEGATS_BASE = 5
    PORTEE_BASE = 3
    VITESSE_ATTAQUE_BASE = 0.8
    COUT_BASE = 40
    TYPE_TOUR = "Eau"
    
    def __init__(self, col, ligne, x_pixel, y_pixel, evolution=None):
        super().__init__(col, ligne, x_pixel, y_pixel, evolution)
        self.effet_ralentissement = 0.3  # 30%
        self.duree_ralentissement = 2.0  # 2 secondes
    
    def _appliquer_evolution(self):
        if self.evolution == "Gel profond":
            self.effet_ralentissement = 0.6  # 60%
        elif self.evolution == "Tsunami":
            self.portee = int(self.PORTEE_BASE * 1.5)
            # Repousse: à implémenter dans la créature
        elif self.evolution == "Eau révélatrice":
            self.degats = int(self.DEGATS_BASE * 0.8)
            # Retire camouflage définitivement
    
    def appliquer_effet_ralentissement(self, cible):
        """Applique le ralentissement à une cible."""
        # Cet effet doit être géré par la créature ou une classe d'état
        # Pour l'instant, on mémorise juste l'effet
        pass
    
    def attaquer(self, cible):
        """Attaque + applique ralentissement."""
        if cible:
            tuees = 1 if cible.prendre_degats(self.degats) else 0
            self.appliquer_effet_ralentissement(cible)
            
            # Si Eau révélatrice, retire le camouflage
            if self.evolution == "Eau révélatrice":
                cible.reveler_camoufle()
            
            return tuees
        return 0


# ══════════════════════════════════════════════════════════════════════════
#  DICTS DE RÉFÉRENCE
# ══════════════════════════════════════════════════════════════════════════

CREATURES_DISPONIBLES = {
    "legere": CreatureLegere,
    "lourd": CreatureLourd,
    "camouflee": CreatureCamouflee,
}

TOURS_DISPONIBLES = {
    "fleche": TourFleche,
    "epee": TourEpee,
    "eau": TourEau,
}

EVOLUTIONS_PAR_TOUR = {
    "fleche": ["Sniper", "Flèches perforantes", "Mitrailleuse"],
    "epee": ["Lame lourde", "Coup circulaire", "Lame toxique"],
    "eau": ["Gel profond", "Tsunami", "Eau révélatrice"],
}
