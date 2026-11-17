"""Étape 1 – Vérifier TOUS les sujets SEED-VIG (pas seulement un fichier).

Pour chaque expérience (sujet_session, ex. 10_20151125_noon.mat), on vérifie :
  - que le fichier existe dans chaque dossier de features et dans perclos_labels ;
  - la forme (fenêtres, features) de chaque modalité ;
  - que le nombre de fenêtres vaut 885 et correspond aux labels ;
  - les valeurs manquantes (NaN) ou infinies ;
  - la plage du PERCLOS (doit être dans [0, 1]).

Le résultat est écrit dans results/inventaire.csv (une ligne par expérience).

Usage :
    python src/verifier_donnees.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.io import loadmat

from data import list_subjects, load_config

N_FENETRES_ATTENDU = 885


def lire_variable(chemin: Path, cle: str) -> np.ndarray:
    """Lit une variable .mat ; gère le format v7.3 (HDF5) si scipy échoue."""
    try:
        return np.asarray(loadmat(chemin)[cle], dtype=float)
    except NotImplementedError:
        import h5py
        with h5py.File(chemin, "r") as f:
            return np.asarray(f[cle], dtype=float).T  # h5py inverse l'ordre des axes


def main():
    cfg = load_config()
    racine = Path(cfg["data_dir"])
    fichiers = list_subjects(cfg)
    print(f"{len(fichiers)} expériences trouvées dans {cfg['label_dir']}/\n")

    lignes = []
    for fichier in fichiers:
        ligne = {"fichier": fichier}

        # 1) Labels PERCLOS
        y = lire_variable(racine / cfg["label_dir"] / fichier, cfg["label_key"]).ravel()
        ligne["n_labels"] = len(y)
        ligne["perclos_min"] = float(np.nanmin(y))
        ligne["perclos_max"] = float(np.nanmax(y))
        ligne["perclos_nan"] = int(np.isnan(y).sum())

        # 2) Chaque modalité configurée (dossier + clé)
        for nom, spec in cfg["modalities"].items():
            chemin = racine / spec["dir"] / fichier
            if not chemin.exists():
                ligne[f"{nom}_manquant"] = True
                continue
            x = lire_variable(chemin, spec["key"])
            ligne[f"{nom}_forme"] = "x".join(str(d) for d in x.shape)
            ligne[f"{nom}_nan_inf"] = int(np.sum(~np.isfinite(x)))

        lignes.append(ligne)

    df = pd.DataFrame(lignes)
    Path("results").mkdir(exist_ok=True)
    df.to_csv("results/inventaire.csv", index=False)

    # Contrôles et résumé
    print("Fenêtres par expérience (attendu 885) :", sorted(df["n_labels"].unique()))
    print("Plage PERCLOS globale : [{:.4f}, {:.4f}]".format(df["perclos_min"].min(), df["perclos_max"].max()))
    print("NaN dans les labels :", int(df["perclos_nan"].sum()))
    for nom in cfg["modalities"]:
        col = f"{nom}_nan_inf"
        if col in df:
            print(f"NaN/inf dans {nom} : {int(df[col].sum())} | formes : {sorted(df[f'{nom}_forme'].unique())}")
        if f"{nom}_manquant" in df:
            print(f"ATTENTION fichiers manquants pour {nom} : {int(df[f'{nom}_manquant'].sum())}")
    if (df["n_labels"] != N_FENETRES_ATTENDU).any():
        print("ATTENTION : au moins une expérience n'a pas 885 fenêtres.")
    print("\nInventaire écrit dans results/inventaire.csv")


if __name__ == "__main__":
    main()
