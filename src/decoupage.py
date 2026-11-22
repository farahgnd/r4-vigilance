"""Étape 4.1 – Découpage aléatoire des fenêtres contre blocs contigus (preuve de fuite).

Même protocole, même grille v1, mêmes 23 sujets, mêmes modalités (EOG, EEG frontal 2 Hz,
fusion). Seul change le DÉCOUPAGE EXTERNE (5 plis) :
  - contigu  : 5 blocs consécutifs dans le temps (protocole principal) ;
  - aléatoire : 5 plis tirés au hasard parmi les 885 fenêtres (KFold shuffle, graine 42).

Dans le cas aléatoire, les fenêtres voisines (autocorrélation 0,999 à 8 s) se retrouvent
dans l'apprentissage ET dans le test : c'est la fuite à mesurer. La réglage interne reste
contigu dans les deux cas, pour ne mesurer que l'effet du découpage externe.

Produit :
  - results/decoupage_par_sujet.csv : COR et RMSE par sujet, par découpage et modalité ;
  - results/decoupage_comparaisons.csv : écart (aléatoire − contigu), IC bootstrap, Wilcoxon apparié.

Usage : python src/decoupage.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon
from sklearn.model_selection import KFold

from baselines import make_models
from data import list_subjects, load_config, load_subject

MODALITES = {"eog": ["eog"], "eeg_2hz_front": ["eeg_2hz_front"], "eeg_2hz_front+eog": ["eeg_2hz_front", "eog"]}
N_BOOT = 10_000


def cor(a, b) -> float:
    return float(np.corrcoef(a, b)[0, 1])


def rmse(a, b) -> float:
    return float(np.sqrt(np.mean((a - b) ** 2)))


def evaluer(X, y, decoupage) -> tuple[float, float]:
    """COR et RMSE sur les 885 prédictions hors pli, rangées dans l'ordre temporel."""
    pred = np.full(len(y), np.nan)
    for tr, te in decoupage.split(X):
        modele = make_models(42, "v1")["svr_rbf"]
        modele.fit(X[tr], y[tr])
        pred[te] = modele.predict(X[te])
    assert not np.isnan(pred).any()
    return cor(y, pred), rmse(y, pred)


def main():
    cfg = load_config()
    lignes = []
    for s in list_subjects(cfg):
        for nom, mods in MODALITES.items():
            X, y = load_subject(cfg, s, mods)
            contigu = KFold(n_splits=5, shuffle=False)
            aleatoire = KFold(n_splits=5, shuffle=True, random_state=42)
            c_cor, c_rmse = evaluer(X, y, contigu)
            a_cor, a_rmse = evaluer(X, y, aleatoire)
            lignes.append({"sujet": s, "modalites": nom,
                           "COR_contigu": c_cor, "RMSE_contigu": c_rmse,
                           "COR_aleatoire": a_cor, "RMSE_aleatoire": a_rmse})
        print(f"{s} ok", flush=True)
    par_sujet = pd.DataFrame(lignes)
    Path("results").mkdir(exist_ok=True)
    par_sujet.to_csv("results/decoupage_par_sujet.csv", index=False)

    rng = np.random.default_rng(42)
    comps = []
    for nom, sous in par_sujet.groupby("modalites", sort=False):
        for metrique in ["COR", "RMSE"]:
            c = sous[f"{metrique}_contigu"].to_numpy()
            a = sous[f"{metrique}_aleatoire"].to_numpy()
            diff = a - c
            idx = rng.integers(0, len(diff), size=(N_BOOT, len(diff)))
            bm = diff[idx].mean(axis=1)
            p = 1.0 if np.all(diff == 0) else float(wilcoxon(a, c).pvalue)
            comps.append({"modalites": nom, "metrique": metrique, "moyenne_contigu": c.mean(),
                          "moyenne_aleatoire": a.mean(), "diff_aleatoire_moins_contigu": diff.mean(),
                          "IC95_bas": np.percentile(bm, 2.5), "IC95_haut": np.percentile(bm, 97.5),
                          "p_wilcoxon": p})
    comp = pd.DataFrame(comps)
    comp.to_csv("results/decoupage_comparaisons.csv", index=False)
    pd.set_option("display.width", 220)
    print(comp.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
