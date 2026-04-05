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

## Système de Ressources

Le système de ressources a été ajusté pour équilibrer le duel entre l’Attaquant et le Défenseur.
Les gains dépendent désormais **de l’avancée des créatures sur le chemin.**
1. **Suppression du bonus fixe du Défenseur**

- Le bonus automatique de **+40 crédits** en fin de vague a été retiré.

- Si le Défenseur ne tue aucune créature, il ne gagne **aucune ressource.**

2. **Récompense dynamique selon la position de mort**

Chaque créature tuée rapporte des crédits au Défenseur, mais le montant dépend de l’endroit où elle meurt.

Le chemin est découpé en **3 zones** :

- **Zone 1** : début du chemin (avant le 5ᵉ point)

- **Zone 2** : milieu (entre le 5ᵉ et le 9ᵉ point)

- **Zone 3** : fin du chemin (après le 9ᵉ point)

3. **Coefficients appliqués à la récompense**

Chaque créature possède une reward de base.
On applique un coefficient selon la zone où elle meurt :

- **Zone 1** : Début : **65%** de la reward
- **Zone 2** : Milieu : **40%** de la reward
- **Zone 3** : Fin : **20%** de la reward

Les créatures fortes rapportent toujours plus que les faibles, mais les gains ont été nerfés pour éviter que le Défenseur snowball trop vite.

4. **Récompenses pour l’Attaquant**

L’Attaquant gagne aussi des ressources selon la survie de ses créatures :

- **Si une créature atteint la base :**
    → l’Attaquant gagne **100%** de sa reward habituelle

- **Si elle meurt en Zone 3 :**
    → l’Attaquant gagne **50%** de sa reward

- **Si elle meurt en Zone 1 ou 2 :**
    → l’Attaquant ne gagne **rien**

5. **Cas particulier : créatures invoquées**

Les créatures invoquées par le summoner :

- rapportent **moins** de ressources au Défenseur

- infligent **moins** de dégâts à la base

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

## Structure du projet

```text
Legends-Strikes/
│
├── main.py                 # Lance le jeu
├── README.md               # Documentation du projet
├── repartition_effective.pdf
├── journalgit.txt          # Journal Git récapitulatif
├── .gitignore              # Fichiers à ignorer par Git
├── assets/                 # Images, polices, musiques, sprites du jeu
│
├── 1e_contribution/        # Documents de conception et première contribution (UML, rapport, journal Git)
│   ├── 1e_contribution_Tower_Defense.pdf
│   ├── diagramme_activité.png
│   ├── diagramme_cas_utilisation.png
│   ├── diagramme_classe.png
│   ├── diagramme_sequence.png
│   └── journal_git.txt
│
└── game/                   # Code source du jeu
    ├── _init_.py           # Déclare le module
    ├── assets.py           # Chargement des ressources
    ├── board.py            # Plateau de jeu
    ├── constants.py        # Constantes globales
    ├── creatures.py        # Créatures et comportements
    ├── effects.py          # Effets globaux et bonus
    ├── path.py             # Chemin et zones
    ├── players.py          # Attaquant / Défenseur
    ├── towers.py           # Tours et améliorations
    ├── turnPlayer.py       # Gestion des tours de jeu
    ├── ui.py               # Interface utilisateur
    ├── utils.py            # Fonctions utilitaires
    ├── vision.py           # Portée et visibilité
    └── wave.py             # Gestion des vagues
```


## Équipe
20231925 NARAYANASSAMYCHETTIAR VISWADEVI

20245194 MEZEGHRANE ZINEDDINE

20233004 PLUVINET-VIAENE ARMAND

20230692 NGUARA NGOMA MARC

## État actuel
Le jeu est en cours de développement.
Les prochaines étapes possibles :

- Interface graphique
- Mettre en ligne
- Améliorer toute les fonctionnalités
- Effets spéciaux et bonus avancés
- Ajout des animations


