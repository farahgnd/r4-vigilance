# Carte de reproductibilité – R4

Article : Zheng et Lu 2017, *A Multimodal Approach to Estimating Vigilance Using EEG and Forehead EOG*, J. Neural Eng. 14 026017.
Pour chaque information : page / section / tableau / figure **du manuscrit fourni** (`reports/article/R4_Zheng2017.pdf`, 16 pages, pagination différente de la version publiée). Les numéros de page ont été relus sur ce manuscrit (en-tête imprimé en haut de chaque page).
Fiche sujet : `reports/article/R4.pdf`.

## 0. Type de reproduction visé

Fiche R4 : **reproduction fidèle pour la SVR** (mêmes données SEED-VIG, mêmes modalités) ; **partielle pour CCRF et CCNF**.

- Fidèle pour la SVR : mêmes features fournies, même découpage en 5 sessions et 5 plis, même métrique (COR sur les 885 prédictions concaténées).
- Partielle pour CCRF et CCNF : ces modèles ne sont pas implémentés dans scikit-learn. Une approximation causale (lissage des prédictions passées) est prévue à l'étape 3. Elle ne reproduit pas CCRF/CCNF.

## 1. Résultat à reproduire

Fiche, « Ce qui vous est demandé », point 1 : **Figure 10 et texte p. 11** du manuscrit, montage frontal, COR / RMSE moyens :

| Modèle | COR | RMSE | Source |
| --- | --- | --- | --- |
| SVR (EEG frontal + EOG frontal) | 0,83 | 0,10 | texte p. 11, l. « For the forehead setup » ; figure 10 p. 11 |
| CCRF | 0,84 | 0,10 | idem |
| CCNF | 0,85 | 0,09 | idem |

Protocole du résultat : 885 échantillons de 8 s par expérience, **5 sessions**, **validation croisée à 5 plis** (section 2.4, p. 8). Le manuscrit dit « separated into five sessions » sans préciser la contiguïté : la fiche demande des sessions **contiguës**, nous le suivons (voir section 3).

Résultats mono-modalité que nous voulons aussi retrouver (Tableaux 2 et 3, p. 9 ; conclusion p. 13) :

| Résultat | COR (moyenne ± ET) | RMSE (moyenne ± ET) | Source |
| --- | --- | --- | --- |
| EOG frontal, ICA-MINUS (= `icav_minh`) | 0,7773 ± 0,1745 | 0,1188 ± 0,0391 | Tableau 2, p. 9 ; conclusion p. 13 : « 0.78/0.12 » |
| EEG postérieur 2 Hz | 0,7001 ± 0,2250 | 0,1327 ± 0,0303 | Tableau 3, p. 9 ; conclusion : « 0.70/0.13 » (EEG seul) |
| EEG temporal 2 Hz | 0,6678 ± 0,2349 | 0,1385 ± 0,0343 | Tableau 3, p. 9 |
| EEG frontal 2 Hz | 0,6502 ± 0,2116 | 0,1463 ± 0,0383 | Tableau 3, p. 9 |
| EEG postérieur 5 bandes | 0,6807 ± 0,2129 | 0,1429 ± 0,0393 | Tableau 3, p. 9 |
| EEG temporal 5 bandes | 0,6410 ± 0,2246 | 0,1603 ± 0,0722 | Tableau 3, p. 9 |
| EEG frontal 5 bandes | 0,5749 ± 0,2463 | 0,1640 ± 0,0483 | Tableau 3, p. 9 |

Lecture du texte p. 11 : le EOG frontal fait mieux que l'EEG postérieur ; la fusion frontale améliore la COR et diminue la RMSE. La section 3.3 (p. 10–11) introduit la fusion.

Note sur les figures : la figure 10 (p. 11) est un graphique vectoriel sans valeurs numériques dans le texte. Les valeurs de la figure ne sont **pas** lues ici ; seules celles du texte et des tableaux sont utilisées comme cibles.

Question du sujet (fil rouge, fiche) : *une bonne prédiction du PERCLOS vient-elle de l'EEG, ou surtout des signaux oculaires, proches de la cible ?* Le manuscrit suggère les signaux oculaires : « forehead EOG has more information in common with the annotations of eye tracking data » (p. 11). Nous testons cela par l'apport de l'EEG frontal au-dessus de l'EOG seul (comparaison appariée).

