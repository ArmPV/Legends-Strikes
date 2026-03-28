"""
Legends Strikes - Plateau de jeu
=================================
Ce module contient toute la logique du plateau de jeu :
  - Les constantes de dimensions et de couleurs
  - Les classes de base : Unite, Attaquant, Defenseur, Joueur
  - La génération du chemin aléatoire (en zigzag, avec des vrais virages)
  - La génération des zones de placement (toute case hors chemin)
  - La classe Plateau qui assemble le tout
  - Les fonctions d'affichage Pygame (dessiner_plateau, dessiner_infos_partie)

Architecture du jeu :
  - L'attaquant envoie ses unités depuis la BASE ATK (bord gauche)
  - Les unités suivent le CHEMIN case par case jusqu'à la BASE DEF (bord droit)
  - Le défenseur place ses tours sur les ZONES DE PLACEMENT (toutes les cases
    qui ne sont pas sur le chemin)
  - Les tours tirent sur les unités qui passent à portée
"""
import random
import pygame
import math
from phases import AmeliorationsJoueur


# ══════════════════════════════════════════════════════════════════════════
#  CONSTANTES DU PLATEAU
# ══════════════════════════════════════════════════════════════════════════

# Taille de la fenêtre Pygame quand on affiche le plateau de jeu
# (différente de la fenêtre du menu qui fait 800×600)
LARGEUR_FENETRE = 1280   # largeur en pixels
HAUTEUR_FENETRE = 720    # hauteur en pixels

# Dimensions de la grille de jeu
COLS = 20                # nombre de colonnes  (axe horizontal)
LIGNES = 14              # nombre de lignes    (axe vertical)
TAILLE_CASE = 40         # taille d'une case en pixels (carré 40×40)

# Marges du plateau
# La grille est volontairement alignée à gauche pour libérer un panneau UI à droite.
MARGE_X = 20
MARGE_Y = (HAUTEUR_FENETRE - LIGNES * TAILLE_CASE) // 2

# ── Couleurs (tuples RGB) ──────────────────────────────────────────────
# Utilisées partout dans l'affichage Pygame pour dessiner les cases,
# le texte, les symboles de bases, etc.
BLANC       = (255, 255, 255)
NOIR        = (8, 12, 25)            # Fond noir profond (cyberpunk)
GRIS_SOMBRE = (20, 28, 40)           # Gris-bleu sombre
GRIS_MOYEN  = (45, 55, 75)           # Gris-bleu moyen
GRIS        = (35, 40, 50)           # bordures des cases
GRIS_CASE   = (20, 25, 35)           # fond des cases vides (inutilisé maintenant)
VERT        = (50, 220, 100)
VERT_CLAIR  = (100, 255, 150)

# Zone de placement - Vert néon cyberpunk
ZONE_VERT     = (0, 220, 150)        # Cyan néon vif
ZONE_VERT_2   = (50, 240, 180)       # Cyan néon clair
ZONE_VERT_D   = (20, 100, 80)        # Cyan néon sombre

# Chemin - Jaune classique (ancien style)
CHEMIN_OR     = (255, 210, 80)       # Jaune du chemin (couleur d'avant)
CHEMIN_OMBRE  = (200, 150, 40)       # Ombre du chemin
CHEMIN_HAUT   = (255, 230, 120)      # Subrillance du chemin

# Base attaquant - Rouge-Rose vif
ROUGE         = (255, 70, 100)       # Rouge-rose principal
ROUGE_FONCE   = (200, 40, 70)        # Rouge-rose sombre
ROUGE_CLAIR   = (255, 150, 160)      # Rouge-rose clair

# Base défenseur - Bleu Cyan cyberpunk
BLEU          = (70, 200, 255)       # Bleu cyan principal
BLEU_FONCE    = (40, 120, 180)       # Bleu cyan sombre
BLEU_CLAIR    = (150, 230, 255)      # Bleu cyan clair / texte défenseur dans le HUD

# Accents
JAUNE       = (255, 210, 80)         # ligne du chemin + numéro de tour
ORANGE      = (255, 150, 50)
OR_ACCENT   = (255, 200, 60)         # Accents or
MARRON      = (140, 100, 60)         # couleur des cases du chemin
MARRON_CLAIR = (180, 130, 80)
VIOLET      = (180, 100, 255)

# ── Types de case ──────────────────────────────────────────────────────
# Chaque case de la grille a un type parmi ceux-ci.
# On les utilise comme clés dans le dictionnaire COULEURS_CASE (voir plus bas)
# et pour la logique de jeu (savoir si on peut placer une tour, etc.)
VIDE       = 0    # case vide (ne devrait pas exister sur le plateau final)
CHEMIN     = 1    # case faisant partie du chemin que les attaquants suivent
BASE_ATK   = 2    # base attaquant : point de spawn des unités (bord gauche)
BASE_DEF   = 3    # base défenseur : objectif à protéger (bord droit)
ZONE_PLACE = 4    # zone de placement : le défenseur peut y poser ses tours


