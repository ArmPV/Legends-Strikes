import pygame
import sys

# Initialisation de Pygame
pygame.init()

# Configuration de la fenêtre
LARGEUR = 800
HAUTEUR = 600
ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Legends Strikes - Menu")

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

class Bouton:
    def __init__(self, x, y, largeur, hauteur, texte, couleur, couleur_survol):
        self.rect = pygame.Rect(x, y, largeur, hauteur)
        self.texte = texte
        self.couleur = couleur
        self.couleur_survol = couleur_survol
        self.est_survole = False
    
    def dessiner(self, surface):
        couleur = self.couleur_survol if self.est_survole else self.couleur
        pygame.draw.rect(surface, couleur, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLANC, self.rect, 3, border_radius=10)
        
        texte_surface = police.render(self.texte, True, BLANC)
        texte_rect = texte_surface.get_rect(center=self.rect.center)
        surface.blit(texte_surface, texte_rect)
    
    def verifier_survol(self, pos):
        self.est_survole = self.rect.collidepoint(pos)
        return self.est_survole
    
    def est_clique(self, pos, clic):
        return self.rect.collidepoint(pos) and clic

# Création des boutons
largeur_bouton = 250
hauteur_bouton = 60
x_centre = LARGEUR // 2 - largeur_bouton // 2

bouton_jouer = Bouton(x_centre, 250, largeur_bouton, hauteur_bouton, "Jouer", BLEU, BLEU_SURVOL)
bouton_parametres = Bouton(x_centre, 350, largeur_bouton, hauteur_bouton, "Paramètres", BLEU, BLEU_SURVOL)
bouton_quitter = Bouton(x_centre, 450, largeur_bouton, hauteur_bouton, "Quitter", BLEU, BLEU_SURVOL)

boutons = [bouton_jouer, bouton_parametres, bouton_quitter]

# Boucle principale
clock = pygame.time.Clock()
en_cours = True

while en_cours:
    pos_souris = pygame.mouse.get_pos()
    clic = False
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            en_cours = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                clic = True
    
    # Vérifier les survols et clics
    for bouton in boutons:
        bouton.verifier_survol(pos_souris)
    
    if bouton_jouer.est_clique(pos_souris, clic):
        print("Jouer cliqué !")
    
    if bouton_parametres.est_clique(pos_souris, clic):
        print("Paramètres cliqué !")
    
    if bouton_quitter.est_clique(pos_souris, clic):
        en_cours = False
    
    # Dessiner
    ecran.fill(NOIR)
    
    # Titre
    titre = police_titre.render("Legends Strikes", True, BLANC)
    titre_rect = titre.get_rect(center=(LARGEUR // 2, 100))
    ecran.blit(titre, titre_rect)
    
    # Boutons
    for bouton in boutons:
        bouton.dessiner(ecran)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()