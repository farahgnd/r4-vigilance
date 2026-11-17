"""Étape 2 – Baselines avec un protocole propre.

Protocole (reproduit celui de l'article, section 2.4) :
  - un modèle par sujet (intra-sujet) ;
  - les 885 fenêtres d'un sujet sont coupées en 5 BLOCS CONTIGUS dans le temps
    (pas de mélange aléatoire, pour éviter la fuite entre fenêtres voisines) ;
  - validation croisée à 5 plis : 4 blocs pour apprendre, 1 bloc pour tester ;
  - normalisation et réglage des hyperparamètres appris sur l'apprentissage SEULEMENT
    (Pipeline + GridSearchCV interne, lui aussi par blocs) ;
  - COR et RMSE calculés sur les 885 prédictions hors pli concaténées (article, éq. 9-10) ;
    résultat = moyenne et écart-type sur les sujets (voir reports/protocole.md).

Usage :
    python src/baselines.py --modalities eog
    python src/baselines.py --modalities eeg_2hz_front
    python src/baselines.py --modalities eeg_2hz_front eog
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
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


def rmse(a, b) -> float:
    """Éq. 9 de l'article : racine de l'erreur quadratique moyenne."""
    return float(np.sqrt(np.mean((np.asarray(a) - np.asarray(b)) ** 2)))


def run_subject(X, y, models, n_folds):
    """Renvoie, pour chaque modèle, les prédictions hors pli concaténées (885 valeurs),
    la session (pli) de chaque fenêtre, puis COR et RMSE calculés sur ces 885 valeurs."""
    outer = KFold(n_splits=n_folds, shuffle=False)  # 5 blocs contigus
    out = {}
    for name, model in models.items():
        y_true, y_pred, sessions = [], [], []
        for k, (tr, te) in enumerate(outer.split(X)):
            model.fit(X[tr], y[tr])  # tout (scaler, réglage interne) appris sur tr seulement
            p = model.predict(X[te])
            y_true.append(y[te]); y_pred.append(p); sessions.append(np.full(len(te), k + 1))
        yt, yp = np.concatenate(y_true), np.concatenate(y_pred)
        out[name] = {"COR": cor(yt, yp), "RMSE": rmse(yt, yp), "y_true": yt, "y_pred": yp,
                     "session": np.concatenate(sessions)}
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
            rows.append({"sujet": s, "modele": model, "modalites": tag, "n_features": X.shape[1],
                         "COR": r["COR"], "RMSE": r["RMSE"]})
            # Traçabilité : sujet, session (pli 1 à 5) et indice de fenêtre pour chaque prédiction
            preds.append(pd.DataFrame({"sujet": s, "modele": model, "session": r["session"],
                                       "t": np.arange(len(r["y_true"])),
                                       "y_true": r["y_true"], "y_pred": r["y_pred"]}))
        print(f"  {s} ok ({time.time() - t0:.0f} s)")

    temps = time.time() - t0
    df = pd.DataFrame(rows)
    Path("results").mkdir(exist_ok=True)
    df.to_csv(f"results/baselines_{tag}.csv", index=False)
    pd.concat(preds).to_csv(f"results/predictions_{tag}.csv", index=False)

    # Métadonnées pour la reproductibilité (annexe du rapport, étape 5)
    meta = {"modalites": tag, "n_sujets": len(subjects), "graine": cfg["seed"],
            "temps_s": round(temps, 1), "python": sys.version.split()[0],
            "numpy": np.__version__, "scikit-learn": sklearn.__version__,
            "pandas": pd.__version__, "commande": " ".join(sys.argv)}
    Path(f"results/meta_{tag}.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

    summary = df.groupby("modele")[["COR", "RMSE"]].agg(["mean", "std"]).round(4)
    print("\nRésultats (moyenne et écart-type sur les sujets) :")
    print(summary)
    print(f"\nTemps total : {temps:.0f} s")


if __name__ == "__main__":
    main()
