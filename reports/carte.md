# Carte de reproductibilité – R4 (J1)

Article : Zheng et Lu 2017, J. Neural Eng. 14 026017. Pour chaque information : page / section / tableau.

## 0. Type de reproduction visé

À compléter avec la fiche R4 (fidèle / partielle / conceptuelle) et la justification.

## 1. Résultat à reproduire

À confirmer avec la fiche R4. Candidats dans l'article :

- Tableau 3 (p. 9) : EEG seul, COR / RMSE par zone et par type de DE.
- Tableau 2 (p. 9) : EOG frontal seul, COR / RMSE par méthode de séparation.
- Section 3.3 (p. 11) : montage frontal, SVR 0,83 / 0,10 ; CCRF 0,84 / 0,10 ; CCNF 0,85 / 0,09.

Protocole : intra-sujet, 885 fenêtres de 8 s par expérience, 5 sessions, validation croisée 5 plis (section 2.4, p. 7).

## 2. Données

- Nom et version : SEED-VIG
- Fichier téléchargé et ouvert : oui / non
- Taille : environ 2 Go
- Licence : usage académique, pas de redistribution hors du cours

## 3. Pipeline

| Étape | Dans l'article | Notre choix, s'il manque une information |
| --- | --- | --- |
| Sujets, sessions, exclusions | Décrit : 23 sujets, environ 2 h (2.1, p. 3) ; aucune exclusion mentionnée | |
| Unité d'observation | Décrit : fenêtre de 8 s sans recouvrement, 885 par expérience (2.3, 2.4) | |
| Cible et labels | Décrit : PERCLOS continu, lunettes SMI (2.2, p. 4) | |
| Prétraitement et artefacts | Décrit : EEG 1–75 Hz, 200 Hz ; EOG ICA / soustraction (2.3) | Features fournies par SEED-VIG |
| Features et normalisation | Features décrites (DE 2 Hz / 5 bandes, 36 EOG) ; normalisation absente | StandardScaler appris sur l'apprentissage |
| Modèle et hyperparamètres | SVR RBF, grid search c et g (2.4) ; grille absente | Grille et réglage interne à préciser |
| Découpage apprentissage / test | Incomplet : 5 sessions et 5 plis, contiguïté non précisée | 5 blocs contigus dans le temps |
| Métrique et agrégation | Décrit : RMSE, COR sur les 5 sessions concaténées (2.4, p. 7) | Moyenne et écart-type sur les sujets |

## 4. Ce qui ne doit jamais passer de l'apprentissage au test

- Fenêtres voisines dans le temps (forte autocorrélation) : découpage par blocs contigus.
- Normalisation, sélection et réglage des hyperparamètres : appris sur l'apprentissage seulement.
- Lissage temporel des features (ex. moyenne mobile, LDS) : vérifier s'il utilise des fenêtres futures ou de test.

## 5. Première baseline et temps de calcul

À compléter après `python src/baselines.py --modalities eog --max-subjects 1`.

## 6. Plan B

À compléter avec la fiche R4.
