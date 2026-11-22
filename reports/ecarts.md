# Écarts : article contre reproduction – R4 (étape 3)

Référence : Zheng et Lu 2017, manuscrit fourni `reports/article/R4_Zheng2017.pdf` (16 pages, pagination du manuscrit). Protocole : `reports/protocole.md`, amendement du 2026-11-20 inclus. Carte : `reports/carte.md`.

**Décision du 2026-11-22 (voir `reports/protocole.md`)** : le **résultat principal est la grille v1** (protocole d'origine). La **grille v2 est une analyse de sensibilité** : elle est présentée à côté, mais elle ne remplace pas le résultat principal.

Deux grilles de réglage SVR sont présentées :
- **v1** : C ∈ {0,1 ; 1 ; 10}, gamma ∈ {scale ; 0,01 ; 0,001} (9 combinaisons, grille de l'étape 2). Résultats dans `results/grille_v1/`.
- **v2** : grille LIBSVM, C = 2^k pour k ∈ {-5, -3, …, 9, 10}, gamma = 2^k pour k ∈ {-15, -13, …, 3} (90 combinaisons). Amendement daté dans le protocole, motivé par l'écart Ridge > SVR constaté à l'étape 2 (validation croisée, pas le test). Résultats dans `results/`.

Les deux grilles utilisent le même protocole : 23 sujets, 5 blocs contigus, 5 plis, réglage interne par validation croisée sur l'apprentissage seulement, COR et RMSE sur les 885 prédictions concaténées.

**Précision de lecture** : les chiffres de l'article sont tirés du texte et des tableaux (Table 2 p. 9, Table 3 p. 9, texte p. 11, conclusion p. 13). Les valeurs individuelles de la figure 10 (p. 11) ne sont pas lues (graphique vectoriel). Les écarts-types de l'article sont ceux des tableaux 2 et 3.

## 1. Tableau principal : article contre reproduction

COR (moyenne ± écart-type sur 23 sujets) et RMSE. Modèle : SVR RBF sauf mention.

### 1a. Mono-modalités

| Modalité | Article (COR / RMSE) | Reproduction v1 (COR / RMSE) | Reproduction v2 (COR / RMSE) | Pages article |
| --- | --- | --- | --- | --- |
| EOG frontal, ICA-MINUS (`icav_minh`) | 0,7773 ± 0,1745 / 0,1188 ± 0,0391 | 0,764 ± 0,193 / 0,126 ± 0,041 | 0,747 ± 0,228 / 0,129 ± 0,043 | Table 2, p. 9 ; conclusion p. 13 (0,78 / 0,12) |
| EEG postérieur 2 Hz (11 canaux) | 0,7001 ± 0,2250 / 0,1327 ± 0,0303 | 0,647 ± 0,240 / 0,152 ± 0,038 | 0,545 ± 0,351 / 0,159 ± 0,052 | Table 3, p. 9 ; conclusion (0,70 / 0,13) |
| EEG temporal 2 Hz (6 canaux) | 0,6678 ± 0,2349 / 0,1385 ± 0,0343 | 0,633 ± 0,274 / 0,149 ± 0,036 | 0,573 ± 0,315 / 0,157 ± 0,061 | Table 3, p. 9 |
| EEG frontal 2 Hz (4 canaux) | 0,6502 ± 0,2116 / 0,1463 ± 0,0383 | 0,613 ± 0,265 / 0,151 ± 0,038 | 0,571 ± 0,300 / 0,159 ± 0,038 | Table 3, p. 9 |
| EEG postérieur 5 bandes | 0,6807 ± 0,2129 / 0,1429 ± 0,0393 | 0,644 ± 0,241 / 0,151 ± 0,053 | 0,613 ± 0,276 / 0,155 ± 0,057 | Table 3, p. 9 |
| EEG temporal 5 bandes | 0,6410 ± 0,2246 / 0,1603 ± 0,0722 | 0,638 ± 0,261 / 0,151 ± 0,048 | 0,580 ± 0,303 / 0,159 ± 0,063 | Table 3, p. 9 |
| EEG frontal 5 bandes | 0,5749 ± 0,2463 / 0,1640 ± 0,0483 | 0,605 ± 0,228 / 0,160 ± 0,036 | 0,542 ± 0,297 / 0,168 ± 0,046 | Table 3, p. 9 |

### 1b. Fusion frontale (cible principale de la fiche)

| Modèle | Article (COR / RMSE) | Reproduction v1 (COR / RMSE) | Reproduction v2 (COR / RMSE) | Pages article |
| --- | --- | --- | --- | --- |
| **SVR, EEG frontal 2 Hz + EOG frontal** | **0,83 / 0,10** | **0,775 ± 0,212 / 0,117 ± 0,030** | **0,732 ± 0,281 / 0,126 ± 0,038** | texte p. 11, l. « For the forehead setup » ; figure 10 p. 11 |
| CCRF | 0,84 / 0,10 | non reproduit (approximation causale : voir section 3) | non reproduit | idem |
| CCNF | 0,85 / 0,09 | non reproduit | non reproduit | idem ; conclusion p. 13 (0,85 / 0,09) |
| Ridge (repère), même fusion | non rapporté | 0,792 ± 0,204 / 0,125 ± 0,055 | 0,792 ± 0,204 / 0,125 ± 0,055 (Ridge inchangé) | non rapporté |

**Lecture** : avec la grille v1, la SVR fusion approche l'article (COR 0,78 contre 0,83 ; RMSE 0,117 contre 0,10). Avec la grille v2, l'écart se creuse (COR 0,73 contre 0,83). **La grille élargie ne réduit donc pas l'écart sur la fusion. Elle l'augmente.**

### 1c. Fusion 5 bandes (exploratoire, non préplanifiée)

| Modèle | Reproduction v1 | Reproduction v2 |
| --- | --- | --- |
| SVR, EEG frontal 5 bandes + EOG | 0,804 ± 0,168 / 0,116 ± 0,032 | 0,748 ± 0,244 / 0,126 ± 0,036 |

Ce résultat est **exploratoire**. Il n'était pas dans les comparaisons prévues au protocole, et l'article ne le rapporte pas. Il ne doit pas être présenté comme résultat principal : le retenir après l'avoir vu reviendrait à sélectionner sur le test. Il n'est pas testé statistiquement dans ce rapport.

### 1d. Intervalles de confiance (bootstrap sur les sujets, 10 000 rééchantillonnages)

| Modalité (SVR) | COR v1 [IC 95 %] | COR v2 [IC 95 %] |
| --- | --- | --- |
| EOG frontal | 0,764 [0,680 ; 0,835] | 0,747 [0,646 ; 0,830] |
| Fusion frontale 2 Hz | 0,775 [0,683 ; 0,856] | 0,732 [0,612 ; 0,838] |
| EEG frontal 2 Hz | 0,613 [0,505 ; 0,715] | 0,571 [0,449 ; 0,688] |

Les intervalles se recouvrent largement. **Les écarts entre la reproduction et l'article (0,05 à 0,10 en COR) sont du même ordre que l'incertitude sur 23 sujets** : on ne peut pas, avec cet échantillon, affirmer qu'un écart de 0,05 est réel. Ce qui est établi, c'est le sens des comparaisons appariées (section 2).

## 2. Comparaisons appariées : le gain de la fusion est-il significatif ?

Wilcoxon signé sur les 23 sujets, mêmes plis, correction de Holm sur les 4 comparaisons prévues, séparément pour COR et RMSE.

| Comparaison | Grille | Δ COR (moyenne) | p Holm COR | Δ RMSE | p Holm RMSE |
| --- | --- | --- | --- | --- | --- |
| **Fusion vs EOG seul** | v1 | +0,011 | 0,30 (n.s.) | −0,009 | 0,14 (n.s.) |
| **Fusion vs EOG seul** | v2 | −0,015 | 0,99 (n.s.) | −0,004 | 0,69 (n.s.) |
| Fusion vs EEG frontal | v1 | +0,162 | < 0,001 | −0,034 | < 0,001 |
| Fusion vs EEG frontal | v2 | +0,161 | < 0,001 | −0,033 | 0,003 |
| EEG frontal vs EOG | v1 | −0,152 | 0,004 | +0,025 | 0,022 |
| EEG frontal vs EOG | v2 | −0,176 | 0,002 | +0,030 | 0,013 |
| EEG postérieur vs EOG | v1 | −0,117 | 0,013 | +0,026 | 0,012 |
| EEG postérieur vs EOG | v2 | −0,201 | 0,006 | +0,030 | 0,022 |

**Réponse à la question de la fiche** :
- **Le gain fusion vs EOG seul n'est pas significatif, dans aucune des deux grilles.** En v1 il est positif mais faible (+0,011 COR, p Holm 0,30). En v2 il est négatif (−0,015 COR, p Holm 0,99).
- L'article rapporte, lui, une fusion qui améliore significativement la régression (p. 10–11 : « Modality fusion can significantly enhance the regression performance »). Il rapporte aussi une ANOVA sur les COR, avec p = 0,2978 pour l'EOG frontal et p = 0,0264 pour l'EEG postérieur (p. 11). Ces p-valeurs ne sont pas comparables à nos tests appariés, car le test n'est pas le même.
- **Ce que nous observons** : l'EEG frontal apporte une information nettement moins bonne que l'EOG (COR −0,15 à −0,18, significatif). Ajouter l'EEG à l'EOG ne change pas significativement le résultat. Dans nos données, la prédiction du PERCLOS vient donc surtout des signaux oculaires, ce qui rejoint l'hypothèse de l'article (p. 10 : « forehead EOG has more information in common with the annotations of eye tracking data »). Notre résultat ne réfute pas un gain faible de la fusion : nos tests ont une puissance limitée sur 23 sujets.

## 3. Approximation causale de CCRF : lissage des prédictions SVR

Lissage causal : moyenne des prédictions passées et courantes sur une fenêtre de longueur 7 (longueur de séquence de l'article, p. 9), à l'intérieur de chaque bloc. Aucun label n'est utilisé. Comparaison à la SVR brute, grille v2, mêmes 23 sujets et mêmes plis.

| Modalité | COR brute → lissée | Δ COR | p Holm COR | RMSE brute → lissé | p Holm RMSE |
| --- | --- | --- | --- | --- | --- |
| EOG frontal | 0,747 → 0,735 | −0,012 | 0,004 | 0,129 → 0,134 | 0,002 |
| EEG frontal 2 Hz | 0,571 → 0,567 | −0,005 | 0,30 (n.s.) | 0,159 → 0,160 | 0,38 (n.s.) |
| Fusion frontale 2 Hz | 0,732 → 0,718 | −0,014 | < 0,001 | 0,126 → 0,131 | < 0,001 |

**Résultat** : le lissage causal **dégrade** légèrement la prédiction (significativement pour l'EOG et la fusion). Il ne reproduit donc pas le gain de CCRF (0,83 → 0,84 dans l'article).

**Explication** : le lissage causal introduit un retard. Une moyenne sur les 7 dernières fenêtres (56 s) répond plus lentement aux changements de vigilance. Les écarts en COR augmentent là où les transitions sont rapides. CCRF, lui, modélise la séquence de façon jointe et peut s'appuyer sur les fenêtres voisines dans les deux sens, à partir de la structure apprise. Notre approximation n'a pas accès aux fenêtres futures par construction. Elle ne peut donc pas reproduire ce gain, et le résultat ne doit pas être interprété comme une réfutation de CCRF.

## 4. Explication de chaque écart

### 4.1 Grille de réglage de la SVR (écart principal sur la fusion)

- **Constat** : passer de v1 à v2 dégrade la SVR sur toutes les modalités (fusion : 0,775 → 0,732 ; EOG : 0,764 → 0,747 ; EEG frontal : 0,613 → 0,571). La grille élargie n'améliore donc pas la SVR, contrairement à l'hypothèse de départ.
- **Hypothèse** : une grille plus large laisse la validation interne (4 blocs) choisir parmi davantage de combinaisons, dont des extrêmes (gamma très petit ou très grand). Le choix devient plus bruité et le modèle généralise moins bien. Cette hypothèse est **non vérifiée** : les hyperparamètres retenus à chaque pli n'ont pas été sauvegardés. Il faudrait les enregistrer pour la confirmer.
- **Conséquence** : l'écart Ridge > SVR constaté à l'étape 2 est confirmé, et même renforcé : Ridge fait 0,792 sur la fusion, la SVR 0,732 (v2). Le problème n'est donc pas une grille trop étroite. Il vient plus probablement du réglage de la SVR elle-même, ou d'une dépendance au choix des hyperparamètres dans cette configuration de données.
- **Statut** : la grille v1 reste la plus proche de l'article sur la fusion. La grille v2 est présentée comme résultat, comme demandé, mais elle ne rapproche pas de l'article.

### 4.2 Sessions contiguës

- L'article dit « separated the entire data from one experiment into five sessions » (p. 8), sans préciser la contiguïté. La fiche demande des sessions contiguës, nous les avons prises.
- **Effet attendu** : le découpage contigu est le plus strict, car il évite les fenêtres voisines dans l'apprentissage et le test. Un découpage aléatoire des fenêtres laisserait les fenêtres voisines (autocorrélation de 0,999 à 8 s, voir `figures/eda_autocorrelation.png`) passer de l'apprentissage au test, et ferait monter les scores artificiellement.
- **Hypothèse** : si l'article a utilisé un découpage non contigu, cela pourrait expliquer une partie de son avantage. **Non mesuré ici** : c'est l'objet de la comparaison « découpage aléatoire contre blocs contigus » prévue à l'étape 4.

### 4.3 Lissage `movingAve` des features EEG

- L'article décrit des DE calculées sur des fenêtres de 8 s non chevauchantes, sans mentionner de lissage ultérieur (p. 8). Le suffixe `movingAve` des fichiers SEED-VIG est donc un traitement ajouté par les données, non décrit dans l'article.
- Un lissage centré utiliserait des fenêtres futures, et pourrait gonfler les scores. Un lissage causal ne le ferait pas. Nous ne savons pas lequel est appliqué (voir `reports/carte.md`, section 4).
- **Choix fait avant calcul** : `movingAve` pour la SVR (variante principale), `LDS` non retenue pour l'étape 3. L'effet de ce choix est **non mesuré** : c'est l'objet de l'étape 4.

### 4.4 11 canaux postérieurs au lieu de 12 (CPZ absent)

- L'article décrit 12 canaux postérieurs (CP1, CPZ, CP2, P1, PZ, P2, PO3, POZ, PO4, O1, OZ, O2 ; p. 4). Le jeu de données en fournit 11 : CPZ manque (`Raw_Data`, canaux 7–17).
- Les canaux temporaux correspondent exactement (FT7, FT8, T7, T8, TP7, TP8, canaux 1–6).
- **Effet** : partiel et non isolable. Il ne peut pas expliquer seul l'écart sur l'EEG postérieur (0,647 contre 0,70 en v1), car nous ne l'avons pas mesuré séparément. Il contribue probablement à l'écart.
- **Constat** : en v1, l'ordre des zones EEG est reproduit : postérieur (0,647) > temporal (0,633) > frontal (0,613). En v2, l'ordre change (postérieur 0,545 < temporal 0,573 ≈ frontal 0,571). Le classement n'est donc stable qu'en v1.

### 4.5 Métrique : RMSE concaténé contre moyenne des RMSE par pli

- Le code de l'étape 2 calculait le RMSE comme moyenne des RMSE par pli. Le protocole, amendé avant calcul, utilise le RMSE sur les 885 prédictions concaténées (éq. 9 de l'article, p. 8).
- Mesure (`results/effet_metrique.csv`, sans réentraîner) : le RMSE concaténé est supérieur d'environ 0,01 à la moyenne des RMSE par pli, dans les deux grilles et pour toutes les modalités (par exemple fusion v1 : 0,117 concaténé contre 0,108 par pli).
- **Effet sur l'écart à l'article** : si l'article agrège par pli, sa valeur de RMSE de fusion (0,10) se compare à 0,108 (v1), soit un écart réduit de moitié. Nous ne savons pas comment l'article agrège, car le manuscrit ne le précise pas. Le choix reste donc à documenter comme une hypothèse.

### 4.6 Données et prétraitement

- Les features sont celles fournies par SEED-VIG, calculées par les auteurs du jeu de données. Nous ne les avons pas recalculées. Les étapes exactes (filtrage, ICA, DE) ne sont pas toutes détaillées dans l'article, donc une différence de traitement entre l'article et le jeu de données publié est possible et non mesurable ici.

### 4.7 Incertitude statistique

- Les écarts-types sur les sujets sont de 0,2 à 0,3 en COR. Les intervalles bootstrap (section 1d) se recouvrent largement avec l'article.
- Un écart de 0,05 en COR n'est pas, à lui seul, une preuve de non-reproduction. Le seul constat solide est la direction des comparaisons appariées (section 2) : l'EEG frontal est significativement moins bon que l'EOG, et la fusion n'apporte pas de gain significatif dans nos données.

## 5. Ce qui n'est pas reproduit, et pourquoi

| Élément | Statut | Raison |
| --- | --- | --- |
| SVR fusion 0,83 / 0,10 | Non reproduit (v1 0,775 / 0,117 ; v2 0,732 / 0,126) | Grille, métrique, sessions, lissage, canaux : voir section 4 |
| CCRF 0,84 / 0,10 | Non reproduit | CCRF modélise la séquence jointement ; notre approximation causale n'a pas accès au futur et dégrade la prédiction (section 3) |
| CCNF 0,85 / 0,09 | Non reproduit | Non implémenté (pas de bibliothèque standard dans scikit-learn) |
| Gain significatif de la fusion | Non reproduit | Test apparié sur 23 sujets : non significatif dans les deux grilles |

## 6. Limites et points non réglés

- Hyperparamètres retenus par pli : non sauvegardés. Il faudrait les enregistrer pour vérifier l'hypothèse de la section 4.1.
- Temps de calcul de `eeg_5b_front` (grille v2) : `results/meta_eeg_5b_front.json` indique 16 415 s, soit 4 h 33 en horloge murale. Les autres modalités prennent 250 à 870 s. Ce temps inclut probablement une interruption de la machine pendant le calcul. Le fichier de résultats est complet (23 sujets, 69 lignes) et n'a pas été relancé, conformément à la consigne. Le temps réel n'est donc pas mesuré. Il doit être corrigé dans l'annexe (étape 5).
- Pas de recalcul de la figure 10 (valeurs non lues).
- Les tests statistiques portent sur 23 sujets : leur puissance est limitée.

## 7. Pour l'oral : à retenir

1. **La grille élargie ne sauve pas la SVR.** Elle dégrade tous les résultats. L'hypothèse d'une grille trop étroite est fausse ici.
2. **Ridge fait mieux que la SVR sur la fusion** (0,792 contre 0,732 en v2). Ce constat est stable.
3. **La prédiction vient surtout de l'EOG.** L'EEG frontal est significativement moins bon ; la fusion ne gagne pas significativement sur l'EOG seul.
4. **Les écarts à l'article (0,05 à 0,10 en COR) sont du même ordre que l'incertitude sur 23 sujets.** Il faut le dire sans survendre.
5. **Le lissage causal ne reproduit pas CCRF** : il retarde la réponse et dégrade légèrement les scores. Ce n'est pas une réfutation de CCRF, qui exploite le contexte dans les deux sens.
6. **Les écarts ont des causes identifiées mais non mesurées** : sessions, `movingAve`, CPZ absent, métrique. Elles seront testées à l'étape 4 (sessions et `movingAve`) ou restent des hypothèses (CPZ, traitement des données).
7. **La fusion 5 bandes (0,80 en v1) est exploratoire.** Elle n'était pas prévue : ne pas la présenter comme résultat.

---

## 8. Étape 4 : vérifications (résultats de la grille v1, principale)

### 8.1 Hyperparamètres retenus (3 sujets, 5 plis, `results/hyperparametres_3sujets.csv`)

Le réglage interne est enregistré pour 3 sujets seulement, comme demandé ; les 23 sujets ne sont pas relancés.

| Grille | Modalité | C au bord | gamma au bord | Valeurs typiques |
| --- | --- | --- | --- | --- |
| v1 | EOG | 9/15 à C = 10 | 14/15 à gamma = 0,001 | C = 10 ou 1 ; gamma = 0,001 |
| v1 | EEG frontal 2 Hz | 4/15 à C = 10 | 12/15 à gamma = 0,001 (3/15 `scale`) | C = 1 ou 10 |
| v1 | Fusion | 8/15 à C = 10 | 15/15 à gamma = 0,001 | C = 10 |
| v2 | EOG | 4/15 à C = 2¹⁰ (+2/15 à 2⁹) | 6/15 à gamma = 2⁻¹⁵ | C de 0,5 à 2¹⁰ (majorité à 2⁵ ou plus) |
| v2 | EEG frontal 2 Hz | 0/15 | 2/15 à gamma = 2⁻¹⁵ | C de 0,125 à 2⁷ |
| v2 | Fusion | 2/15 à C = 2¹⁰ | 11/15 à gamma = 2⁻¹⁵ | C de 2 à 2¹⁰ (dont 7/15 à 2⁷ ou plus) |

**Lecture** : en v1, le gamma choisi est presque toujours le plus petit de la grille (0,001) ; en v2, il atteint souvent la borne 2⁻¹⁵ et le C la borne 2¹⁰. La SVR-RBF choisit donc un noyau très lisse, proche du linéaire, et la grille pousse vers la limite. Cela éclaire deux constats :
- **Ridge fait aussi bien que la SVR** (0,792 contre 0,775 en v1 sur la fusion) : la non-linéarité du RBF n'est pas utilisée.
- **Élargir la grille n'aide pas** : il faudrait descendre encore plus bas en gamma, ce qui revient à un modèle linéaire. Le problème n'est donc pas une borne trop étroite, mais un noyau RBF peu adapté à ces features.

**Limite** : les C et gamma sont lus sur 3 sujets, pas sur les 23. C'est un diagnostic, pas une preuve générale.

### 8.2 Découpage aléatoire contre blocs contigus (`results/decoupage_comparaisons.csv`)

Même grille v1, 23 sujets, mêmes modalités ; seul le découpage externe change. Réglage interne contigu dans les deux cas.

| Modalité | COR contigu → aléatoire | Δ COR [IC 95 %] | RMSE contigu → aléatoire | Δ RMSE [IC 95 %] |
| --- | --- | --- | --- | --- |
| EOG | 0,764 → 0,945 | +0,181 [+0,121 ; +0,252] | 0,126 → 0,066 | −0,061 [−0,074 ; −0,048] |
| EEG frontal 2 Hz | 0,613 → 0,889 | +0,277 [+0,190 ; +0,367] | 0,151 → 0,092 | −0,059 [−0,070 ; −0,048] |
| Fusion frontale | 0,775 → 0,952 | +0,177 [+0,108 ; +0,258] | 0,117 → 0,064 | −0,053 [−0,063 ; −0,044] |

Toutes les différences sont significatives (Wilcoxon apparié, p < 0,001).

**Conclusion** : le découpage aléatoire **gonfle les scores de 0,18 à 0,28 en COR** et divise l'erreur par deux environ. C'est la **preuve chiffrée de la fuite** entre fenêtres voisines : une fenêtre et ses voisines (autocorrélation 0,999 à 8 s) se retrouvent dans l'apprentissage et dans le test. Le découpage contigu est donc indispensable. Ce résultat donne aussi une piste d'explication pour les écarts avec l'article (section 4.2) : si l'article a utilisé un découpage non contigu, ses scores seraient gonflés de cette façon. C'est une hypothèse, non vérifiée.

### 8.3 Lissage movingAve et LDS (`src/lissage_test.py`)

**Alignement temporel** (proxy de la DE calculée sur les données brutes, 3 sujets, décalage en fenêtres de 8 s) :
- **movingAve** : corrélation maximale à **k = −3** (r = 0,599), contre r = 0,536 à k = 0. Le maximum est **avant** l'instant courant : la valeur à t résume les fenêtres **passées**. Cela correspond à une moyenne causale sur **7 fenêtres** (le centre de la moyenne tombe 3 fenêtres en arrière). **movingAve n'utilise pas de fenêtre future.**
- **LDS** : corrélation maximale à **k = 0** (r = 0,573). Le maximum est centré : le lissage **utilise des fenêtres futures**. Cohérent avec un lisseur de Kalman appliqué à toute la séquence d'une expérience (hypothèse de littérature, non vérifiée dans le code des auteurs).
- **Limite** : la proxy brute n'est pas la DE exacte de l'article (pas de STFT de 8 s). Seule la position du maximum est interprétée, pas la valeur absolue de r.

**Impact sur la prédiction** (SVR v1, 23 sujets, appariés, p bruts, non corrigés) :

| Modalité | COR movingAve → LDS | p | RMSE movingAve → LDS | p |
| --- | --- | --- | --- | --- |
| EEG frontal 2 Hz | 0,613 → 0,633 | 0,098 | 0,151 → 0,147 | 0,16 |
| Fusion frontale | 0,775 → 0,784 | 0,38 | 0,117 → 0,115 | 0,086 |

**Lecture** : LDS, qui utilise le futur, est un peu meilleur, mais la différence **n'est pas significative**. On ne peut pas conclure que l'utilisation du futur gonfle les scores. En revanche, LDS introduit une dépendance entre le bloc de test et ses voisins d'apprentissage à la frontière des blocs. Nous gardons `movingAve` (causal), comme décidé avant calcul.

**Features non lissées** : elles ne sont pas fournies par SEED-VIG pour les EEG (seules les variantes `movingAve` et `LDS` existent). Cette comparaison est donc **impossible** avec les données disponibles.

---

## 9. Étape 4 : extension inter-sujets (leave-one-subject-out, `reports/extension.md`)

Résultats détaillés dans `reports/extension.md`, section 8. Résumé :

- **H1 confirmée** : l'EEG frontal est significativement moins bon que l'EOG en inter-sujets (COR 0,53 contre 0,79 ; p Holm = 0,0002). Le signal oculaire se transfère mieux d'une personne à l'autre que l'EEG.
- **H2 confirmée pour la COR** : la fusion ne dépasse pas l'EOG seul de façon significative (+0,021 ; p Holm = 0,80).
- **Point non prévu** : pour le RMSE, la fusion est significativement moins bonne que l'EOG (+0,034 ; p Holm = 0,03). Rapporté sans le masquer.
- **Comparaison avec l'intra-sujet** : les niveaux de COR baissent peu pour l'EOG (0,79 en inter, 0,76 en intra) ; pour l'EEG seul, la baisse est nette en RMSE (0,248 contre 0,151). Le protocole n'est pas strictement identique, donc cette comparaison reste descriptive.
- **Lien avec l'écart à l'article** (hypothèse, non testée) : le protocole intra-sujet de l'article pourrait avantager l'EEG, qui s'ajuste à une personne donnée. L'extension montre que la performance de l'EEG chute fortement pour des personnes nouvelles ; elle ne prouve pas que l'article a surestimé l'EEG.
