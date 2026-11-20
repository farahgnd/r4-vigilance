# Protocole – R4 : vigilance (PERCLOS) à partir de l'EEG et de l'EOG frontal

Ce document est écrit **avant** tout calcul de l'étape 2. Il fixe les choix ci-dessous. Si un choix change plus tard, la modification est datée et justifiée dans `reports/ecarts.md`, jamais effacée.

Référence : Zheng et Lu 2017, manuscrit fourni (`reports/article/R4_Zheng2017.pdf`). Fiche : `reports/article/R4.pdf`. Carte : `reports/carte.md`.

## 1. Question et cible

- **Cible** : PERCLOS continu, `perclos` dans `perclos_labels/`, valeurs dans [0 ; 1] (vérifié à l'étape 1).
- **Unité d'observation** : une fenêtre de 8 s. Une expérience = 885 fenêtres.
- **Question du sujet** (fil rouge) : la prédiction vient-elle de l'EEG, ou surtout des signaux oculaires, proches de la cible ?
- **Objectif minimal (fiche)** : SVR sur EEG seul, EOG seul et fusion, avec les 5 sessions contiguës de l'article ; COR et RMSE ; baseline EOG seule.

## 2. Données et exclusions

- SEED-VIG, 23 expériences, toutes conservées (aucune exclusion, vérifié à l'étape 1).
- Les features sont celles fournies par SEED-VIG. Nous ne les recalculons pas.

## 3. Modalités comparées

| Nom | Source | Dimension | Rôle |
| --- | --- | --- | --- |
| **EOG frontal** | `EOG_Feature/features_table_icav_minh` (ICA-MINUS) | 36 | modalité 1 (principale) |
| **EEG frontal 2 Hz** | `Forehead_EEG/EEG_Feature_2Hz`, `de_movingAve`, 4 canaux × 25 bandes | 100 | modalité 2 (principale) |
| **Fusion frontale** | EOG frontal + EEG frontal 2 Hz (concaténation) | 136 | modalité 3 (principale) |
| EEG postérieur 2 Hz | `EEG_Feature_2Hz`, canaux 7–17 (11 canaux), 25 bandes | 275 | secondaire (Tableau 3 de l'article) |
| EEG temporal 2 Hz | `EEG_Feature_2Hz`, canaux 1–6 (6 canaux), 25 bandes | 150 | secondaire (Tableau 3) |
| EEG frontal 5 bandes | `Forehead_EEG/EEG_Feature_5Bands`, 4 × 5 | 20 | secondaire (Tableau 3) |
| Fusion frontale 5 bandes | EOG frontal + EEG frontal 5 bandes | 56 | secondaire |

**Choix justifiés avant calcul** :
- **Variante EOG** : `icav_minh` = ICA-MINUS, retenue par l'article (tableau 2). Nous ne la re-sélectionnons pas sur nos résultats.
- **Variante EEG** : `de_movingAve`. Le manuscrit ne décrit aucun lissage pour les DE (2.3.4, p. 8). Nous prenons `movingAve` plutôt que `LDS`, car `LDS` est un modèle temporel qui traite toute la séquence (voir `reports/carte.md`, section 4). `LDS` est testé à l'étape 4 comme risque de fuite, pas comme choix de modèle.
- **Zones EEG** : canaux 1–6 = temporaux, canaux 7–17 = postérieurs, selon les noms du fichier brut (vérifié à l'étape 1). CPZ est absent du jeu de données, alors que l'article en a 12 postérieurs (écart à signaler).
- **Résolution fréquentielle** : 2 Hz comme modalité principale, parce que le manuscrit le retient (p. 9 : « we employ the EEG features with a 2 Hz frequency resolution »). Les 5 bandes sont secondaires.

## 4. Découpage et validation

- **Sessions** : chaque expérience est coupée en **5 blocs contigus** de fenêtres dans l'ordre temporel, sans mélange (`KFold(n_splits=5, shuffle=False)`). Le manuscrit ne précise pas la contiguïté ; la fiche la demande, nous la suivons.
- **Validation croisée** : 5 plis. Pour chaque pli, 4 blocs servent à apprendre et 1 bloc à tester.
- **Mêmes plis pour toutes les modalités** : les mêmes 885 fenêtres et les mêmes 5 blocs sont utilisés pour chaque modalité. C'est ce qui permet les comparaisons appariées.
- **Réglage interne** : à l'intérieur des 4 blocs d'apprentissage d'un pli, `GridSearchCV` avec 4 blocs contigus (pas de mélange). Le bloc de test n'est jamais utilisé pour choisir un paramètre.

## 5. Modèles

- **SVR RBF** (`sklearn.svm.SVR`), dans un `Pipeline` : `StandardScaler` puis SVR. Le scaler est appris sur l'apprentissage seulement.
- **Grille** : C ∈ {0,1 ; 1 ; 10}, gamma ∈ {`scale` ; 0,01 ; 0,001}. L'article ne publie pas sa grille ; celle-ci est notre choix, documenté.
- **Référence** : moyenne d'apprentissage (`DummyRegressor`) et Ridge (grille alpha ∈ {0,1 ; 1 ; 10 ; 100 ; 1000}). Ces deux modèles servent de repères, pas de cible de reproduction.
- **Fusion** : concaténation des features (comme l'article, 2.4 p. 8). Pas de modèle de fusion tardive.
- **CCRF / CCNF** : non implémentés à ce stade. L'étape 3 proposera une approximation causale, partielle.

## 6. Métriques

Pour chaque expérience et chaque modèle :
- **COR** : corrélation de Pearson entre les 885 prédictions hors pli (concaténées dans l'ordre temporel) et les 885 labels. Définition de l'article (éq. 10, p. 8).
- **RMSE** : racine de l'erreur quadratique moyenne sur ces mêmes 885 prédictions (éq. 9, p. 8).

**Changement par rapport au code de départ** : `baselines.py` faisait la moyenne des RMSE par pli. Nous passons au RMSE calculé sur les 885 prédictions, comme la formule (9) de l'article. Ce changement est fait **avant** tout calcul de l'étape 2 et est donc noté ici.

Agrégation :
- **Par expérience** : une valeur de COR et une de RMSE, par modèle et par modalité.
- **Sur les 23 sujets** : moyenne et écart-type, et un intervalle de confiance à 95 % par bootstrap sur les sujets (10 000 rééchantillonnages, graine 42). L'unité statistique est le **sujet**, pas la fenêtre.

## 7. Comparaisons et règle de décision

- **Test apparié** : Wilcoxon signé sur les 23 sujets, pour chaque paire de modalités. Paires prévues :
  1. fusion frontale vs EOG frontal ;
  2. fusion frontale vs EEG frontal 2 Hz ;
  3. EEG frontal 2 Hz vs EOG frontal ;
  4. EEG postérieur 2 Hz vs EOG frontal (secondaire, pour l'article).
- **Correction** : Holm sur les paires testées, sur COR et sur RMSE séparément.
- **Seuil** : α = 0,05 après correction de Holm.
- **Lecture de la question du sujet** : la fusion apporte-t-elle un gain significatif par rapport à l'EOG seul ? Si oui, l'EEG apporte une information en plus des signaux oculaires. Si non, l'information utile est surtout oculaire. Un résultat non significatif n'est pas une preuve d'absence d'effet : nous le dirons ainsi.
- **Pas de sélection sur le test** : aucun choix (grille, variante, zone) n'est modifié après avoir vu les résultats de test. Si cela arrive, le choix est reporté dans `reports/ecarts.md`.

## 8. Ce qui ne doit pas être fait

- Régler un paramètre, choisir une variante ou une zone en regardant le score de test.
- Mélanger les fenêtres avant le découpage (fuite entre fenêtres voisines).
- Normaliser ou sélectionner sur tout le jeu de données.
- Comparer des modèles sur des plis différents.
- Présenter une valeur sans son écart-type ou son IC.

## 9. Traçabilité

Chaque exécution enregistre : graine (42), version de Python et des bibliothèques, commande, temps de calcul, nombre de sujets. Les prédictions hors pli sont sauvegardées avec le sujet, le pli (session) et l'indice de fenêtre, pour que chaque résultat puisse être retrouvé.

Versions prévues : Python 3.11.9, numpy 2.4.6, scipy 1.17.1, scikit-learn 1.9.1, pandas 3.1.1.

## 10. Plan d'exécution (étape 2)

1. Protocole écrit et commité (ce document).
2. Mise à jour de `src/data.py` : sélection des canaux par zone, et `src/baselines.py` : RMSE de l'éq. 9, colonne `session`.
3. EDA sur les labels : distribution du PERCLOS, évolution dans le temps par sujet, autocorrélation (`src/eda.py`). Ce sont des statistiques sur les labels, pas un réglage de modèle.
4. Baselines sur les 23 sujets : moyenne, Ridge, SVR pour EOG frontal, EEG frontal 2 Hz, fusion frontale ; secondaires EEG postérieur / temporal / 5 bandes.
5. Tests appariés et IC, sauvegardés dans `results/`.

---

## Amendement du 2026-11-20 : grille SVR élargie (avant relance)

**Motif** : à l'étape 2, la baseline Ridge a fait mieux que la SVR sur la fusion frontale (COR moyenne 0,792 contre 0,775 pour la SVR, mêmes plis). Une grille de 9 combinaisons, avec `gamma = scale`, est peut-être trop étroite. Ce constat vient des scores de **validation croisée** de l'étape 2 et d'une comparaison entre modèles ; il ne vient pas d'un choix fait sur les scores de test. L'amendement ne change ni les plis, ni les modalités, ni les métriques.

**Ce qui change** : la grille de la SVR devient une grille de type LIBSVM (pas de 2 sur l'exposant) :
- C = 2^k pour k ∈ {-5, -3, -1, 1, 3, 5, 7, 9, 10} (9 valeurs). Le dernier point, 2^10, est ajouté pour atteindre la borne demandée ; le pas de 2 à partir de -5 n'y arrive pas exactement.
- gamma = 2^k pour k ∈ {-15, -13, ..., 1, 3} (10 valeurs, pas de 2).
- Soit 90 combinaisons, réglées par validation interne (4 blocs contigus) sur l'apprentissage **seulement**, comme avant.

**Inchangé** : StandardScaler appris sur l'apprentissage ; 5 blocs contigus ; COR et RMSE sur les 885 prédictions concaténées ; Ridge et moyenne ; modalités ; graine 42.

**Conservation** : les résultats de l'ancienne grille (9 combinaisons : C ∈ {0,1 ; 1 ; 10}, gamma ∈ {scale ; 0,01 ; 0,001}) sont conservés dans `results/grille_v1/`. Ils sont présentés à côté des nouveaux dans `reports/ecarts.md`.

**Règle** : la nouvelle grille sera la grille principale. Une éventuelle comparaison des grilles se fera uniquement avec les tests appariés déjà prévus, sans nouveau choix sur le test.
