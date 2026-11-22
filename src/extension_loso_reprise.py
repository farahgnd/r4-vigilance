"""Extension LOSO – version avec sauvegarde après CHAQUE pli (reprise possible).

Même protocole que src/extension_loso.py (voir reports/extension.md) :
  leave-one-subject-out, réglage interne GroupKFold par sujet, grille v1, SVR RBF.

Différence : après chaque pli, une ligne est ajoutée à results/loso_plis.csv (écriture
immédiate). Au démarrage, les couples (modalité, sujet) déjà présents sont SAUTÉS. Une
coupure de calcul ne fait donc perdre que le pli en cours.

Usage :
    python src/extension_loso_reprise.py --modalites eog eeg_2hz_front eog+eeg

Ce fichier ne modifie pas extension_loso.py. Pour assembler le résultat final, les lignes
de results/loso_plis.csv sont lues par src/extension_comparaisons.py après conversion.
"""
import argparse
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import GridSearchCV, GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR

from baselines import GRILLES_SVR
from data import list_subjects, load_config, load_subject

MODALITES = {"eog": ["eog"], "eeg_2hz_front": ["eeg_2hz_front"], "eeg_2hz_front+eog": ["eeg_2hz_front", "eog"]}
ALIAS = {"eog": "eog", "eeg_2hz_front": "eeg_2hz_front", "eog+eeg": "eeg_2hz_front+eog"}
SORTIE = Path("results/loso_plis.csv")
COLONNES = ["modalites", "sujet_teste", "COR", "RMSE", "C", "gamma", "n_apprentissage", "facteur", "temps_s"]


def deja_faits() -> set:
    if not SORTIE.exists():
        return set()
    df = pd.read_csv(SORTIE)
    return set(zip(df["modalites"], df["sujet_teste"]))


def ajouter_ligne(ligne: dict) -> None:
    entete = not SORTIE.exists()
    pd.DataFrame([ligne], columns=COLONNES).to_csv(SORTIE, mode="a", header=entete, index=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modalites", nargs="+", default=["eog", "eeg_2hz_front", "eog+eeg"], choices=list(ALIAS))
    args = ap.parse_args()

    cfg = load_config()
    sujets = list_subjects(cfg)
    SORTIE.parent.mkdir(exist_ok=True)
    faits = deja_faits()
    print(f"Plis déjà sauvegardés : {len(faits)} (sautés)", flush=True)

    g = GRILLES_SVR["v1"]
    for alias in args.modalites:
        nom = ALIAS[alias]
        donnees = {s: load_subject(cfg, s, MODALITES[nom]) for s in sujets}
        for j_test, s_test in enumerate(sujets):
            if (nom, s_test) in faits:
                continue
            t0 = time.time()
            X_tr, y_tr, g_tr = [], [], []
            for j, s in enumerate(sujets):
                if s == s_test:
                    continue
                X, y = donnees[s]
                X_tr.append(X); y_tr.append(y); g_tr.append(np.full(len(y), j))
            X_tr, y_tr, g_tr = np.vstack(X_tr), np.concatenate(y_tr), np.concatenate(g_tr)
            X_te, y_te = donnees[s_test]

            modele = GridSearchCV(
                make_pipeline(StandardScaler(), SVR(kernel="rbf")),
                {"svr__C": g["C"], "svr__gamma": g["gamma"]},
                cv=GroupKFold(n_splits=5), scoring="neg_root_mean_squared_error", n_jobs=-1)
            modele.fit(X_tr, y_tr, groups=g_tr)
            p = modele.predict(X_te)
            ligne = {
                "modalites": nom, "sujet_teste": s_test,
                "COR": float(np.corrcoef(y_te, p)[0, 1]),
                "RMSE": float(np.sqrt(np.mean((y_te - p) ** 2))),
                "C": modele.best_params_["svr__C"], "gamma": modele.best_params_["svr__gamma"],
                "n_apprentissage": len(y_tr), "facteur": 1,
                "temps_s": round(time.time() - t0, 1),
            }
            ajouter_ligne(ligne)  # sauvegarde immédiate
            faits.add((nom, s_test))
            print(f"{nom} {s_test} sauvegardé ({ligne['temps_s']} s)", flush=True)


if __name__ == "__main__":
    main()
