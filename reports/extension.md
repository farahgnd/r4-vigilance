# Extension – R4 : validation inter-sujets (leave-one-subject-out)

Rédigé **avant tout calcul de l'extension**, le 2026-11-22. Ce document fixe l'hypothèse, la modification, la référence, les métriques et la règle de décision. Il ne sera pas modifié après les calculs ; tout écart sera noté dans une section ajoutée à la fin.

## 1. Question

Le protocole principal est **intra-sujet** : un modèle par personne, entraîné sur les autres blocs de la même personne. Un système réel doit souvent prédire la vigilance d'une **personne nouvelle**, sans calibration. L'extension demande : **le résultat tient-il quand la personne testée n'a jamais été vue ?**

## 2. Hypothèse (fixée avant calcul)

En validation inter-sujets :
- **H1** : l'EOG frontal seul reste **meilleur** que l'EEG frontal seul (COR plus élevée, significativement).
- **H2** : la **fusion** EEG + EOG n'apporte **pas de gain significatif** par rapport à l'EOG seul.

Justification : les signaux oculaires (clignements, saccades) sont plus proches de la cible (PERCLOS calculé à partir des yeux, p. 5) et moins dépendants de l'individu que l'EEG, dont l'amplitude et la topographie varient fortement d'une personne à l'autre. L'article le reconnaît comme limite : « Due to individual differences of neurophysiological signals across subjects, the performance of vigilance estimation models may be dramatically degraded » (p. 13).

## 3. Modification du protocole

| Élément | Protocole principal (intra-sujet) | Extension (inter-sujets) |
| --- | --- | --- |
| Données d'apprentissage | 4 blocs (~708 fenêtres) du même sujet | **22 sujets entiers** (19 470 fenêtres) |
| Données de test | 1 bloc (177 fenêtres) du même sujet | **le sujet entier**, 885 fenêtres |
| Découpage externe | 5 blocs contigus par sujet | **Leave-one-subject-out** : 23 plis, un par sujet |
| Réglage interne | 4 blocs contigus du même sujet | **GroupKFold par sujet** : 5 groupes de sujets disjoints dans l'apprentissage ; un sujet n'apparaît jamais dans deux groupes |
| Grille SVR | v1 (principale) | **v1** (même grille, pour comparer) |
| Normalisation | StandardScaler appris sur l'apprentissage | Idem, appris sur les 22 sujets d'apprentissage seulement |
| Modèle | SVR RBF | SVR RBF (seul modèle, pas de Ridge) |
| Modalités | EOG, EEG frontal 2 Hz, fusion | **Idem** |

**Rien ne fuit entre sujets** : le sujet testé n'est jamais dans l'apprentissage, ni dans le réglage interne, ni dans la normalisation.

**Plan de repli** : si le temps de calcul d'un pli dépasse 5 minutes après mesure sur le premier pli, on sous-échantillonne les fenêtres d'apprentissage d'un facteur 4 (une fenêtre sur quatre), et on le déclare. Le test reste sur les 885 fenêtres complètes. Ce repli est décidé ici, avant calcul.

## 4. Référence de comparaison

Les résultats **intra-sujet** de la grille v1 (`results/grille_v1/tableau_principal.csv`, `results/grille_v1/comparaisons_appariees.csv`), sur les **mêmes 23 sujets** et les **mêmes modalités**.

Les deux protocoles ne sont pas strictement comparables (données d'apprentissage très différentes). La comparaison des niveaux de performance est donc **descriptive** ; les tests de H1 et H2 portent uniquement sur les comparaisons **inter-sujets** entre modalités.

## 5. Métriques

Pour chaque sujet testé (les 23 sujets sont des « sujets testés », un par pli) :
- **COR** : corrélation entre les 885 prédictions et les 885 labels de ce sujet ;
- **RMSE** : éq. 9 de l'article, sur les 885 prédictions de ce sujet.

Résumé : moyenne ± écart-type sur les 23 sujets, IC 95 % par bootstrap sur les sujets (10 000 rééchantillonnages, graine 42).

## 6. Test et règle de décision

**Test** : Wilcoxon signé apparié sur les 23 sujets testés, pour chaque paire :
1. EEG frontal vs EOG (H1) ;
2. fusion vs EOG (H2) ;
3. fusion vs EEG frontal (information).

**Correction** : Holm sur les 3 comparaisons, séparément pour COR et RMSE. Seuil α = 0,05.

**Règle de décision**, fixée avant calcul :
- **H1 confirmée** si, pour la COR, EEG − EOG < 0 **et** p_Holm < 0,05.
- **H1 infirmée** si la COR de l'EEG est significativement **supérieure** à celle de l'EOG (p_Holm < 0,05, différence positive).
- **H1 indécise** sinon.
- **H2 confirmée** si la différence fusion − EOG pour la COR n'est pas significative (p_Holm ≥ 0,05).
- **H2 infirmée** si la fusion est significativement meilleure que l'EOG (p_Holm < 0,05, différence positive).

**Précision** : un résultat non significatif **n'est pas la preuve** que l'effet est nul. Avec 23 sujets, la puissance est limitée. On écrira « non significatif », jamais « pas d'effet ».

## 7. Ce qui ne sera pas fait

- Aucun réglage sur les scores de test inter-sujets : la grille est v1, comme dans le protocole principal.
- Aucune sélection de modalité ou de variante après avoir vu les résultats.
- Pas de nouvelle variante de lissage dans l'extension (`movingAve` seul).