# ════════════════════════════════════════════════════════════════════════
#  CLASSES DE BASE
# ════════════════════════════════════════════════════════════════════════

class Unite:
    """
    Classe de base pour toutes les unités du jeu.
    
    C'est la classe parente de Attaquant et Defenseur.
    Elle contient les attributs communs (PV, attaque, position...)
    et les méthodes de base (subir des dégâts, vérifier si vivant).
    
    Attributs :
        nom (str)      : nom de l'unité (ex: "Guerrier", "Tour d'archers")
        pv_max (int)    : points de vie maximum (pour afficher la barre de vie)
        pv (int)        : points de vie actuels
        attaque (int)   : dégâts infligés par attaque
        vitesse (int)   : nombre de cases parcourues par tour (0 pour les tours)
        portee (int)    : portée d'attaque en cases (distance de Manhattan)
        cout (int)      : coût en or pour acheter/placer cette unité
        x, y (int)      : position actuelle sur la grille (colonne, ligne)
        vivant (bool)   : True si l'unité est encore en vie
    """
    def __init__(self, nom, pv, attaque, vitesse, portee, cout):
        self.nom = nom
        self.pv_max = pv       # on garde le max pour les barres de vie
        self.pv = pv           # PV actuels, diminuent quand l'unité prend des dégâts
        self.attaque = attaque
        self.vitesse = vitesse  # cases par tour (ex: 1 = lent, 3 = rapide)
        self.portee = portee    # portée en cases (distance de Manhattan)
        self.cout = cout        # coût en or pour invoquer/placer cette unité
        self.x = 0             # position colonne sur la grille
        self.y = 0             # position ligne sur la grille
        self.vivant = True     # passe à False quand PV <= 0

    def subir_degats(self, degats):
        """
        Inflige des dégâts à cette unité.
        
        Réduit les PV du montant 'degats'. Si les PV tombent à 0 ou moins,
        l'unité meurt (vivant = False).
        
        Args:
            degats (int) : nombre de points de dégâts à infliger
        """
        self.pv -= degats
        if self.pv <= 0:
            self.pv = 0
            self.vivant = False

    def est_vivant(self):
        """Renvoie True si l'unité est encore en vie (PV > 0)."""
        return self.vivant

    def __repr__(self):
        """Représentation texte pour le debug (ex: 'Guerrier (PV:80/100 ATK:15)')."""
        return f"{self.nom} (PV:{self.pv}/{self.pv_max} ATK:{self.attaque})"


class Attaquant(Unite):
    """
    Unité offensive qui avance sur le chemin vers la base défenseur.
    
    Hérite de Unite. La portée est fixée à 1 (corps à corps).
    L'attaquant se déplace case par case le long du chemin généré.
    
    Attribut supplémentaire :
        index_chemin (int) : index dans la liste 'chemin' du plateau,
                             représente la progression sur le parcours.
                             0 = départ (base ATK), len(chemin)-1 = arrivée (base DEF)
    """
    def __init__(self, nom, pv, attaque, vitesse, cout):
        # Portée fixée à 1 car les attaquants sont des unités de mêlée
        super().__init__(nom, pv, attaque, vitesse, portee=1, cout=cout)
        self.index_chemin = 0  # commence au début du chemin (base ATK)

    def avancer(self, chemin):
        """
        Fait avancer l'unité de 'self.vitesse' cases sur le chemin.
        
        L'unité ne peut pas dépasser la fin du chemin (base DEF).
        Après le déplacement, les coordonnées (x, y) sont mises à jour.
        
        Args:
            chemin (list[tuple]) : liste ordonnée des cases du chemin
                                   [(col, ligne), (col, ligne), ...]
        """
        # On avance du minimum entre la vitesse et les cases restantes
        pas = min(self.vitesse, len(chemin) - 1 - self.index_chemin)
        self.index_chemin += pas
        # Mise à jour des coordonnées grille
        self.x, self.y = chemin[self.index_chemin]

    def a_atteint_base(self, chemin):
        """
        Vérifie si l'unité a atteint la base défenseur (fin du chemin).
        
        Returns:
            bool : True si l'unité est arrivée à la dernière case du chemin
        """
        return self.index_chemin >= len(chemin) - 1


class Defenseur(Unite):
    """
    Tour défensive placée sur une zone de placement par le joueur défenseur.
    
    Hérite de Unite. La vitesse est fixée à 0 (une tour ne bouge pas).
    La tour tire automatiquement sur les attaquants qui passent à portée.
    
    La portée utilise la distance de Manhattan :
      distance = |x1 - x2| + |y1 - y2|
    Exemple : portée 3 = peut toucher une cible à 3 cases de distance max.
    """
    def __init__(self, nom, pv, attaque, portee, cout):
        # Vitesse = 0 car une tour ne se déplace jamais
        super().__init__(nom, pv, attaque, vitesse=0, portee=portee, cout=cout)

    def peut_attaquer(self, cible):
        """
        Vérifie si cette tour peut attaquer une cible donnée.
        
        Conditions : la cible doit être vivante ET à portée (distance de Manhattan).
        
        Args:
            cible (Unite) : l'unité attaquante à vérifier
        
        Returns:
            bool : True si la cible est à portée et vivante
        """
        dist = abs(self.x - cible.x) + abs(self.y - cible.y)
        return dist <= self.portee and cible.est_vivant()


