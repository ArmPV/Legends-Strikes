import pygame
import sys

# Initialisation de Pygame
pygame.init()

# Configuration de la fenêtre
LARGEUR = 800
HAUTEUR = 600
ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Legends Strikes")

# Couleurs
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
GRIS = (100, 100, 100)
GRIS_CLAIR = (150, 150, 150)
BLEU = (50, 100, 200)
BLEU_SURVOL = (70, 130, 230)

# Police
police = pygame.font.Font(None, 50)
police_titre = pygame.font.Font(None, 80)


# Classe Bouton
class Bouton:
    def __init__(self, x, y, largeur, hauteur, texte, couleur, couleur_survol):
        self.rect = pygame.Rect(x, y, largeur, hauteur)
        self.texte = texte
        self.couleur = couleur
        self.couleur_survol = couleur_survol
        self.est_survole = False
    
    def dessiner(self, surface):
        # Change la couleur si la souris survole
        couleur = self.couleur_survol if self.est_survole else self.couleur
        
        # Dessine le bouton
        pygame.draw.rect(surface, couleur, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLANC, self.rect, 3, border_radius=10)
        
        # Dessine le texte
        texte_surface = police.render(self.texte, True, BLANC)
        texte_rect = texte_surface.get_rect(center=self.rect.center)
        surface.blit(texte_surface, texte_rect)
    
    def verifier_survol(self, pos):
        self.est_survole = self.rect.collidepoint(pos)
    
    def est_clique(self, pos, clic):
        return self.rect.collidepoint(pos) and clic


# Fonction pour afficher le plateau
def afficher_plateau(surface, lignes=15, colonnes=20, taille_case=40):
    # Dessine une grille simple
    for y in range(lignes):
        for x in range(colonnes):
            rect = pygame.Rect(x * taille_case, y * taille_case, taille_case, taille_case)
            pygame.draw.rect(surface, GRIS_CLAIR, rect, 1)


# Fonction pour afficher la fenêtre de confirmation
def afficher_confirmation(surface):
    # Fond sombre transparent
    overlay = pygame.Surface((LARGEUR, HAUTEUR))
    overlay.set_alpha(180)
    overlay.fill(NOIR)
    surface.blit(overlay, (0, 0))

    # Boîte de dialogue
    # (x=150, y=200, largeur=550, hauteur=200)
    pygame.draw.rect(surface, GRIS, (150, 200, 500, 200), border_radius=15)
    pygame.draw.rect(surface, BLANC, (150, 200, 500, 200), 3, border_radius=15)

    # Texte
    texte = police.render("Êtes-vous sûr de quitter ?", True, BLANC)
    surface.blit(texte, (LARGEUR//2 - texte.get_width()//2, 230))

    # Boutons Oui / Non
    bouton_oui.dessiner(surface)
    bouton_non.dessiner(surface)


# Boutons du menu
largeur_bouton = 250
hauteur_bouton = 60
x_centre = LARGEUR // 2 - largeur_bouton // 2

bouton_jouer = Bouton(x_centre, 250, largeur_bouton, hauteur_bouton, "Jouer", BLEU, BLEU_SURVOL)
bouton_parametres = Bouton(x_centre, 350, largeur_bouton, hauteur_bouton, "Paramètres", BLEU, BLEU_SURVOL)
bouton_menu_quitter = Bouton(x_centre, 450, largeur_bouton, hauteur_bouton, "Quitter", BLEU, BLEU_SURVOL)

boutons_menu = [bouton_jouer, bouton_parametres, bouton_menu_quitter]

# Bouton Quitter sur le plateau
bouton_quitter_plateau = Bouton(650, 520, 120, 50, "Quitter", BLEU, BLEU_SURVOL)

# Boutons de confirmation
bouton_oui = Bouton(300, 320, 100, 50, "Oui", BLEU, BLEU_SURVOL)
bouton_non = Bouton(420, 320, 100, 50, "Non", BLEU, BLEU_SURVOL)

# États
clock = pygame.time.Clock()
en_cours = True
afficher_menu = True
confirmation_quitter = False


# Boucle principale
while en_cours:
    pos_souris = pygame.mouse.get_pos()
    clic = False
    
    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            en_cours = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            clic = True

    # Si la fenêtre de confirmation est ouverte
    if confirmation_quitter:
        bouton_oui.verifier_survol(pos_souris)
        bouton_non.verifier_survol(pos_souris)

        if bouton_oui.est_clique(pos_souris, clic):
            en_cours = False

        if bouton_non.est_clique(pos_souris, clic):
            confirmation_quitter = False

        afficher_confirmation(ecran)
        pygame.display.flip()
        clock.tick(60)
        continue


    # MENU PRINCIPAL
    if afficher_menu:
        for bouton in boutons_menu:
            bouton.verifier_survol(pos_souris)

        if bouton_jouer.est_clique(pos_souris, clic):
            afficher_menu = False

        if bouton_menu_quitter.est_clique(pos_souris, clic):
            confirmation_quitter = True

        ecran.fill(NOIR)

        titre = police_titre.render("Legends Strikes", True, BLANC)
        titre_rect = titre.get_rect(center=(LARGEUR // 2, 100))
        ecran.blit(titre, titre_rect)

        for bouton in boutons_menu:
            bouton.dessiner(ecran)

    # PLATEAU
    else:
        ecran.fill(NOIR)
        afficher_plateau(ecran)

        # Bouton quitter sur le plateau
        bouton_quitter_plateau.verifier_survol(pos_souris)
        bouton_quitter_plateau.dessiner(ecran)

        if bouton_quitter_plateau.est_clique(pos_souris, clic):
            confirmation_quitter = True

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
