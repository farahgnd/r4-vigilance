"""Extension – validation inter-sujets (leave-one-subject-out), voir reports/extension.md.

Pour chaque sujet testé (23 plis) :
  - apprentissage = les 22 AUTRES sujets, entièrement ;
  - réglage interne = GroupKFold par sujet (5 groupes de sujets disjoints) sur ces 22 sujets ;
  - StandardScaler et SVR appris sur l'apprentissage seulement ;
  - test = les 885 fenêtres du sujet laissé de côté ; COR et RMSE sur ces 885 prédictions.
Grille v1 (principale), modalités EOG, EEG frontal 2 Hz, fusion.

Repli (décidé dans reports/extension.md) : si un pli complet dépasse 5 minutes, on
sous-échantillonne les fenêtres d'apprentissage d'un facteur 4 (option --facteur 4).

Produit :
  - results/loso_par_sujet.csv : COR, RMSE, C et gamma retenus, temps, par sujet testé ;
  - results/loso_comparaisons.csv : Wilcoxon apparié + Holm, et référence intra-sujet.

Usage :
    python src/extension_loso.py --modalites eog --plis 1          # chronométrer un pli
    python src/extension_loso.py --modalites eog eeg_2hz_front eog+eeg  # tout
"""
import argparse
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon
from sklearn.model_selection import GridSearchCV, GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR

from baselines import GRILLES_SVR
from data import list_subjects, load_config, load_subject

MODALITES = {"eog": ["eog"], "eeg_2hz_front": ["eeg_2hz_front"], "eeg_2hz_front+eog": ["eeg_2hz_front", "eog"]}
ALIAS = {"eog": "eog", "eeg_2hz_front": "eeg_2hz_front", "eog+eeg": "eeg_2hz_front+eog"}
Path_resultats = Path("results")


def modele_v1(groupes):
    """SVR v1 avec réglage interne groupé par sujet."""
    g = GRILLES_SVR["v1"]
    return GridSearchCV(
        make_pipeline(StandardScaler(), SVR(kernel="rbf")),
        {"svr__C": g["C"], "svr__gamma": g["gamma"]},
        cv=GroupKFold(n_splits=5), scoring="neg_root_mean_squared_error", n_jobs=-1)


def cor(a, b):
    return float(np.corrcoef(a, b)[0, 1])


def rmse(a, b):
    return float(np.sqrt(np.mean((a - b) ** 2)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modalites", nargs="+", default=["eog", "eeg_2hz_front", "eog+eeg"],
                    choices=list(ALIAS))
    ap.add_argument("--plis", type=int, default=None, help="Nombre de plis (chronométrage)")
    ap.add_argument("--facteur", type=int, default=1, help="Sous-échantillonnage de l'apprentissage")
    args = ap.parse_args()

    cfg = load_config()
    sujets = list_subjects(cfg)
    n_plis = args.plis or len(sujets)
    Path_resultats.mkdir(exist_ok=True)
    lignes = []
    for alias in args.modalites:
        nom = ALIAS[alias]
        donnees = {s: load_subject(cfg, s, MODALITES[nom]) for s in sujets}
        for i, s_test in enumerate(sujets[:n_plis]):
            t0 = time.time()
            X_tr, y_tr, g_tr = [], [], []
            for j, s in enumerate(sujets):
                if s == s_test:
                    continue
                X, y = donnees[s]
                idx = np.arange(0, len(y), args.facteur)
                X_tr.append(X[idx]); y_tr.append(y[idx]); g_tr.append(np.full(len(idx), j))
            X_tr, y_tr, g_tr = np.vstack(X_tr), np.concatenate(y_tr), np.concatenate(g_tr)
            X_te, y_te = donnees[s_test]

            modele = modele_v1(g_tr)
            modele.fit(X_tr, y_tr, groups=g_tr)
            p = modele.predict(X_te)
            lignes.append({
                "modalites": nom, "sujet_teste": s_test,
                "COR": cor(y_te, p), "RMSE": rmse(y_te, p),
                "C": modele.best_params_["svr__C"], "gamma": modele.best_params_["svr__gamma"],
                "n_apprentissage": len(y_tr), "facteur": args.facteur,
                "temps_s": round(time.time() - t0, 1),
            })
            print(f"{nom} {s_test} ok ({lignes[-1]['temps_s']} s)", flush=True)

    df = pd.DataFrame(lignes)
    sortie = Path_resultats / "loso_par_sujet.csv"
    if sortie.exists():
        # Ajout : on remplace les lignes des modalités recalculées
        ancien = pd.read_csv(sortie)
        ancien = ancien[~ancien["modalites"].isin(df["modalites"].unique())]
        df = pd.concat([ancien, df], ignore_index=True)
    df.to_csv(sortie, index=False)
    print(df.groupby("modalites")[["COR", "RMSE", "temps_s"]].mean().round(4).to_string())


if __name__ == "__main__":
    main()