class Joueur:
    """
    Représente un joueur dans la partie.
    
    Il existe deux rôles :
      - "attaquant" : envoie des unités (Attaquant) sur le chemin
      - "defenseur" : place des tours (Defenseur) sur les zones de placement
    
    Chaque joueur possède un budget en or qu'il dépense pour acheter ses unités.
    
    Attributs :
        nom (str)             : nom affiché du joueur (ex: "Joueur 1")
        role (str)            : "attaquant" ou "defenseur"
        or_disponible (int)   : or restant pour acheter des unités/tours
        unites (list[Unite])  : liste de toutes les unités du joueur en jeu
        interet (float)       : taux d'intérêt gagnant par tour (0.05 = 5% par tour)
        ameliorations         : objet AmeliorationsJoueur pour gérer les upgrades
    """
    def __init__(self, nom, role, or_initial=100):
        self.nom = nom
        self.role = role              # "attaquant" ou "defenseur"
        self.or_disponible = or_initial
        self.unites = []              # unités achetées et placées/envoyées
        
        # Intérêt - justifie de ne pas tout dépenser immédiatement
        self.interet = 0.05  # 5% par tour (peut être amélioré)
        self.gains_interet_tour = 0  # accumule les gains d'intérêt
        
        # Améliorations pour ce joueur
        self.ameliorations = AmeliorationsJoueur(role)
    
    def calculer_interet(self):
        """Calcule et ajoute les gains d'intérêt au joueur."""
        gain = int(self.or_disponible * self.interet)
        self.gains_interet_tour = gain
        self.or_disponible += gain
        return gain
    
    def augmenter_interet(self, bonus):
        """Augmente le taux d'intérêt (pour les améliorations)."""
        self.interet += bonus

    def ajouter_unite(self, unite):
        """
        Achète et ajoute une unité au joueur.
        
        Vérifie que le joueur a assez d'or. Si oui, déduit le coût
        et ajoute l'unité à sa liste.
        
        Args:
            unite (Unite) : l'unité à acheter
        
        Returns:
            bool : True si l'achat a réussi, False si pas assez d'or
        """
        if self.or_disponible >= unite.cout:
            self.or_disponible -= unite.cout
            self.unites.append(unite)
            return True
        return False

    def __repr__(self):
        """Représentation texte pour le debug."""
        return f"Joueur({self.nom}, {self.role}, or={self.or_disponible})"


# ════════════════════════════════════════════════════════════════════════
#  GENERATION DU CHEMIN ALEATOIRE (avec virages)
# ════════════════════════════════════════════════════════════════════════