## 2. Données

- Nom et version : SEED-VIG (fourni avec `Readme_English.txt`, 23 expériences, 885 fenêtres de 8 s chacune).
- Fichier téléchargé et ouvert : **oui** (archive `SEED-VIG.zip`, dossier extrait dans `C:/Users/WIN11/Downloads/SEED-VIG/SEED-VIG`, hors du dépôt).
- Taille : environ 3 Go extraits (archive 3,1 Go). Le README du projet disait 2 Go : information corrigée.
- Licence : usage académique, pas de redistribution hors du cours.
- Contrôles (étape 1, sur les 23 expériences) :
  - 885 fenêtres par expérience, pour toutes les modalités et pour les labels ;
  - aucune valeur manquante ni infinie ;
  - PERCLOS dans [0,0221 ; 1,0000], cohérent avec l'intervalle 0–1 annoncé ;
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

- **Correction de `_to_2d`** (`src/data.py`) : le code choisissait l'axe des fenêtres par `argmax`. Le résultat était juste ici (885 est le plus grand axe), mais c'était une devinette. L'axe 1 est maintenant explicite, comme le documente le Readme.
- **Zones EEG, résolues** : le Readme dit « canaux 1–5 temporaux, 7–17 postérieurs », sans attribuer le canal 6. Le fichier brut `Raw_Data/10_20151125_noon.mat` donne les noms des 17 canaux :
  - canaux 1–6 = FT7, FT8, T7, T8, TP7, TP8 : **6 canaux temporaux**, ce qui correspond à la section 2.1 (p. 4) ;
  - canaux 7–17 = CP1, CP2, P1, PZ, P2, PO3, POZ, PO4, O1, OZ, O2 : **11 canaux postérieurs**. L'article en décrit 12 (p. 4), avec CPZ en plus, qui est absent du jeu de données. Écart à signaler.
  - Le Readme est donc inexact sur le canal 6 : il est temporal.
- **Montage frontal** : `Forehead_EEG` = 4 canaux (les canaux 4–7 de l'article, p. 6–7, reconstruits par ICA). Les features sont déjà calculées par les auteurs : nous ne les recalculons pas.
- **Variantes EOG** : `features_table_icav_minh` correspond à **ICA-MINUS** du tableau 2 (p. 9) : VEOf par ICA, HEOf par soustraction. C'est la variante que l'article retient comme la meilleure. Le choix vient donc de l'article (qui l'a sélectionnée sur ses propres résultats), et nous le reprenons sans le re-sélectionner sur le test.
- Les autres variantes (`features_table_ica` = EOG-ICA, `features_table_minus` = EOG-MINUS) sont dans le tableau 2 et pourront servir de comparaison à l'étape 4.

## 3. Pipeline

