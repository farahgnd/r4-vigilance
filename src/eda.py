"""Étape 2 – Analyse exploratoire des LABELS (PERCLOS), sans modèle.

Pourquoi : justifier le découpage en blocs contigus (fenêtres voisines très corrélées)
et voir la forme de la cible. On n'utilise que les labels : aucun résultat de modèle,
aucun réglage. Les tableaux sont écrits dans results/ et les figures dans figures/.

Produit :
  - results/eda_perclos_par_sujet.csv : moyenne, écart-type, min, max, pente par expérience ;
  - results/eda_autocorrelation.csv   : autocorrélation moyenne sur les 23 expériences,
                                        pour des décalages de 1 à 20 fenêtres (1 fenêtre = 8 s) ;
  - figures/eda_distribution.png      : distribution du PERCLOS ;
  - figures/eda_evolution.png         : évolution dans le temps, quelques sujets ;
  - figures/eda_autocorrelation.png   : autocorrélation moyenne.

Usage :
    python src/eda.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # figures écrites dans un fichier, pas d'affichage
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from data import list_subjects, load_config, lire_labels

MAX_LAG = 20  # en fenêtres ; 1 fenêtre = 8 s, donc 20 fenêtres = 160 s


def autocorr(y: np.ndarray, lag: int) -> float:
    """Corrélation entre y(t) et y(t + lag)."""
    return float(np.corrcoef(y[:-lag], y[lag:])[0, 1])


def main():
    cfg = load_config()
    Path("results").mkdir(exist_ok=True)
    Path("figures").mkdir(exist_ok=True)
    subjects = list_subjects(cfg)

    labels = {s: lire_labels(cfg, s) for s in subjects}

    # 1) Statistiques par expérience
    rows = []
    for s, y in labels.items():
        t = np.arange(len(y))
        pente = float(np.polyfit(t, y, 1)[0]) * len(y)  # variation sur toute l'expérience
        rows.append({"experience": s, "moyenne": y.mean(), "ecart_type": y.std(ddof=1),
                     "min": y.min(), "max": y.max(), "variation_totale": pente})
    stats = pd.DataFrame(rows)
    stats.to_csv("results/eda_perclos_par_sujet.csv", index=False)

    # 2) Autocorrélation par décalage, puis moyenne sur les expériences
    acf = pd.DataFrame({
        lag: [autocorr(y, lag) for y in labels.values()] for lag in range(1, MAX_LAG + 1)
    })
    acf_moy = acf.mean()
    acf_ec = acf.std(ddof=1)
    pd.DataFrame({"decalage_fenetres": acf_moy.index, "decalage_s": acf_moy.index * 8,
                  "acf_moyenne": acf_moy.values, "acf_ecart_type": acf_ec.values}
                 ).to_csv("results/eda_autocorrelation.csv", index=False)

    # Figures
    toutes = np.concatenate(list(labels.values()))
    part_sature = float(np.mean(toutes >= 0.99))  # fenêtres quasi égales à 1 (plafond du label)
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    ax.hist(toutes, bins=50, color="#4C72B0")
    ax.axvline(1.0, color="#C44E52", lw=0.8, ls="--")
    ax.text(0.97, ax.get_ylim()[1] * 0.80, f"{part_sature:.1%} des fenêtres\n≥ 0,99 (plafond)",
            ha="right", fontsize=8, color="#C44E52")
    ax.set_xlabel("PERCLOS (labels, 23 expériences)")
    ax.set_ylabel("Nombre de fenêtres")
    ax.set_title("Distribution du PERCLOS", fontsize=11)
    fig.tight_layout(); fig.savefig("figures/eda_distribution.png", dpi=150); plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 4.2))
    for s in subjects[:5]:  # quelques expériences pour lisibilité
        ax.plot(np.arange(len(labels[s])) * 8 / 60, labels[s], lw=0.8, label=s.replace(".mat", ""))
    ax.set_xlabel("Temps (minutes)")
    ax.set_ylabel("PERCLOS")
    ax.set_title("Évolution du PERCLOS dans le temps (5 expériences)", fontsize=11)
    ax.legend(fontsize=7, loc="upper left", bbox_to_anchor=(1.01, 1.0), frameon=False)
    fig.tight_layout(); fig.savefig("figures/eda_evolution.png", dpi=150); plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.errorbar(acf_moy.index * 8, acf_moy.values, yerr=acf_ec.values, marker="o", ms=3, capsize=2)
    ax.axhline(0, color="grey", lw=0.6)
    ax.set_xlabel("Décalage (secondes)")
    ax.set_ylabel("Autocorrélation du PERCLOS")
    ax.set_title("Autocorrélation moyenne (± écart-type sur 23 expériences)")
    fig.tight_layout(); fig.savefig("figures/eda_autocorrelation.png", dpi=150); plt.close(fig)

    print(f"{len(subjects)} expériences ; PERCLOS moyen : {stats['moyenne'].mean():.3f}")
    print(f"Fenêtres avec PERCLOS >= 0,99 (plafond) : {part_sature:.1%}")
    print("Autocorrélation moyenne : lag 1 (8 s) = {:.3f}, lag 5 (40 s) = {:.3f}, lag 20 (160 s) = {:.3f}".format(
        acf_moy[1], acf_moy[5], acf_moy[20]))
    print("Tableaux : results/eda_perclos_par_sujet.csv, results/eda_autocorrelation.csv")


if __name__ == "__main__":
    main()
