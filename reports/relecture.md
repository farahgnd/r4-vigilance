# Relecture – R4 : estimation de la vigilance (EEG et EOG frontal, SEED-VIG)

Document destiné à une autre équipe qui relit notre travail. Il résume le protocole, les résultats principaux et les points à vérifier. Le détail est dans `reports/protocole.md`, `reports/ecarts.md` et `reports/extension.md`.

## 1. Question et données

- **Question** : peut-on prédire le PERCLOS (fermeture des paupières, 0 à 1) à partir de l'EEG et de l'EOG frontal ? La prédiction vient-elle surtout des signaux oculaires ?
- **Article reproduit** : Zheng et Lu (2017), *J. Neural Eng.* 14 026017. Manuscrit fourni : `reports/article/R4_Zheng2017.pdf`, 16 pages. Les numéros de page cités sont ceux de ce manuscrit.
- **Données** : SEED-VIG, 23 expériences de conduite simulée, 885 fenêtres de 8 s chacune. Les features sont fournies par le jeu de données (non recalculées). Données non redistribuées, hors dépôt.

## 2. Protocole principal (intra-sujet)

1. **Un modèle par sujet** : les 885 fenêtres d'un sujet sont découpées en **5 blocs contigus**, dans l'ordre temporel, sans mélange.
2. **Validation croisée à 5 plis** : 4 blocs pour apprendre, 1 bloc pour tester.
3. **Réglage interne** : `GridSearchCV` sur les 4 blocs d'apprentissage seulement (4 blocs contigus). La normalisation (`StandardScaler`) est aussi apprise sur l'apprentissage.
4. **Modèle** : SVR à noyau RBF. Grille principale (v1) : C ∈ {0,1 ; 1 ; 10}, gamma ∈ {scale ; 0,01 ; 0,001}.
5. **Métriques** : COR et RMSE calculés sur les **885 prédictions hors pli concaténées** (éq. 9-10 de l'article). Résumé : moyenne ± écart-type sur les 23 sujets, IC 95 % bootstrap sur les sujets.
6. **Comparaisons** : tests de Wilcoxon **appariés** sur les 23 sujets (mêmes plis), correction de Holm.

## 3. Résultats principaux (grille v1)

| Modalité | COR | RMSE |
| --- | --- | --- |
| EOG frontal (variante ICA-MINUS) | 0,764 ± 0,193 | 0,126 ± 0,041 |
| EEG frontal 2 Hz (4 canaux) | 0,613 ± 0,265 | 0,151 ± 0,038 |
| Fusion EEG frontal + EOG | 0,775 ± 0,212 | 0,117 ± 0,030 |

Article (manuscrit) : EOG 0,78 / 0,12 ; fusion SVR 0,83 / 0,10 (p. 11). **Notre fusion est en dessous de l'article sur la COR** (0,775 contre 0,83).

**Comparaisons appariées (v1)** : la fusion n'est pas significativement meilleure que l'EOG seul (ΔCOR = +0,011, p Holm = 0,30). L'EEG frontal est significativement moins bon que l'EOG (ΔCOR = −0,15, p Holm = 0,004).

## 4. Analyses de sensibilité et vérifications

- **Grille v2** (plus large, type LIBSVM) : elle dégrade la SVR (fusion 0,732). Présentée comme sensibilité, pas comme résultat principal.
- **Découpage aléatoire** au lieu de blocs contigus : les scores grimpent à COR 0,95 pour l'EOG (contre 0,76). C'est la preuve de la fuite entre fenêtres voisines.
- **Lissage** : `movingAve` est causal (fenêtres passées seulement) ; `LDS` est centré et utilise le futur. Leur impact n'est pas significatif.
- **Approximation causale de CCRF** (lissage des prédictions sur 7 fenêtres passées) : elle dégrade légèrement la prédiction. CCRF n'est pas reproduit.
- **Extension inter-sujets** (leave-one-subject-out) : voir `reports/extension.md` pour le plan et les résultats.

## 5. Points à vérifier (pour le relecteur)

1. **Contiguïté des sessions** : l'article dit « five sessions » sans préciser la contiguïté. Nous avons pris des blocs contigus, conformément à la fiche. Si l'article a utilisé autre chose, nos scores ne sont pas comparables (voir le découpage aléatoire ci-dessus).
2. **Grille de réglage** : non publiée dans l'article. Notre grille v1 est un choix, documenté. Les hyperparamètres choisis tombent souvent aux bords de la grille (gamma minimal) : le noyau RBF est presque linéaire.
3. **Variante EOG** : `icav_minh` correspond à la variante ICA-MINUS de l'article. Nous la reprenons sans la re-sélectionner sur nos résultats.
4. **Canaux postérieurs** : 11 canaux disponibles, 12 dans l'article (CPZ absent du jeu de données). Les canaux temporaux (6) correspondent exactement.
5. **Métrique** : RMSE calculé sur les 885 prédictions concaténées. Une moyenne des RMSE par pli donnerait une valeur plus basse d'environ 0,01 ; le manuscrit ne précise pas l'agrégation.
6. **Lissage `movingAve`** : absent de la description de l'article, ajouté par le jeu de données. Les features non lissées ne sont pas fournies.
7. **Fusion 5 bandes** : résultat exploratoire (non prévu au protocole). Ne pas la présenter comme résultat principal.
8. **Temps de calcul** : le temps enregistré pour `eeg_5b_front` (grille v2) est de 4 h 33 : anomalie d'horloge, non vérifiée.
9. **Tests** : 23 sujets seulement ; les non-significatifs ne prouvent pas l'absence d'effet.

## 6. Reproduire

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python src/verifier_donnees.py
python src/baselines.py --modalities eog --grille v1
python src/baselines.py --modalities eeg_2hz_front --grille v1
python src/baselines.py --modalities eeg_2hz_front eog --grille v1
python src/comparaisons.py --dossier results/grille_v1
```

Les résultats v1 sont écrits dans `results/grille_v1/`. Les résultats de la grille v2 (sensibilité) s'obtiennent avec `--grille v2` et `python src/comparaisons.py` (sans option). Les lissages, le découpage aléatoire et l'extension ont leurs propres scripts (`src/lissage_test.py`, `src/decoupage.py`, `src/extension_loso.py`).

Les versions utilisées sont dans `results/meta_*.json`. Graine : 42.
