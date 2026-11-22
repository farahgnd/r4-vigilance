"""Étape 3 – Effet du choix de métrique sur le RMSE (sans réentraîner).

Le code de l'étape 2 calculait le RMSE comme la moyenne des RMSE par pli. Le protocole
(amendé, reports/protocole.md) calcule le RMSE sur les 885 prédictions concaténées
(éq. 9 de l'article). Ce script mesure l'écart entre les deux, à partir des prédictions
sauvegardées (session par session), pour la SVR, dans les deux grilles.

Produit : results/effet_metrique.csv
Usage :  python src/effet_metrique.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

MODALITES = ["eog", "eeg_2hz_front", "eeg_2hz_front+eog"]
DOSSIERS = {"v2": Path("results"), "v1": Path("results/grille_v1")}


def rmse(a, b) -> float:
    return float(np.sqrt(np.mean((np.asarray(a) - np.asarray(b)) ** 2)))


def main():
    lignes = []
    for grille, dossier in DOSSIERS.items():
        for mod in MODALITES:
            chemin = dossier / f"predictions_{mod}.csv"
            if not chemin.exists():
                print(f"(absent : {chemin})")
                continue
            df = pd.read_csv(chemin)
            df = df[df["modele"] == "svr_rbf"]
            concat, par_pli = [], []
            for sujet, sous in df.groupby("sujet"):
                concat.append(rmse(sous["y_true"], sous["y_pred"]))  # 885 valeurs
                par_pli.append(np.mean([rmse(g["y_true"], g["y_pred"])
                                        for _, g in sous.groupby("session")]))  # moyenne des 5 plis
            lignes.append({"grille": grille, "modalites": mod,
                           "RMSE_concatene_moyenne": np.mean(concat),
                           "RMSE_moyenne_des_plis": np.mean(par_pli),
                           "ecart": np.mean(par_pli) - np.mean(concat)})
    res = pd.DataFrame(lignes)
    res.to_csv("results/effet_metrique.csv", index=False)
    print(res.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
