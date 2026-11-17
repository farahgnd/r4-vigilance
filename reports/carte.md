# Carte de reproductibilité – R4 (J1)

Article : Zheng et Lu 2017, J. Neural Eng. 14 026017. Pour chaque information : page / section / tableau.
Les informations « données » ci-dessous viennent de l'exploration réelle (`src/explore.py`, `src/verifier_donnees.py`, inventaire dans `results/inventaire.csv`) et de `Readme_English.txt` fourni avec SEED-VIG. Le PDF de l'article n'est pas dans le dépôt : les numéros de page sont ceux déjà notés par l'équipe, à revérifier sur le PDF.

## 0. Type de reproduction visé

À compléter avec la fiche R4 (fidèle / partielle / conceptuelle) et la justification.
**Question ouverte** : nous n'avons pas la fiche R4 dans le dépôt.

## 1. Résultat à reproduire

À confirmer avec la fiche R4. Candidats dans l'article :

- Tableau 3 (p. 9) : EEG seul, COR / RMSE par zone et par type de DE.
- Tableau 2 (p. 9) : EOG frontal seul, COR / RMSE par méthode de séparation.
- Section 3.3 (p. 11) : montage frontal, SVR 0,83 / 0,10 ; CCRF 0,84 / 0,10 ; CCNF 0,85 / 0,09.

Protocole : intra-sujet, 885 fenêtres de 8 s par expérience, 5 sessions, validation croisée 5 plis (section 2.4, p. 7).

## 2. Données