def generer_chemin():
    """
    Génère un chemin aléatoire en zigzag avec de vrais virages.
    
    Le chemin va de la BASE ATTAQUANT (bord gauche, colonne 0) à la
    BASE DÉFENSEUR (bord droit, colonne COLS-1).
    
    ⚠ IMPORTANT : ce chemin est généré UNE SEULE FOIS par partie.
    Il ne change PAS entre les tours.
    
    Algorithme en 2 étapes :
    ─────────────────────────
    1) WAYPOINTS : on crée 4 à 7 points de passage espacés horizontalement.
       Chaque waypoint alterne entre le haut et le bas de la grille pour
       forcer de grands virages en zigzag.
       
       Exemple de waypoints :  (0,3) → (5,10) → (10,3) → (15,11) → (19,5)
    
    2) SEGMENTS EN L : entre chaque paire de waypoints, on trace un chemin
       en forme de « L » (un segment horizontal + un segment vertical).
       L'ordre (horizontal d'abord ou vertical d'abord) est choisi
       aléatoirement pour plus de variété.
       
       Waypoint A ──────┐          ou      Waypoint A
                        │                       │
                        │                       │
                   Waypoint B              ─────Waypoint B
    
    Si la génération échoue (rare), un chemin de secours en S est utilisé.
    
    Returns:
        list[tuple(int,int)] : liste ordonnée de (colonne, ligne) formant le chemin
    """
    # On tente jusqu'à 100 fois de générer un chemin valide
    # (en pratique ça réussit quasi toujours au 1er essai)
    for _tentative in range(100):

        # ── ÉTAPE 1 : Créer des waypoints en zigzag ────────────────
        # Plus il y a de segments, plus il y aura de virages
        nb_segments = random.randint(4, 7)  # entre 4 et 7 virages

        # Espacement horizontal régulier entre chaque waypoint
        # Exemple : 20 colonnes / 5 segments = 1 waypoint toutes les 4 colonnes
        step_x = (COLS - 1) / nb_segments

        waypoints = []

        # Premier waypoint = bord gauche, rangée aléatoire (en évitant les bords)
        start_y = random.randint(2, LIGNES - 3)
        waypoints.append((0, start_y))

        prev_y = start_y
        for i in range(1, nb_segments):
            # Position horizontale du waypoint (répartie uniformément)
            wx = int(round(i * step_x))
            wx = max(1, min(wx, COLS - 2))  # garder dans les limites

            # ── Alternance haut/bas pour forcer de grands virages ──
            # Si le waypoint précédent est en haut → celui-ci va en bas
            # Si le waypoint précédent est en bas  → celui-ci va en haut
            marge = 3  # écart minimum entre deux waypoints consécutifs
            if prev_y < LIGNES // 2:
                # Le précédent est en haut → on descend
                wy = random.randint(max(prev_y + marge, LIGNES // 2), LIGNES - 3)
            else:
                # Le précédent est en bas → on monte
                wy = random.randint(2, min(prev_y - marge, LIGNES // 2 - 1))
            wy = max(1, min(wy, LIGNES - 2))  # sécurité bornes

            waypoints.append((wx, wy))
            prev_y = wy

        # Dernier waypoint = bord droit, rangée aléatoire
        end_y = random.randint(2, LIGNES - 3)
        waypoints.append((COLS - 1, end_y))

        # ── ÉTAPE 2 : Relier les waypoints par des segments en L ───
        chemin = [waypoints[0]]       # le chemin commence au 1er waypoint
        chemin_set = {waypoints[0]}   # set pour éviter les doublons (O(1))

        for k in range(len(waypoints) - 1):
            # Points A et B à relier
            ax, ay = waypoints[k]
            bx, by = waypoints[k + 1]

            # On choisit aléatoirement l'ordre du L :
            #   True  → horizontal d'abord, puis vertical  (─ puis │)
            #   False → vertical d'abord, puis horizontal  (│ puis ─)
            if random.choice([True, False]):
                segment = _segment_horizontal(ax, ay, bx) + _segment_vertical(bx, ay, by)
            else:
                segment = _segment_vertical(ax, ay, by) + _segment_horizontal(ax, by, bx)

            # Ajouter chaque case du segment au chemin (sans doublons)
            for pt in segment:
                if pt not in chemin_set:
                    if 0 <= pt[0] < COLS and 0 <= pt[1] < LIGNES:
                        chemin.append(pt)
                        chemin_set.add(pt)

        # ── Validation du chemin ───────────────────────────────────
        # Le chemin doit avoir au moins COLS+4 cases (sinon trop court)
        if len(chemin) < COLS + 4:
            continue
        # Le chemin doit aller du bord gauche (col 0) au bord droit (col COLS-1)
        if chemin[0][0] != 0 or chemin[-1][0] != COLS - 1:
            continue

        return chemin  # ✓ Chemin valide trouvé !

    # ── Fallback : chemin de secours en forme de S ─────────────────
    # Utilisé uniquement si les 100 tentatives échouent (très rare)
    chemin = []
    y = LIGNES // 4                         # partie haute
    for x in range(0, COLS // 2):           # horizontal vers la droite
        chemin.append((x, y))
    for dy in range(y, LIGNES - y):         # vertical vers le bas
        chemin.append((COLS // 2, dy))
    y2 = LIGNES - y - 1                     # partie basse
    for x in range(COLS // 2, COLS):        # horizontal vers la droite
        chemin.append((x, y2))
    return chemin


def _segment_horizontal(x1, y, x2):
    """
    Crée un segment horizontal de cases sur une même ligne.
    
    Génère toutes les cases de (x1, y) à (x2, y) inclus.
    Fonctionne dans les deux sens (gauche→droite ou droite→gauche).
    
    Args:
        x1 (int) : colonne de départ
        y  (int) : ligne (fixe)
        x2 (int) : colonne d'arrivée
    
    Returns:
        list[tuple] : [(x1,y), (x1+1,y), ..., (x2,y)]
    """
    pas = 1 if x2 >= x1 else -1
    return [(x, y) for x in range(x1, x2 + pas, pas)]


def _segment_vertical(x, y1, y2):
    """
    Crée un segment vertical de cases sur une même colonne.
    
    Génère toutes les cases de (x, y1) à (x, y2) inclus.
    Fonctionne dans les deux sens (haut→bas ou bas→haut).
    
    Args:
        x  (int) : colonne (fixe)
        y1 (int) : ligne de départ
        y2 (int) : ligne d'arrivée
    
    Returns:
        list[tuple] : [(x,y1), (x,y1+1), ..., (x,y2)]
    """
    pas = 1 if y2 >= y1 else -1
    return [(x, y) for y in range(y1, y2 + pas, pas)]


# ════════════════════════════════════════════════════════════════════════
#  ZONES DE PLACEMENT
# ════════════════════════════════════════════════════════════════════════

def generer_zones_placement(chemin_set):
    """
    Détermine les zones de placement pour le défenseur.
    
    Règle simple : TOUTE case qui n'est PAS sur le chemin est une zone
    de placement. Le défenseur peut y poser ses tours.
    
    Args:
        chemin_set (set[tuple]) : ensemble des cases du chemin
    
    Returns:
        set[tuple] : ensemble de (colonne, ligne) des zones de placement
    """
    zones = set()
    for y in range(LIGNES):
        for x in range(COLS):
            if (x, y) not in chemin_set:
                zones.add((x, y))
    return zones


# ════════════════════════════════════════════════════════════════════════
#  CLASSE PLATEAU
# ════════════════════════════════════════════════════════════════════════

class Plateau:
    """
    Classe principale du plateau de jeu.
    
    Assemble tous les éléments : la grille, le chemin aléatoire,
    les bases et les zones de placement.
    
    Le plateau est créé UNE FOIS au début de la partie. Le chemin
    reste identique pendant toute la durée de la partie.
    
    Structure de la grille :
        self.grille[ligne][colonne] = type de case (VIDE, CHEMIN, BASE_ATK, etc.)
        ⚠ Attention : c'est grille[LIGNE][COL] et non grille[x][y]
    
    Attributs :
        grille (list[list[int]])    : matrice 2D des types de cases (LIGNES × COLS)
        chemin (list[tuple])        : liste ordonnée des cases du chemin [(col,lig), ...]
        chemin_set (set[tuple])     : même chose en set pour des recherches rapides O(1)
        zones_placement (set[tuple]): cases où le défenseur peut poser des tours
        base_attaquant (tuple)      : coordonnées (col, lig) de la base attaquant
        base_defenseur (tuple)      : coordonnées (col, lig) de la base défenseur
    """
    def __init__(self):
        # Initialiser la grille vide (toutes les cases à VIDE)
        self.grille = [[VIDE for _ in range(COLS)] for _ in range(LIGNES)]

        # Générer le chemin aléatoire en zigzag
        # ⚠ Fixé pour toute la durée de la partie (pas re-généré à chaque tour)
        self.chemin = generer_chemin()
        self.chemin_set = set(self.chemin)  # version set pour recherche rapide

        # Générer les zones de placement (= toutes les cases hors chemin)
        self.zones_placement = generer_zones_placement(self.chemin_set)

        # Les bases sont les extrémités du chemin
        self.base_attaquant = self.chemin[0]    # première case = bord gauche
        self.base_defenseur = self.chemin[-1]   # dernière case = bord droit

        # Remplir la grille avec les bons types de cases
        self._remplir_grille()

    def _remplir_grille(self):
        """
        Remplit la matrice self.grille avec les types de cases.
        
        Ordre d'écriture (les derniers écrasent les premiers) :
          1. Cases du chemin      → CHEMIN
          2. Zones de placement   → ZONE_PLACE (si pas déjà CHEMIN)
          3. Base attaquant       → BASE_ATK
          4. Base défenseur       → BASE_DEF
        """
        # 1) Marquer toutes les cases du chemin
        for (x, y) in self.chemin:
            self.grille[y][x] = CHEMIN

        # 2) Marquer les zones de placement (seulement si la case est encore VIDE)
        for (x, y) in self.zones_placement:
            if self.grille[y][x] == VIDE:
                self.grille[y][x] = ZONE_PLACE

        # 3-4) Marquer les bases (écrase le CHEMIN sur ces cases)
        bx, by = self.base_attaquant
        self.grille[by][bx] = BASE_ATK
        bx, by = self.base_defenseur
        self.grille[by][bx] = BASE_DEF

    def case_a(self, col, ligne):
        """
        Renvoie le type de la case aux coordonnées grille données.
        
        Args:
            col (int)   : numéro de colonne (0 à COLS-1)
            ligne (int) : numéro de ligne   (0 à LIGNES-1)
        
        Returns:
            int ou None : le type de case (VIDE, CHEMIN, etc.) ou None si hors limites
        """
        if 0 <= col < COLS and 0 <= ligne < LIGNES:
            return self.grille[ligne][col]
        return None

    def pixel_vers_case(self, px, py):
        """
        Convertit une position en pixels (ex: position de la souris)
        en coordonnées de la grille (colonne, ligne).
        
        Utile pour savoir sur quelle case l'utilisateur a cliqué.
        
        Args:
            px (int) : position X en pixels
            py (int) : position Y en pixels
        
        Returns:
            tuple(int,int) ou None : (colonne, ligne) ou None si clic hors grille
        """
        col = (px - MARGE_X) // TAILLE_CASE
        ligne = (py - MARGE_Y) // TAILLE_CASE
        if 0 <= col < COLS and 0 <= ligne < LIGNES:
            return (col, ligne)
        return None

    def case_vers_pixel(self, col, ligne):
        """
        Convertit des coordonnées grille en position pixel (coin haut-gauche de la case).
        
        Utile pour dessiner un rectangle à la bonne position.
        
        Args:
            col (int)   : numéro de colonne
            ligne (int) : numéro de ligne
        
        Returns:
            tuple(int,int) : (px, py) position du coin haut-gauche en pixels
        """
        px = MARGE_X + col * TAILLE_CASE
        py = MARGE_Y + ligne * TAILLE_CASE
        return (px, py)

    def case_vers_centre(self, col, ligne):
        """
        Convertit des coordonnées grille en position pixel (centre de la case).
        
        Utile pour dessiner un sprite ou un cercle centré dans la case.
        
        Args:
            col (int)   : numéro de colonne
            ligne (int) : numéro de ligne
        
        Returns:
            tuple(int,int) : (px, py) position du centre en pixels
        """
        px = MARGE_X + col * TAILLE_CASE + TAILLE_CASE // 2
        py = MARGE_Y + ligne * TAILLE_CASE + TAILLE_CASE // 2
        return (px, py)


# ════════════════════════════════════════════════════════════════════════
#  AFFICHAGE DU PLATEAU (PYGAME)
# ════════════════════════════════════════════════════════════════════════

# Dictionnaire qui associe chaque type de case à sa couleur d'affichage
# Utilisé par dessiner_plateau() pour colorier la grille
COULEURS_CASE = {
    VIDE:       (15, 20, 35),          # case vide (ne devrait pas apparaître)
    CHEMIN:     CHEMIN_OR,             # chemin que les attaquants suivent
    BASE_ATK:   ROUGE,                 # base attaquant (point de spawn)
    BASE_DEF:   BLEU,                  # base défenseur (à protéger)
    ZONE_PLACE: ZONE_VERT_D,           # zone de placement (vert cyberpunk sombre)
}


def dessiner_case_moderne(surface, px, py, type_case, taille=40):
    """Dessine une case avec rendu moderne 3D avec dégradés et ombres.
    Les cases du chemin sont dessinées sans bordures mais avec texture pour une apparence continue mais riche."""
    
    couleur_base = COULEURS_CASE.get(type_case, GRIS_SOMBRE)
    rect = pygame.Rect(px, py, taille, taille)
    
    # Ombre portée
    shadow_color = (0, 0, 0)
    shadow_rect = pygame.Rect(px + 2, py + 2, taille - 1, taille - 1)
    pygame.draw.rect(surface, shadow_color, shadow_rect)
    
    # Case principale
    pygame.draw.rect(surface, couleur_base, rect)
    
    # Effets visuels
    if type_case == CHEMIN:
        # Ombre légère en haut-gauche et relief en bas-droit pour le chemin
        pygame.draw.line(surface, (200, 160, 60), (px + 2, py + 2), (px + taille - 3, py + 2), 1)
        pygame.draw.line(surface, (200, 160, 60), (px + 2, py + 2), (px + 2, py + taille - 3), 1)
        pygame.draw.line(surface, (180, 120, 20), (px + taille - 3, py + 2), (px + taille - 3, py + taille - 3), 1)
        pygame.draw.line(surface, (180, 120, 20), (px + 2, py + taille - 3), (px + taille - 3, py + taille - 3), 1)
    else:
        # Bordure externe sombre
        pygame.draw.rect(surface, GRIS_MOYEN, rect, 2)
        
        # Bordure interne brillante (effet 3D)
        if type_case == ZONE_PLACE:
            pygame.draw.line(surface, ZONE_VERT_2, (px + 2, py + 2), (px + taille - 3, py + 2), 1)
            pygame.draw.line(surface, ZONE_VERT_2, (px + 2, py + 2), (px + 2, py + taille - 3), 1)
        elif type_case == BASE_ATK:
            pygame.draw.line(surface, ROUGE_CLAIR, (px + 2, py + 2), (px + taille - 3, py + 2), 1)
        elif type_case == BASE_DEF:
            pygame.draw.line(surface, BLEU_CLAIR, (px + 2, py + 2), (px + taille - 3, py + 2), 1)


def dessiner_plateau(surface, plateau, police_info=None, afficher_zones=True):
    """Dessine le plateau avec style moderne cyberpunk/gaming."""
    
    # Fond noir profond
    surface.fill(NOIR)
    
    # Motif de grille subtile en arrière-plan (cyberpunk) avec dégradé de couleur
    # Gradient vertical de bleu sombre à noir profond
    for y in range(0, HAUTEUR_FENETRE, 20):
        # Créer un gradient bleu→noir
        ratio = y / HAUTEUR_FENETRE
        couleur_gradient = (
            int(20 * (1 - ratio) + 8 * ratio),
            int(28 * (1 - ratio) + 12 * ratio),
            int(50 * (1 - ratio) + 25 * ratio)
        )
        pygame.draw.line(surface, couleur_gradient, (0, y), (LARGEUR_FENETRE, y), 1)
    
    # Motif vertical pour la grille
    for x in range(0, LARGEUR_FENETRE, 20):
        pygame.draw.line(surface, (12, 16, 32), (x, 0), (x, HAUTEUR_FENETRE), 1)
    
    # Ajouter une teinte légère de couleur au fond de la zone du jeu
    # Créer un rectangle semi-transparent avec une teinte bleuâtre
    fond_rect = pygame.Surface((LARGEUR_FENETRE, HAUTEUR_FENETRE))
    fond_rect.set_alpha(20)
    fond_rect.fill((20, 40, 80))  # Teinte bleu-foncé subtile
    surface.blit(fond_rect, (0, 0))

    # Cases modernes
    for ligne in range(LIGNES):
        for col in range(COLS):
            type_case = plateau.grille[ligne][col]
            if not afficher_zones and type_case == ZONE_PLACE:
                type_case = VIDE
            px, py = plateau.case_vers_pixel(col, ligne)
            dessiner_case_moderne(surface, px, py, type_case, TAILLE_CASE)

    # Chemin avec glow - CACHÉ (pas affiché)
    # La ligne du chemin est masquée pour garder une esthétique propre
    # if len(plateau.chemin) >= 2:
    #     # Tracer segment par segment, en remplissant les cases adjacentes
    #     for i in range(len(plateau.chemin) - 1):
    #         ... code masqué ...

    # Flèches directionnelles - MASQUÉES
    # for i in range(0, len(plateau.chemin) - 1, 3):
    #     cx, cy = plateau.case_vers_centre(*plateau.chemin[i])
    #     nx, ny = plateau.case_vers_centre(*plateau.chemin[i + 1])
    #     dx = (nx - cx) // 2
    #     dy = (ny - cy) // 2
    #     
    #     pygame.draw.circle(surface, CHEMIN_OR, (cx + dx, cy + dy), 5)
    #     pygame.draw.circle(surface, (255, 255, 100), (cx + dx, cy + dy), 7, 1)

    # Base attaquant - Carré rouge avec glow
    bx, by = plateau.case_vers_centre(*plateau.base_attaquant)
    # Glow progressif
    pygame.draw.circle(surface, (150, 30, 60), (bx, by), 25)
    pygame.draw.circle(surface, (200, 40, 80), (bx, by), 20)
    # Carré principal
    rect_atk = pygame.Rect(bx - 15, by - 15, 30, 30)
    pygame.draw.rect(surface, ROUGE, rect_atk)
    pygame.draw.rect(surface, ROUGE_CLAIR, rect_atk, 2)

    # Base défenseur - Carré bleu avec glow
    dx, dy = plateau.case_vers_centre(*plateau.base_defenseur)
    # Glow progressif
    pygame.draw.circle(surface, (30, 100, 150), (dx, dy), 25)
    pygame.draw.circle(surface, (40, 150, 200), (dx, dy), 20)
    # Carré principal
    rect_def = pygame.Rect(dx - 15, dy - 15, 30, 30)
    pygame.draw.rect(surface, BLEU, rect_def)
    pygame.draw.rect(surface, BLEU_CLAIR, rect_def, 2)

    # Légende moderne et élégante
    if police_info is None:
        police_info = pygame.font.Font(None, 19)

    legend_y = HAUTEUR_FENETRE - 40
    # Fond dégradé pour la légende
    legend_surface = pygame.Surface((LARGEUR_FENETRE, 40))
    legend_surface.fill((8, 12, 28))
    # Dégradé bleu subtil
    for i in range(40):
        ratio = i / 40
        couleur = (int(8 + 20 * ratio), int(12 + 30 * ratio), int(28 + 50 * ratio))
        pygame.draw.line(legend_surface, couleur, (0, i), (LARGEUR_FENETRE, i))
    surface.blit(legend_surface, (0, legend_y))
    
    # Bordures avec couleurs
    pygame.draw.line(surface, (70, 150, 255), (0, legend_y), (LARGEUR_FENETRE, legend_y), 2)
    pygame.draw.line(surface, (150, 80, 255), (0, HAUTEUR_FENETRE - 1), (LARGEUR_FENETRE, HAUTEUR_FENETRE - 1), 1)

    legende_items = [(CHEMIN_OR, "* Chemin"), (ROUGE, "* Base Attaquant"),
                      (BLEU, "* Base Defenseur")]
    if afficher_zones:
        legende_items.append((ZONE_VERT, "* Zone placement"))
    ly = legend_y + 10
    lx = MARGE_X + 15
    for couleur, texte in legende_items:
        label = police_info.render(texte, True, couleur)
        surface.blit(label, (lx, ly))
        lx += label.get_width() + 45

    # Titre ultra-moderne en blanc avec ombre subtile
    police_titre = pygame.font.Font(None, 38)
    titre_texte = "*** LEGENDS STRIKES — Plateau de jeu ***"
    
    # Ombre portée
    titre_ombre = police_titre.render(titre_texte, True, (100, 80, 180))
    titre_rect = titre_ombre.get_rect(center=(LARGEUR_FENETRE // 2 + 2, 17))
    surface.blit(titre_ombre, titre_rect)
    
    # Titre principal blanc
    titre = police_titre.render(titre_texte, True, BLANC)
    titre_rect = titre.get_rect(center=(LARGEUR_FENETRE // 2, 15))
    surface.blit(titre, titre_rect)
    
    # Ligne décorative sous le titre avec gradient
    pygame.draw.line(surface, (70, 150, 255), (LARGEUR_FENETRE // 2 - 170, 35), 
                     (LARGEUR_FENETRE // 2 + 170, 35), 3)
    pygame.draw.line(surface, (150, 80, 255), (LARGEUR_FENETRE // 2 - 170, 36), 
                     (LARGEUR_FENETRE // 2 + 170, 36), 1)



def dessiner_infos_partie(surface, joueur_atk, joueur_def, tour, police=None, afficher_stats_atk=True, afficher_stats_def=True):
    """Affiche le HUD moderne avec style gaming."""
    if police is None:
        police = pygame.font.Font(None, 28)
        police_petit = pygame.font.Font(None, 21)
    else:
        police_petit = pygame.font.Font(None, 21)

    hud_y = MARGE_Y - 40
    hud_height = 45
    
    # Fond dégradé pour le HUD avec bordures colorées
    hud_surface = pygame.Surface((LARGEUR_FENETRE, hud_height))
    # Dégradé bleu sombre → noir
    for i in range(hud_height):
        ratio = i / hud_height
        couleur = (
            int(10 + 15 * (1 - ratio)),
            int(15 + 20 * (1 - ratio)),
            int(30 + 40 * (1 - ratio))
        )
        pygame.draw.line(hud_surface, couleur, (0, i), (LARGEUR_FENETRE, i))
    surface.blit(hud_surface, (0, hud_y))
    
    # Bordures décoratives
    pygame.draw.line(surface, (70, 150, 255), (0, hud_y), (LARGEUR_FENETRE, hud_y), 2)
    pygame.draw.line(surface, (150, 80, 255), (0, hud_y + hud_height - 1), (LARGEUR_FENETRE, hud_y + hud_height - 1), 1)

    # Attaquant - Côté gauche avec accent rouge
    txt_atk_nom = police.render(f">> {joueur_atk.nom}", True, ROUGE)
    if afficher_stats_atk:
        txt_atk_stats = police_petit.render(f"Or: {joueur_atk.or_disponible} | Unites: {len(joueur_atk.unites)}", True, ROUGE_CLAIR)
    else:
        txt_atk_stats = police_petit.render("Or: -- | Unites: --", True, ROUGE_CLAIR)
    surface.blit(txt_atk_nom, (MARGE_X + 15, hud_y + 5))
    surface.blit(txt_atk_stats, (MARGE_X + 15, hud_y + 25))
    
    # Ligne décorative sous attaquant
    pygame.draw.line(surface, ROUGE, (MARGE_X + 10, hud_y + 42), (MARGE_X + 240, hud_y + 42), 1)

    # Défenseur - Côté droit avec accent bleu
    txt_def_nom = police.render(f"{joueur_def.nom} <<", True, BLEU_CLAIR)
    if afficher_stats_def:
        txt_def_stats = police_petit.render(f"Or: {joueur_def.or_disponible} | Tours: {len(joueur_def.unites)}", True, BLEU_CLAIR)
    else:
        txt_def_stats = police_petit.render("Or: -- | Tours: --", True, BLEU_CLAIR)
    surface.blit(txt_def_nom, (LARGEUR_FENETRE - MARGE_X - txt_def_nom.get_width() - 15, hud_y + 5))
    surface.blit(txt_def_stats, (LARGEUR_FENETRE - MARGE_X - txt_def_stats.get_width() - 15, hud_y + 25))
    
    # Ligne décorative sous défenseur
    pygame.draw.line(surface, BLEU, (LARGEUR_FENETRE - MARGE_X - 240, hud_y + 42), (LARGEUR_FENETRE - MARGE_X - 10, hud_y + 42), 1)

    # Numéro de tour au centre sans glow
    txt_tour = police.render(f"TOUR {tour}", True, OR_ACCENT)
    tour_ombre = pygame.font.Font(None, 28)
    txt_tour_ombre = tour_ombre.render(f"TOUR {tour}", True, (100, 80, 20))
    tour_rect = txt_tour.get_rect(center=(LARGEUR_FENETRE // 2, hud_y + 20))
    
    surface.blit(txt_tour_ombre, (tour_rect.x + 2, tour_rect.y + 2))
    surface.blit(txt_tour, tour_rect)

