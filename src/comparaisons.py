"""Étape 2 – Tableau principal et comparaisons appariées entre modalités.

Lit les résultats sauvegardés par src/baselines.py (results/baselines_<modalites>.csv)
et ne réentraîne rien.

Pour chaque modalité et chaque modèle :
  - moyenne et écart-type de COR et RMSE sur les sujets ;
  - intervalle de confiance à 95 % de la moyenne, par bootstrap sur les sujets
    (10 000 rééchantillonnages, graine 42).

Comparaisons appariées (même sujet, mêmes 5 plis) :
  - test de Wilcoxon signé sur les 23 sujets ;
  - correction de Holm sur les comparaisons, séparément pour COR et RMSE.

Produit :
  - results/tableau_principal.csv
  - results/comparaisons_appariees.csv

Usage :
    python src/comparaisons.py --dossier results/grille_v1   (résultat principal, grille v1)
    python src/comparaisons.py                              (sensibilité, grille v2)
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

MODELE_PRINCIPAL = "svr_rbf"
DOSSIER = Path("results")  # remplacé par --dossier
N_BOOT = 10_000
SEED = 42
ALPHA = 0.05

# Modalités principales (protocole) puis secondaires
MODALITES = [
    "eog",
    "eeg_2hz_front",
    "eeg_2hz_front+eog",
    "eeg_2hz_post",
    "eeg_2hz_temp",
    "eeg_5b_front",
    "eeg_5b_front+eog",
    "eeg_5b_post",
    "eeg_5b_temp",
]

# Comparaisons appariées prévues dans reports/protocole.md, section 7
PAIRES = [
    ("eeg_2hz_front+eog", "eog"),         # fusion vs EOG seul
    ("eeg_2hz_front+eog", "eeg_2hz_front"),  # fusion vs EEG frontal seul
    ("eeg_2hz_front", "eog"),             # EEG frontal vs EOG seul
    ("eeg_2hz_post", "eog"),              # secondaire : EEG postérieur vs EOG
]


def charger(modalite: str) -> pd.DataFrame:
    chemin = DOSSIER / f"baselines_{modalite}.csv"
    if not chemin.exists():
        raise SystemExit(f"Résultat absent : {chemin} (lancer src/baselines.py)")
    return pd.read_csv(chemin)


def ic_bootstrap(valeurs: np.ndarray, rng: np.random.Generator) -> tuple[float, float]:
    """IC 95 % de la moyenne, bootstrap sur les sujets."""
    valeurs = valeurs[~np.isnan(valeurs)]
    idx = rng.integers(0, len(valeurs), size=(N_BOOT, len(valeurs)))
    moyennes = valeurs[idx].mean(axis=1)
    return float(np.percentile(moyennes, 2.5)), float(np.percentile(moyennes, 97.5))


def holm(pvals: list[float]) -> list[float]:
    """Correction de Holm (ajustée, monotone)."""
    m = len(pvals)
    ordre = np.argsort(pvals)
    ajustees = np.empty(m)
    courant = 0.0
    for rang, i in enumerate(ordre):
        courant = max(courant, (m - rang) * pvals[i])
        ajustees[i] = min(1.0, courant)
    return ajustees.tolist()


def main():
    global DOSSIER
    ap = argparse.ArgumentParser()
    ap.add_argument("--dossier", default="results", help="results (grille v2) ou results/grille_v1")
    DOSSIER = Path(ap.parse_args().dossier)
    rng = np.random.default_rng(SEED)
    donnees = {}
    lignes_tableau = []

    for mod in MODALITES:
        if not (DOSSIER / f"baselines_{mod}.csv").exists():
            print(f"(ignoré : pas de résultat pour {mod})")
            continue
        df = charger(mod)
        donnees[mod] = df
        for modele, sous in df.groupby("modele"):
            cor = sous["COR"].to_numpy()
            rmse = sous["RMSE"].to_numpy()
            lo_c, hi_c = ic_bootstrap(cor, rng)
            lo_r, hi_r = ic_bootstrap(rmse, rng)
            lignes_tableau.append({
                "modalites": mod, "modele": modele, "n_sujets": len(sous),
                "n_features": int(sous["n_features"].iloc[0]),
                "COR_moyenne": cor.mean(), "COR_ecart_type": cor.std(ddof=1),
                "COR_IC95_bas": lo_c, "COR_IC95_haut": hi_c,
                "RMSE_moyenne": rmse.mean(), "RMSE_ecart_type": rmse.std(ddof=1),
                "RMSE_IC95_bas": lo_r, "RMSE_IC95_haut": hi_r,
            })
    tableau = pd.DataFrame(lignes_tableau)
    Path("results").mkdir(exist_ok=True)
    tableau.to_csv(DOSSIER / "tableau_principal.csv", index=False)

    # Comparaisons appariées sur le modèle principal (SVR)
    comparaisons = []
    for a, b in PAIRES:
        if a not in donnees or b not in donnees:
            print(f"(comparaison {a} vs {b} ignorée : résultat manquant)")
            continue
        da = donnees[a][donnees[a]["modele"] == MODELE_PRINCIPAL].set_index("sujet")
        db = donnees[b][donnees[b]["modele"] == MODELE_PRINCIPAL].set_index("sujet")
        sujets = da.index.intersection(db.index)  # appariement par sujet
        for metrique in ["COR", "RMSE"]:
            x, y = da.loc[sujets, metrique].to_numpy(), db.loc[sujets, metrique].to_numpy()
            diff = x - y
            # Wilcoxon signé : on ignore les différences nulles
            if np.all(diff == 0):
                p = 1.0
            else:
                p = float(wilcoxon(x, y, zero_method="wilcox").pvalue)
            comparaisons.append({"comparaison": f"{a} vs {b}", "metrique": metrique,
                                 "n_sujets": len(sujets), "diff_moyenne": diff.mean(),
                                 "diff_mediane": float(np.median(diff)),
                                 "n_sujets_a_meilleur": int((diff > 0).sum() if metrique == "COR"
                                                            else (diff < 0).sum()),
                                 "p_wilcoxon": p})
    comp = pd.DataFrame(comparaisons)
    if len(comp):
        # Holm séparément pour COR et RMSE
        comp["p_holm"] = np.nan
        for metrique in ["COR", "RMSE"]:
            masque = comp["metrique"] == metrique
            comp.loc[masque, "p_holm"] = holm(comp.loc[masque, "p_wilcoxon"].tolist())
        comp["significatif_holm_5pct"] = comp["p_holm"] < ALPHA
    comp.to_csv(DOSSIER / "comparaisons_appariees.csv", index=False)

    pd.set_option("display.width", 200)
    print("Tableau principal (SVR, moyenne et IC 95 % sur les sujets) :")
    sv = tableau[tableau["modele"] == MODELE_PRINCIPAL]
    print(sv[["modalites", "n_features", "COR_moyenne", "COR_ecart_type", "RMSE_moyenne", "RMSE_ecart_type"]]
          .round(4).to_string(index=False))
    print("\nComparaisons appariées (Wilcoxon, correction de Holm) :")
    if len(comp):
        print(comp[["comparaison", "metrique", "diff_moyenne", "n_sujets_a_meilleur", "p_wilcoxon", "p_holm",
                    "significatif_holm_5pct"]].round(4).to_string(index=False))


if __name__ == "__main__":
    main()