| Étape | Dans l'article (manuscrit) | Notre choix, s'il manque une information |
| --- | --- | --- |
| Sujets, sessions, exclusions | 23 sujets, 12 femmes, environ 2 h (2.1, p. 4) ; aucune exclusion mentionnée | Les 23 expériences, aucune exclusion (vérifié, toutes complètes) |
| Unité d'observation | Fenêtres de 8 s **sans recouvrement**, 885 par expérience (2.3.2 p. 6 ; 2.3.4 p. 8 ; 2.4 p. 8) | Fenêtres fournies telles quelles par SEED-VIG |
| Cible et labels | PERCLOS continu, lunettes SMI, formule (1) (2.2, p. 4–5) | `perclos` fourni, dans [0 ; 1] |
| Prétraitement et artefacts | EEG filtré 1–75 Hz, sous-échantillonné à 200 Hz (2.3.4, p. 7) ; EOG par ondelettes puis ICA ou soustraction (2.3.1–2.3.2, p. 5–6) | Features fournies par SEED-VIG, non recalculées |
| Features EEG | DE, sur 5 bandes et sur 2 Hz (1–50 Hz), fenêtre 8 s (2.3.4, p. 8) | DE `movingAve`, voir section 4 ; le manuscrit ne mentionne pas de lissage |
| Features EOG | 36 features (Tableau 1, p. 6) | `icav_minh` = ICA-MINUS (tableau 2, p. 9) |
| Normalisation | Non décrite | StandardScaler appris sur l'apprentissage seulement |
| Modèle et hyperparamètres | SVR RBF, grid search sur c et g (2.4, p. 8) ; grille non publiée | Grille de la baseline : C ∈ {0,1 ; 1 ; 10}, gamma ∈ {scale ; 0,01 ; 0,001}, réglage interne par blocs |
| Fusion | Concaténation des vecteurs de features (2.4, p. 8) | Idem |
| Découpage apprentissage / test | « five sessions » et « 5-fold cross validation » (2.4, p. 8) ; contiguïté non précisée | 5 blocs contigus, sans mélange (KFold, shuffle=False) |
| Métrique | RMSE (éq. 9) et COR (éq. 10) ; COR sur les 5 sessions concaténées (2.4, p. 8) | COR sur les 885 prédictions concaténées ; RMSE calculé de la même façon (éq. 9) |
| Agrégation | Non précisée | Moyenne ± écart-type sur les 23 sujets, IC 95 % par bootstrap, tests appariés |
| CCRF / CCNF | Définis (2.5, p. 8–9) ; grilles de régularisation 10^[0,1,2] et 10^[−3..0] (p. 9) | Non implémentés (étape 3 : approximation causale, partielle) |

## 4. Ce qui ne doit jamais passer de l'apprentissage au test

- **Fenêtres voisines dans le temps** (forte autocorrélation) : découpage par blocs contigus. Un découpage aléatoire mettrait des fenêtres quasi identiques dans l'apprentissage et dans le test. À mesurer à l'étape 4.
- **Normalisation, sélection et réglage des hyperparamètres** : appris sur l'apprentissage seulement (Pipeline + GridSearchCV interne).
- **Lissage temporel des features** : risque de fuite.
  - Le Readme indique seulement « moving average » et « linear dynamic system ». Il ne dit pas si la moyenne est centrée (utilise des fenêtres futures) ou causale.
  - Le LDS (lissage linéaire de type Kalman) traite toute la séquence d'une expérience : chaque valeur peut dépendre de fenêtres futures, y compris du bloc de test.
  - Le manuscrit ne décrit aucun lissage de ce type pour les DE (2.3.4, p. 8). Le suffixe `movingAve` est donc un ajout des données, absent de l'article.
  - À mesurer à l'étape 4 : `movingAve` contre `LDS` (les features non lissées ne sont pas fournies).
- **Comparaison de modalités** : toutes les modalités sont évaluées sur les mêmes 885 fenêtres et les mêmes 5 blocs.

## 5. Première baseline et temps de calcul

Essai sur 1 sujet (`10_20151125_noon`), modalité EOG `icav_minh`, commande `python src/baselines.py --modalities eog --max-subjects 1` :

- Temps : **3 s** pour le sujet (7,7 s au total, démarrage de Python compris), sur cette machine.
- Résultat de ce sujet, à titre de contrôle seulement (**pas un résultat** : un sujet ne donne pas d'écart-type) : moyenne COR −0,47 ; Ridge COR 0,82 / RMSE 0,079 ; SVR COR 0,85 / RMSE 0,076.
- Point d'attention : la baseline « moyenne » a une COR négative. Chaque pli prédit la moyenne de son propre apprentissage, et ces moyennes diffèrent d'un pli à l'autre. Les prédictions concaténées varient donc, et la COR peut devenir négative. Ce n'est pas un bug. À documenter dans le rapport.
- Les sorties de ce test ont été supprimées pour ne pas les confondre avec les résultats de l'étape 2.

## 6. Plan B

Fiche R4 : **Cao et al. (2019)**, conduite simulée, données publiques figshare. La cible devient un **temps de réaction** : c'est une **réplication conceptuelle** (nouvelle carte à produire pour ce jeu de données, pas celle-ci).

Nous ne passons au plan B que si SEED-VIG bloque la reproduction de la SVR. Ce n'est pas le cas à ce stade : toutes les formes et la concordance avec les labels ont été vérifiées (étape 1).
