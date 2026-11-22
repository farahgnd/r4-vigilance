"""Étape 3 – Approximation causale de CCRF : lissage des prédictions SVR.

Idée : la vigilance évolue lentement. On lisse la sortie de la SVR avec une moyenne
des prédictions PASSÉES et COURANTES seulement (fenêtre causale de longueur 7, comme
la longueur de séquence n = 7 de l'article, p. 9). Cette approximation ne reproduit
pas CCRF, qui modélise la séquence jointement (voir reports/ecarts.md).

Règles anti-fuite :
  - le lissage n'utilise que des PRÉDICTIONS, jamais les labels du bloc ;
  - il est fait à l'intérieur de chaque bloc (session) : aucune prédiction d'un autre
    bloc n'est mélangée. Au début d'un bloc, la fenêtre est plus courte (1 à 6 valeurs) ;
  - la longueur 7 est celle de l'article : elle n'est pas réglée sur le test.

Comparaison : SVR brute contre SVR lissée, sur les MÊMES 23 sujets et les MÊMES plis,
test de Wilcoxon apparié, correction de Holm sur les modalités.

Lit : results/predictions_<modalites>.csv (grille v2, principale).
Produit : results/lissage_causal_par_sujet.csv et results/lissage_causal_comparaisons.csv

Usage :
    python src/lissage_causal.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

LONGUEUR = 7
MODELE = "svr_rbf"
MODALITES = ["eog", "eeg_2hz_front", "eeg_2hz_front+eog"]


def lisser_causal(pred: np.ndarray, longueur: int = LONGUEUR) -> np.ndarray:
    """Moyenne des `longueur` dernières prédictions (courante incluse), dans un bloc."""
    out = np.empty_like(pred, dtype=float)
    for t in range(len(pred)):
        debut = max(0, t - longueur + 1)
        out[t] = pred[debut:t + 1].mean()
    return out


def cor(a, b) -> float:
    return float(np.corrcoef(a, b)[0, 1])


def rmse(a, b) -> float:
    return float(np.sqrt(np.mean((np.asarray(a) - np.asarray(b)) ** 2)))


def main():
    lignes = []
    for mod in MODALITES:
        chemin = Path(f"results/predictions_{mod}.csv")
        if not chemin.exists():
            raise SystemExit(f"Prédictions absentes : {chemin} (lancer src/baselines.py --grille v2)")
        df = pd.read_csv(chemin)
        df = df[df["modele"] == MODELE].sort_values(["sujet", "session", "t"])
        for sujet, sous in df.groupby("sujet", sort=False):
            vrai = sous["y_true"].to_numpy()
            brut = sous["y_pred"].to_numpy()
            # lissage séparé dans chaque session (bloc contigu)
            lisse = np.concatenate([lisser_causal(g["y_pred"].to_numpy())
                                    for _, g in sous.groupby("session", sort=False)])
            lignes.append({
                "modalites": mod, "sujet": sujet,
                "COR_brute": cor(vrai, brut), "RMSE_brute": rmse(vrai, brut),
                "COR_lissee": cor(vrai, lisse), "RMSE_lissee": rmse(vrai, lisse),
            })
    par_sujet = pd.DataFrame(lignes)
    Path("results").mkdir(exist_ok=True)
    par_sujet.to_csv("results/lissage_causal_par_sujet.csv", index=False)

    comps = []
    for mod, sous in par_sujet.groupby("modalites", sort=False):
        for metrique in ["COR", "RMSE"]:
            brute = sous[f"{metrique}_brute"].to_numpy()
            lisse = sous[f"{metrique}_lissee"].to_numpy()
            diff = lisse - brute
            p = 1.0 if np.all(diff == 0) else float(wilcoxon(lisse, brute).pvalue)
            comps.append({"modalites": mod, "metrique": metrique, "n_sujets": len(sous),
                          "moyenne_brute": brute.mean(), "moyenne_lissee": lisse.mean(),
                          "diff_moyenne": diff.mean(), "p_wilcoxon": p})
    comp = pd.DataFrame(comps)
    comp["p_holm"] = np.nan
    for metrique in ["COR", "RMSE"]:
        masque = comp["metrique"] == metrique
        p = comp.loc[masque, "p_wilcoxon"].to_numpy()
        ordre = np.argsort(p)
        m = len(p)
        ajust = np.empty(m)
        courant = 0.0
        for rang, i in enumerate(ordre):
            courant = max(courant, (m - rang) * p[i])
            ajust[i] = min(1.0, courant)
        comp.loc[masque, "p_holm"] = ajust
    comp.to_csv("results/lissage_causal_comparaisons.csv", index=False)

    pd.set_option("display.width", 200)
    print(f"SVR brute contre SVR lissée causale (longueur {LONGUEUR}), 23 sujets, mêmes plis :")
    print(comp.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
