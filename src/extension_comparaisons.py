"""Extension – comparaisons appariées inter-sujets et référence intra-sujet.

Lit results/loso_par_sujet.csv (leave-one-subject-out) et results/grille_v1/baselines_*.csv
(référence intra-sujet, grille v1, SVR). Ne réentraîne rien.

Règle de décision : reports/extension.md, section 6.
  - Tests de Wilcoxon appariés sur les 23 sujets testés, puis correction de Holm
    (3 comparaisons, séparément pour COR et RMSE).

Produit :
  - results/extension_resume.csv : moyenne, écart-type et IC 95 % par modalité, inter et intra ;
  - results/extension_comparaisons.csv : Wilcoxon + Holm pour H1 et H2 et la comparaison
    fusion vs EEG.

Usage : python src/extension_comparaisons.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

N_BOOT = 10_000
SEED = 42
ALPHA = 0.05
NOMS_INTRA = {"eog": "eog", "eeg_2hz_front": "eeg_2hz_front", "eeg_2hz_front+eog": "eeg_2hz_front+eog"}


def ic(valeurs: np.ndarray, rng) -> tuple[float, float]:
    idx = rng.integers(0, len(valeurs), size=(N_BOOT, len(valeurs)))
    m = valeurs[idx].mean(axis=1)
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def holm(p: np.ndarray) -> np.ndarray:
    m = len(p)
    ordre = np.argsort(p)
    ajust = np.empty(m)
    courant = 0.0
    for rang, i in enumerate(ordre):
        courant = max(courant, (m - rang) * p[i])
        ajust[i] = min(1.0, courant)
    return ajust


def main():
    rng = np.random.default_rng(SEED)
    inter = pd.read_csv("results/loso_par_sujet.csv")
    intra = pd.concat([pd.read_csv(f"results/grille_v1/baselines_{m}.csv") for m in NOMS_INTRA.values()])
    intra = intra[intra["modele"] == "svr_rbf"]

    # Résumé descriptif
    lignes = []
    for mod in NOMS_INTRA:
        for protocole, df in [("inter-sujets (LOSO)", inter), ("intra-sujet (référence)", intra)]:
            sous = df[df["modalites"] == mod]
            if len(sous) == 0:
                continue
            for m in ["COR", "RMSE"]:
                v = sous[m].to_numpy()
                lo, hi = ic(v, rng)
                lignes.append({"modalites": mod, "protocole": protocole, "metrique": m,
                               "n_sujets": len(v), "moyenne": v.mean(), "ecart_type": v.std(ddof=1),
                               "IC95_bas": lo, "IC95_haut": hi})
    resume = pd.DataFrame(lignes)
    resume.to_csv("results/extension_resume.csv", index=False)

    # Comparaisons appariées inter-sujets (H1, H2, information)
    paires = [("eeg_2hz_front", "eog", "H1 : EEG frontal vs EOG"),
              ("eeg_2hz_front+eog", "eog", "H2 : fusion vs EOG"),
              ("eeg_2hz_front+eog", "eeg_2hz_front", "Info : fusion vs EEG frontal")]
    comps = []
    for a, b, libelle in paires:
        da = inter[inter["modalites"] == a].set_index("sujet_teste").sort_index()
        db = inter[inter["modalites"] == b].set_index("sujet_teste").sort_index()
        for m in ["COR", "RMSE"]:
            x, y = da[m].to_numpy(), db[m].to_numpy()
            diff = x - y
            p = 1.0 if np.all(diff == 0) else float(wilcoxon(x, y).pvalue)
            comps.append({"comparaison": libelle, "a": a, "b": b, "metrique": m,
                          "n_sujets": len(x), "diff_a_moins_b": diff.mean(),
                          "n_sujets_a_meilleur": int((diff > 0).sum() if m == "COR" else (diff < 0).sum()),
                          "p_wilcoxon": p})
    comp = pd.DataFrame(comps)
    comp["p_holm"] = np.nan
    for m in ["COR", "RMSE"]:
        masque = comp["metrique"] == m
        comp.loc[masque, "p_holm"] = holm(comp.loc[masque, "p_wilcoxon"].to_numpy())
    comp["significatif_5pct"] = comp["p_holm"] < ALPHA
    comp.to_csv("results/extension_comparaisons.csv", index=False)

    pd.set_option("display.width", 220)
    print("Résumé :")
    print(resume.round(4).to_string(index=False))
    print("\nComparaisons appariées inter-sujets :")
    print(comp.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