- Nom et version : SEED-VIG (fourni avec `Readme_English.txt`, 23 expériences).
- Fichier téléchargé et ouvert : **oui** (archive `SEED-VIG.zip`, dossier extrait dans `C:/Users/WIN11/Downloads/SEED-VIG/SEED-VIG`, hors du dépôt).
- Taille : **environ 3 Go** extraits (3,1 Go pour l'archive). Le README du projet disait 2 Go : information corrigée.
- Licence : usage académique, pas de redistribution hors du cours.
- Contrôles (étape 1, sur les 23 expériences) :
  - 885 fenêtres par expérience, pour toutes les modalités et pour les labels ;
  - aucune valeur manquante ni infinie ;
  - PERCLOS dans [0,0221 ; 1,0000] : cohérent avec l'intervalle 0–1 annoncé ;
  - les 23 fichiers sont présents dans tous les dossiers utilisés.

### Formes réelles des features

| Modalité (dossier) | Forme `.mat` | Ordre des axes (Readme) | Colonnes après mise à plat |
| --- | --- | --- | --- |
| EEG 2 Hz (`EEG_Feature_2Hz`, clé `de_movingAve`) | 17 × 885 × 25 | canal × fenêtre × bande (2 Hz) | 17 × 25 = **425** |
| EEG 5 bandes (`EEG_Feature_5Bands`, `de_movingAve`) | 17 × 885 × 5 | canal × fenêtre × bande (δ, θ, α, β, γ) | 17 × 5 = **85** |
| EOG (`EOG_Feature`, `features_table_icav_minh`) | 885 × 36 | fenêtre × feature | **36** |
| EEG frontal 2 Hz (`Forehead_EEG/EEG_Feature_2Hz`) | 4 × 885 × 25 | idem | 4 × 25 = **100** |
| EEG frontal 5 bandes (`Forehead_EEG/EEG_Feature_5Bands`) | 4 × 885 × 5 | idem | 4 × 5 = **20** |
| Labels (`perclos_labels`, clé `perclos`) | 885 × 1 | fenêtre | 1 |

- **Correction faite** : `_to_2d` (src/data.py) choisissait l'axe des fenêtres avec `argmax`. Ça donnait le bon résultat ici (885 est le plus grand axe), mais c'était une devinette. L'axe 1 est maintenant explicite, comme le documente le Readme.
- Zones EEG (Readme) : canaux 1–5 = temporaux, canaux 7–17 = postérieurs. **Le canal 6 n'est pas attribué dans le Readme** : à clarifier avant de définir les zones de l'étape 2.
- Le dossier `Forehead_EEG` a 4 canaux frontaux : c'est le montage « frontal » de l'article.
- Les EOG ont trois variantes (`features_table_ica`, `features_table_minus`, `features_table_icav_minh`) : séparation VEO/HEO par ICA, par soustraction, ou mixte. D'après le nom (`icav` = ICA vertical, `minh` = soustraction horizontal), la variante retenue serait l'ICA pour le vertical et la soustraction pour l'horizontal : interprétation à confirmer dans l'article. **Le choix de variante doit venir de la description de l'article (section 2.3, tableau 2), pas des scores sur le test.** Nous avons retenu `icav_minh` dans la configuration, à justifier par l'article.

## 3. Pipeline

| Étape | Dans l'article | Notre choix, s'il manque une information |
| --- | --- | --- |
| Sujets, sessions, exclusions | Décrit : 23 sujets, environ 2 h (2.1, p. 3) ; aucune exclusion mentionnée | Aucune exclusion : 23 expériences conservées (vérifié, toutes complètes) |
| Unité d'observation | Décrit : fenêtre de 8 s sans recouvrement, 885 par expérience (2.3, 2.4) | Fenêtres fournies telles quelles par SEED-VIG |
| Cible et labels | Décrit : PERCLOS continu, lunettes SMI (2.2, p. 4) | `perclos` fourni, dans [0 ; 1] |
| Prétraitement et artefacts | Décrit : EEG 1–75 Hz, 200 Hz ; EOG ICA / soustraction (2.3) | Features fournies par SEED-VIG (pas recalculées) |
| Features et normalisation | Features décrites (DE 2 Hz / 5 bandes, 36 EOG) ; normalisation absente | StandardScaler appris sur l'apprentissage |
| Lissage des features | Non décrit dans l'article (à vérifier) | Les variantes `movingAve` et `LDS` sont fournies (voir section 4) |
| Modèle et hyperparamètres | SVR RBF, grid search c et g (2.4) ; grille absente | Grille de la baseline : C ∈ {0,1 ; 1 ; 10}, gamma ∈ {scale ; 0,01 ; 0,001}, réglage interne par blocs |
| Découpage apprentissage / test | Incomplet : 5 sessions et 5 plis, contiguïté non précisée | 5 blocs contigus dans le temps (KFold sans mélange) |
| Métrique et agrégation | Décrit : RMSE, COR sur les 5 sessions concaténées (2.4, p. 7) | COR sur les 5 blocs concaténés ; RMSE moyen des plis ; moyenne et écart-type sur les sujets |

## 4. Ce qui ne doit jamais passer de l'apprentissage au test

- **Fenêtres voisines dans le temps** (forte autocorrélation) : découpage par blocs contigus. Un découpage aléatoire mettrait des fenêtres quasi identiques dans l'apprentissage et le test. Sera mesuré à l'étape 4.
- **Normalisation, sélection et réglage des hyperparamètres** : appris sur l'apprentissage seulement (Pipeline + GridSearchCV interne).
- **Lissage temporel des features (`movingAve`, `LDS`)** : risque de fuite.
  - Le Readme dit seulement que ce sont « moving average » et « linear dynamic system », sans préciser si la moyenne est centrée (elle utiliserait des fenêtres futures) ou causale.
  - Le LDS (lissage de Kalman) traite toute la séquence d'une expérience : chaque valeur peut dépendre de fenêtres futures, y compris celles du bloc de test.
  - Le lissage est fait sur l'expérience entière, avant le découpage. Les blocs de test ne sont donc pas indépendants des blocs d'apprentissage voisins.
  - À vérifier dans la section 2.3 de l'article. À mesurer à l'étape 4 : `movingAve` contre `LDS` contre features non lissées si elles existent (elles ne sont pas fournies ici : seules les variantes lissées le sont).

## 5. Première baseline et temps de calcul

Essai sur 1 sujet (`10_20151125_noon`), modalité EOG `icav_minh`, commande `python src/baselines.py --modalities eog --max-subjects 1` :

- Temps : **3 s** pour le sujet (7,7 s au total, démarrage de Python compris), sur cette machine.
- Résultat de ce sujet (à titre de contrôle, **pas un résultat** : un sujet ne donne pas d'écart-type) : moyenne COR −0,47 ; Ridge COR 0,82 / RMSE 0,079 ; SVR COR 0,85 / RMSE 0,076.
- **Point d'attention, à expliquer à l'étape 2** : la baseline « moyenne » a une COR négative. Elle ne prédit pas une constante sur les 5 blocs concaténés : chaque pli prédit la moyenne de son propre apprentissage, et ces moyennes diffèrent d'un pli à l'autre. La COR est donc calculée sur des prédictions qui varient. C'est une conséquence du protocole de concaténation, pas un bug. À documenter.
- Les sorties de ce test ont été supprimées pour ne pas les confondre avec les résultats de l'étape 2.

## 6. Plan B

À compléter avec la fiche R4.
**Question ouverte** : nous n'avons pas la fiche R4 dans le dépôt.
