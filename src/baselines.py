"""Étape 2 – Baselines avec un protocole propre.

Protocole (reproduit celui de l'article, section 2.4) :
  - un modèle par sujet (intra-sujet) ;
  - les 885 fenêtres d'un sujet sont coupées en 5 BLOCS CONTIGUS dans le temps
    (pas de mélange aléatoire, pour éviter la fuite entre fenêtres voisines) ;
  - validation croisée à 5 plis : 4 blocs pour apprendre, 1 bloc pour tester ;
  - normalisation et réglage des hyperparamètres appris sur l'apprentissage SEULEMENT
    (Pipeline + GridSearchCV interne, lui aussi par blocs) ;
  - COR calculée sur les 5 blocs de test concaténés (comme l'article),
    RMSE moyen ; résultat = moyenne et écart-type sur les sujets.

Usage :
    python src/baselines.py --modalities eog
    python src/baselines.py --modalities eeg_2hz
    python src/baselines.py --modalities eeg_2hz eog
"""
import argparse
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import GridSearchCV, KFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR

from data import list_subjects, load_config, load_subject


def make_models(seed: int) -> dict:
    inner = KFold(n_splits=4, shuffle=False)  # réglage interne, lui aussi par blocs
    return {
        "moyenne": make_pipeline(DummyRegressor(strategy="mean")),
        "ridge": GridSearchCV(
            make_pipeline(StandardScaler(), Ridge()),
            {"ridge__alpha": [0.1, 1, 10, 100, 1000]},
            cv=inner, scoring="neg_root_mean_squared_error"),
        "svr_rbf": GridSearchCV(
            make_pipeline(StandardScaler(), SVR(kernel="rbf")),
            {"svr__C": [0.1, 1, 10], "svr__gamma": ["scale", 0.01, 0.001]},
            cv=inner, scoring="neg_root_mean_squared_error"),
    }


def cor(a, b) -> float:
    if np.std(a) == 0 or np.std(b) == 0:
        return float("nan")  # prédiction constante (ex. baseline moyenne)
    return float(np.corrcoef(a, b)[0, 1])


def run_subject(X, y, models, n_folds):
    outer = KFold(n_splits=n_folds, shuffle=False)  # 5 blocs contigus
    out = {}
    for name, model in models.items():
        y_true, y_pred, rmses = [], [], []
        for tr, te in outer.split(X):
            model.fit(X[tr], y[tr])
            p = model.predict(X[te])
            y_true.append(y[te]); y_pred.append(p)
            rmses.append(np.sqrt(np.mean((y[te] - p) ** 2)))
        yt, yp = np.concatenate(y_true), np.concatenate(y_pred)
        out[name] = {"COR": cor(yt, yp), "RMSE": float(np.mean(rmses)), "y_true": yt, "y_pred": yp}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/config.json")
    ap.add_argument("--modalities", nargs="+", default=["eog"])
    ap.add_argument("--max-subjects", type=int, default=None, help="Pour un essai rapide")
    args = ap.parse_args()

    cfg = load_config(args.config)
    np.random.seed(cfg["seed"])
    subjects = list_subjects(cfg)[: args.max_subjects]
    if not subjects:
        raise SystemExit("Aucun sujet trouvé : vérifie data_dir et label_dir dans configs/config.json")
    tag = "+".join(args.modalities)
    print(f"{len(subjects)} sujets | modalités : {tag}")

    rows, preds = [], []
    t0 = time.time()
    for s in subjects:
        X, y = load_subject(cfg, s, args.modalities)
        res = run_subject(X, y, make_models(cfg["seed"]), cfg["n_folds"])
        for model, r in res.items():
            rows.append({"sujet": s, "modele": model, "modalites": tag, "COR": r["COR"], "RMSE": r["RMSE"]})
            preds.append(pd.DataFrame({"sujet": s, "modele": model, "t": np.arange(len(r["y_true"])),
                                       "y_true": r["y_true"], "y_pred": r["y_pred"]}))
        print(f"  {s} ok ({time.time() - t0:.0f} s)")

    df = pd.DataFrame(rows)
    Path("results").mkdir(exist_ok=True)
    df.to_csv(f"results/baselines_{tag}.csv", index=False)
    pd.concat(preds).to_csv(f"results/predictions_{tag}.csv", index=False)

    summary = df.groupby("modele")[["COR", "RMSE"]].agg(["mean", "std"]).round(4)
    print("\nRésultats (moyenne et écart-type sur les sujets) :")
    print(summary)
    print(f"\nTemps total : {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
