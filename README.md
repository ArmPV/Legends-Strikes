# Legends-Strikes

# Tower Defense Asymétrique : Duel Stratégique

## Prérequis
Avant de lancer le projet, assurez‑vous d’avoir :
- **Python** installé
- **Pygame** installé (`pip install pygame`)

## Lancement du projet

1. Ouvrir le dossier du projet  
2. Ouvrir un terminal dans ce dossier  
3. Lancer le fichier avec la commande :

```bash
python main.py
```

## Description du projet

Ce projet est une version originale d’un **Tower Defense** en mode 1 contre 1.  

- Un joueur incarne l’**Attaquant**, qui envoie des vagues de créatures. 
- L’autre joueur incarne le **Défenseur**, qui place et améliore des tours.  

Le jeu se termine par :  
- **Victoire de l’Attaquant** : si la base du Défenseur tombe à 0 PV  
- **Victoire du Défenseur** : si l’Attaquant n’a plus assez de monnaie pour lancer une nouvelle vague  


## Plateau de jeu

- Plateau rectangulaire  
- Point de départ : base de l’Attaquant (en haut)  
- Point d’arrivée : base du Défenseur (en bas)  
- Chemin fixe reliant les bases
- Zones de placement pour les tours


## Vision partielle

- **Attaquant** : ne voit que l’emplacement des tours, pas leurs types, niveaux ou effets  
- **Défenseur** : voit l’avancée des créatures une fois la vague lancée, mais pas leur composition exacte avant envoi  


## Phases de jeu

### Phase de préparation (Attaquant)
- Composition d’une vague de créatures avec les ressources disponibles  
- Ajout possible de **bonus** ou **effets globaux** sur la vague

### Phase de défense
- Placement et amélioration de tours par le Défenseur  
- Résolution en temps réel des attaques et des effets  
- Les créatures détruites rapportent des ressources au Défenseur et à l’Attaquant selon l’endroit et les conditions


## Économie du jeu

- **Défenseur** : gagne des ressources pour chaque créature détruite  
- **Attaquant** : gagne des ressources pour les créatures survivantes ou atteignant certains points, ou par revenu fixe par tour


## Créatures

Chaque créature possède :
- PV, vitesse, coût  
- Capacités spéciales : invisibilité, destruction de tours, etc.  
- Bonus temporaires : armure, immunités, etc.


## Tours de défense

Chaque tour possède :
- Effets variés : dégâts, contrôle, détection  
- Mécaniques d’amélioration  
- Coûts équilibrés  


## Déroulé d’une partie

Le jeu se déroule par **tours**, chaque tour comprenant plusieurs étapes :

1. **Phase de préparation**  
   L’Attaquant prépare sa vague de créatures et peut appliquer des bonus ou effets globaux.

2. **Phase de défense**  
   Le Défenseur place ses tours ou améliore celles déjà en place pour se préparer à l’attaque.

3. **Résolution de la vague**  
   La vague de créatures avance sur le plateau, les tours infligent des dégâts et appliquent leurs effets. Les ressources sont attribuées aux deux joueurs selon les résultats (créatures détruites ou atteignant certains points).

4. **Vague suivante**  
   Les joueurs peuvent décider de lancer une nouvelle vague et répéter les phases de préparation, défense et résolution.

5. **Fin de la partie**  
   La partie se termine lorsque la base du Défenseur atteint 0 PV (victoire de l’Attaquant) ou lorsque l’Attaquant n’a plus assez de ressources pour lancer une nouvelle vague (victoire du Défenseur). Le score est donc affiché.

## Structure du projet
Legends-Strikes/
│
├── main.py
├── README.md
├── image/                     # Ressources graphiques
│
├── 1e_contribution/           # Documents de conception et première contribution
│   ├── 1e_contribution_Tower_Defense.pdf
│   ├── diagramme_activité.png
│   ├── diagramme_cas_utilisation.png
│   ├── diagramme_classe.png
│   ├── diagramme_sequence.png
│   └── journal_git.txt
│
└── game/                      # Code source du jeu
    ├── board.py
    ├── creatures.py
    ├── effects.py
    ├── init.py
    ├── path.py
    ├── players.py
    ├── towers.py
    ├── turnPlayer.py
    ├── utils.py
    ├── vision.py
    └── wave.py


## Équipe
20231925 NARAYANASSAMYCHETTIAR VISWADEVI

20245194 MEZEGHRANE ZINEDDINE

20233004 PLUVINET-VIAENE ARMAND

20230692 NGUARA NGOMA MARC

## État actuel
- Interface graphique
- Mettre en ligne
- Améliorer toute les fonctionnalités
- Effets spéciaux et bonus avancés
- Ajout des animations


