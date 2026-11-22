"""Étape 4 – Hyperparamètres retenus à chaque pli, sur 3 sujets seulement.

But : savoir si la validation interne choisit des valeurs AUX BORDS de la grille
(ce qui signale une grille trop étroite ou trop large). Pas de relance des 23 sujets.

Pour chaque grille (v1 principale, v2 sensibilité), chaque modalité (EOG, EEG frontal 2 Hz,
fusion) et chaque pli (5 blocs contigus, comme dans baselines.py), on enregistre le C et le
gamma choisis par GridSearchCV (réglage interne sur l'apprentissage seulement).

Un choix est « au bord » si C ou gamma est la plus petite ou la plus grande valeur numérique
de la grille. `scale` (v1) n'est pas numérique : il n'est jamais compté comme bord.

Produit : results/hyperparametres_3sujets.csv
Usage :   python src/hyperparametres.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import KFold

from baselines import GRILLES_SVR, make_models
from data import list_subjects, load_config, load_subject

N_SUJETS = 3
MODALITES = {"eog": ["eog"], "eeg_2hz_front": ["eeg_2hz_front"], "eeg_2hz_front+eog": ["eeg_2hz_front", "eog"]}


def est_bord(valeur, valeurs_grille) -> bool:
    numeriques = [v for v in valeurs_grille if isinstance(v, (int, float))]
    if not isinstance(valeur, (int, float)) or not numeriques:
        return False
    return valeur in (min(numeriques), max(numeriques))


def main():
    cfg = load_config()
    sujets = list_subjects(cfg)[:N_SUJETS]
    lignes = []
    for grille in ["v1", "v2"]:
        for nom, mods in MODALITES.items():
            for s in sujets:
                X, y = load_subject(cfg, s, mods)
                outer = KFold(n_splits=cfg["n_folds"], shuffle=False)
                for k, (tr, te) in enumerate(outer.split(X), start=1):
                    modele = make_models(cfg["seed"], grille)["svr_rbf"]
                    modele.fit(X[tr], y[tr])
                    p = modele.best_params_
                    C, g = p["svr__C"], p["svr__gamma"]
                    lignes.append({
                        "grille": grille, "modalites": nom, "sujet": s, "pli": k,
                        "C": C, "gamma": g,
                        "C_au_bord": est_bord(C, GRILLES_SVR[grille]["C"]),
                        "gamma_au_bord": est_bord(g, GRILLES_SVR[grille]["gamma"]),
                    })
                print(f"{grille} {nom} {s} ok", flush=True)
    df = pd.DataFrame(lignes)
    Path("results").mkdir(exist_ok=True)
    df.to_csv("results/hyperparametres_3sujets.csv", index=False)

    print("\nPart de plis dont le choix est au bord de la grille :")
    resume = df.groupby(["grille", "modalites"]).agg(
        n_plis=("pli", "size"),
        C_au_bord=("C_au_bord", "mean"),
        gamma_au_bord=("gamma_au_bord", "mean"),
    ).round(3)
    print(resume.to_string())


if __name__ == "__main__":
    main()
