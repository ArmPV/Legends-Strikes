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


# ══════════════════════════════════════════════════════════════════════════
#  CONSTANTES DU PLATEAU
# ══════════════════════════════════════════════════════════════════════════

# Taille de la fenêtre Pygame quand on affiche le plateau de jeu
# (différente de la fenêtre du menu qui fait 800×600)
LARGEUR_FENETRE = 1000   # largeur en pixels
HAUTEUR_FENETRE = 700    # hauteur en pixels

# Dimensions de la grille de jeu
COLS = 20                # nombre de colonnes  (axe horizontal)
LIGNES = 14              # nombre de lignes    (axe vertical)
TAILLE_CASE = 40         # taille d'une case en pixels (carré 40×40)

# Marges calculées automatiquement pour centrer la grille dans la fenêtre
# Exemple : (1000 - 20*40) / 2 = 100 pixels de marge de chaque côté
MARGE_X = (LARGEUR_FENETRE - COLS * TAILLE_CASE) // 2
MARGE_Y = (HAUTEUR_FENETRE - LIGNES * TAILLE_CASE) // 2

# ── Couleurs (tuples RGB) ──────────────────────────────────────────────
# Utilisées partout dans l'affichage Pygame pour dessiner les cases,
# le texte, les symboles de bases, etc.
BLANC       = (255, 255, 255)
NOIR        = (0, 0, 0)
GRIS        = (40, 40, 40)       # bordures des cases
GRIS_CASE   = (30, 30, 30)       # fond des cases vides (inutilisé maintenant)
VERT        = (34, 180, 34)
VERT_CLAIR  = (100, 200, 100)
ROUGE       = (200, 50, 50)      # base attaquant + texte attaquant
BLEU        = (50, 100, 200)     # base défenseur
BLEU_CLAIR  = (100, 160, 255)    # texte défenseur dans le HUD
JAUNE       = (240, 200, 50)     # ligne du chemin + numéro de tour
ORANGE      = (230, 130, 30)
MARRON      = (100, 70, 40)      # couleur des cases du chemin
VIOLET      = (130, 60, 180)

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
    """
    def __init__(self, nom, role, or_initial=100):
        self.nom = nom
        self.role = role              # "attaquant" ou "defenseur"
        self.or_disponible = or_initial
        self.unites = []              # unités achetées et placées/envoyées

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
    VIDE:       GRIS_CASE,       # case vide (ne devrait pas apparaître)
    CHEMIN:     MARRON,          # chemin que les attaquants suivent
    BASE_ATK:   ROUGE,           # base attaquant (point de spawn)
    BASE_DEF:   BLEU,            # base défenseur (à protéger)
    ZONE_PLACE: (25, 50, 25),    # zone de placement (vert foncé)
}


def dessiner_plateau(surface, plateau, police_info=None):
    """
    Dessine le plateau de jeu complet sur la surface Pygame.
    
    Dessine dans l'ordre :
      1. Le fond noir
      2. Chaque case de la grille (colorée selon son type)
      3. La ligne jaune du chemin (pour bien visualiser le parcours)
      4. Des points directionnels sur le chemin (indiquent le sens)
      5. Les symboles des bases (▶ pour ATK, ✚ pour DEF)
      6. La légende en bas de l'écran
      7. Le titre en haut
    
    Args:
        surface (pygame.Surface) : surface sur laquelle dessiner (l'écran)
        plateau (Plateau)        : instance du plateau de jeu
        police_info (Font, opt)  : police pour la légende (créée si None)
    """
    # 1) Fond noir
    surface.fill(NOIR)

    # ── 2) Dessiner chaque case de la grille ────────────────────────
    # On parcourt toutes les cases et on dessine un rectangle coloré
    for ligne in range(LIGNES):
        for col in range(COLS):
            type_case = plateau.grille[ligne][col]
            couleur = COULEURS_CASE.get(type_case, GRIS_CASE)
            px, py = plateau.case_vers_pixel(col, ligne)
            rect = pygame.Rect(px, py, TAILLE_CASE, TAILLE_CASE)
            pygame.draw.rect(surface, couleur, rect)       # case remplie
            pygame.draw.rect(surface, GRIS, rect, 1)       # bordure fine

    # ── 3) Tracer la ligne jaune du chemin ──────────────────────────
    # On relie les centres de chaque case du chemin par une ligne continue
    # Cela aide à visualiser le parcours des attaquants
    if len(plateau.chemin) >= 2:
        points = [plateau.case_vers_centre(c, l) for (c, l) in plateau.chemin]
        pygame.draw.lines(surface, JAUNE, False, points, 3)  # épaisseur 3px

    # ── 4) Points directionnels sur le chemin ───────────────────────
    # Petits cercles jaunes tous les 3 cases pour indiquer le sens de marche
    for i in range(0, len(plateau.chemin) - 1, 3):
        cx, cy = plateau.case_vers_centre(*plateau.chemin[i])
        nx, ny = plateau.case_vers_centre(*plateau.chemin[i + 1])
        dx = nx - cx
        dy = ny - cy
        mid_x = cx + dx // 2  # point au milieu entre 2 cases
        mid_y = cy + dy // 2
        pygame.draw.circle(surface, JAUNE, (mid_x, mid_y), 3)

    # ── 5) Symboles des bases ───────────────────────────────────────
    # Base attaquant : triangle blanc (▶) = direction d'attaque
    bx, by = plateau.case_vers_centre(*plateau.base_attaquant)
    pygame.draw.polygon(surface, BLANC, [
        (bx - 10, by - 10), (bx + 12, by), (bx - 10, by + 10)
    ])
    # Base défenseur : croix dans un carré (bouclier/forteresse)
    dx, dy = plateau.case_vers_centre(*plateau.base_defenseur)
    pygame.draw.rect(surface, BLANC, (dx - 10, dy - 10, 20, 20), 3)  # carré
    pygame.draw.line(surface, BLANC, (dx - 6, dy), (dx + 6, dy), 2)  # croix H
    pygame.draw.line(surface, BLANC, (dx, dy - 6), (dx, dy + 6), 2)  # croix V

    # ── 6) Légende en bas de l'écran ────────────────────────────────
    if police_info is None:
        police_info = pygame.font.Font(None, 22)

    # Liste des éléments de légende : (couleur, texte)
    legende_items = [
        (MARRON,       "Chemin"),
        (ROUGE,        "Base Attaquant"),
        (BLEU,         "Base Défenseur"),
        ((25, 50, 25), "Zone de placement"),
    ]
    ly = HAUTEUR_FENETRE - 30   # position Y de la légende
    lx = MARGE_X                # position X de départ
    for couleur, texte in legende_items:
        # Petit carré coloré + texte à côté
        pygame.draw.rect(surface, couleur, (lx, ly, 14, 14))
        pygame.draw.rect(surface, BLANC, (lx, ly, 14, 14), 1)
        label = police_info.render(texte, True, BLANC)
        surface.blit(label, (lx + 18, ly - 1))
        lx += label.get_width() + 35  # espacement entre les items

    # ── 7) Titre centré en haut ─────────────────────────────────────
    police_titre = pygame.font.Font(None, 30)
    titre = police_titre.render("LEGENDS STRIKES — Plateau de jeu", True, BLANC)
    surface.blit(titre, (LARGEUR_FENETRE // 2 - titre.get_width() // 2, 8))


def dessiner_infos_partie(surface, joueur_atk, joueur_def, tour, police=None):
    """
    Affiche le HUD (Head-Up Display) avec les infos des joueurs et le tour.
    
    Affiché juste au-dessus de la grille :
      - À gauche  : nom de l'attaquant, son or, nombre d'unités (en rouge)
      - Au centre : numéro du tour actuel (en jaune)
      - À droite  : nom du défenseur, son or, nombre de tours posées (en bleu)
    
    Args:
        surface (pygame.Surface) : surface sur laquelle dessiner
        joueur_atk (Joueur)      : le joueur attaquant
        joueur_def (Joueur)      : le joueur défenseur
        tour (int)               : numéro du tour actuel
        police (Font, opt)       : police pour le texte (créée si None)
    """
    if police is None:
        police = pygame.font.Font(None, 24)

    # ── Infos attaquant (à gauche, en rouge) ────────────────────────
    txt_atk = police.render(
        f"⚔ {joueur_atk.nom}  Or: {joueur_atk.or_disponible}  Unités: {len(joueur_atk.unites)}",
        True, ROUGE
    )
    surface.blit(txt_atk, (MARGE_X, MARGE_Y - 25))

    # ── Infos défenseur (à droite, en bleu) ─────────────────────────
    txt_def = police.render(
        f"🛡 {joueur_def.nom}  Or: {joueur_def.or_disponible}  Tours: {len(joueur_def.unites)}",
        True, BLEU_CLAIR
    )
    surface.blit(txt_def, (LARGEUR_FENETRE - MARGE_X - txt_def.get_width(), MARGE_Y - 25))

    # ── Numéro du tour (centré, en jaune) ───────────────────────────
    txt_tour = police.render(f"Tour {tour}", True, JAUNE)
    surface.blit(txt_tour, (LARGEUR_FENETRE // 2 - txt_tour.get_width() // 2, MARGE_Y - 25))
