"""Étape 4.2 – Le lissage movingAve / LDS utilise-t-il des fenêtres futures ?

Partie A : identification du lissage à partir des DONNÉES BRUTES.
  - Les EEG brutes (Raw_Data, 200 Hz, 17 canaux) sont découpées en 885 fenêtres de 8 s
    (1600 échantillons, exactement 885 fenêtres : 1 416 000 / 1 600).
  - Pour chaque fenêtre, canal et bande (δ, θ, α, β, γ), on calcule la puissance par FFT.
    Proxy de la DE : 0,5 × log(puissance), à une constante près (la DE d'un signal
    gaussien vaut 0,5 log(2πe σ²)).
  - On compare la feature lissée F[t] à la proxy non lissée P[t + k] pour des décalages k
    entre −15 et +15 fenêtres. Le décalage qui maximise la corrélation donne le
    décalage temporel effectif du lissage :
      * lissage CENTRÉ : maximum à k = 0 ;
      * lissage CAUSAL (passé seulement) : maximum à k < 0 (la feature à t reflète t − W) ;
      * lissage utilisant le futur : maximum à k > 0.
  - Limite : la proxy n'est pas la DE exacte (pas de STFT de l'article). On ne lit donc que
    la position du maximum, pas la valeur absolue de la corrélation.

Partie B : impact sur la prédiction.
  - SVR (grille v1), 23 sujets, mêmes plis contigus : EEG frontal 2 Hz avec movingAve
    contre LDS, et fusion (EOG + EEG frontal) avec movingAve contre LDS.
  - Test apparié de Wilcoxon sur les 23 sujets. Les p-valeurs affichées sont BRUTES (non
    corrigées), pour 2 comparaisons × 2 métriques : à lire avec prudence.
  - Les features NON lissées ne sont pas fournies par SEED-VIG pour les EEG (seuls
    psd/de movingAve et LDS existent) : cette comparaison est impossible, et c'est dit.

Produit :
  - results/lissage_alignement.csv (corrélations par décalage, moyennes sur sujets) ;
  - results/lissage_impact.csv (COR/RMSE par sujet, movingAve contre LDS).

Usage : python src/lissage_test.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.io import loadmat
from scipy.stats import wilcoxon
from sklearn.model_selection import KFold

from baselines import make_models
from data import list_subjects, load_config, load_subject

FS = 200
W = 1600           # 8 s à 200 Hz
N_FEN = 885
BANDES = {"delta": (1, 4), "theta": (4, 8), "alpha": (8, 14), "beta": (14, 31), "gamma": (31, 50)}
DECALAGES = np.arange(-15, 16)
SUJETS_ALIGN = 3   # sujets utilisés pour l'alignement (le calcul est lourd)


def proxy_de_brute(chemin: Path) -> np.ndarray:
    """Retourne le log-puissance par fenêtre : (885, 17, 5)."""
    brut = loadmat(chemin)["EEG"][0, 0]["data"]          # (1 416 000, 17)
    brut = np.asarray(brut, dtype=float)[: N_FEN * W]
    fen = brut.reshape(N_FEN, W, brut.shape[1])          # (fenêtres, temps, canaux)
    fen = fen * np.hanning(W)[None, :, None]
    spectre = np.abs(np.fft.rfft(fen, axis=1)) ** 2
    freqs = np.fft.rfftfreq(W, d=1 / FS)
    out = np.empty((N_FEN, brut.shape[1], len(BANDES)))
    for j, (lo, hi) in enumerate(BANDES.values()):
        m = (freqs >= lo) & (freqs < hi)
        out[:, :, j] = np.log(spectre[:, m, :].mean(axis=1) + 1e-12)
    return out


def correlation_par_decalage(feat: np.ndarray, proxy: np.ndarray) -> np.ndarray:
    """feat, proxy : (885, n_canaux, n_bandes). Renvoie la corrélation moyenne par décalage."""
    res = np.zeros(len(DECALAGES))
    compte = 0
    for c in range(feat.shape[1]):
        for b in range(feat.shape[2]):
            f = feat[:, c, b]
            p = proxy[:, c, b]
            for i, k in enumerate(DECALAGES):
                if k >= 0:
                    a, bb = f[: N_FEN - k], p[k:]
                else:
                    a, bb = f[-k:], p[: N_FEN + k]
                res[i] += np.corrcoef(a, bb)[0, 1]
            compte += 1
    return res / compte


def partie_a(cfg) -> pd.DataFrame:
    sujets = list_subjects(cfg)[:SUJETS_ALIGN]
    racine = Path(cfg["data_dir"])
    lignes = []
    for s in sujets:
        proxy = proxy_de_brute(racine / "Raw_Data" / s)
        mov = np.asarray(loadmat(racine / "EEG_Feature_5Bands" / s)["de_movingAve"], float)
        lds = np.asarray(loadmat(racine / "EEG_Feature_5Bands" / s)["de_LDS"], float)
        # (17, 885, 5) -> (885, 17, 5)
        mov = np.moveaxis(mov, 1, 0)
        lds = np.moveaxis(lds, 1, 0)
        for nom, feat in [("movingAve", mov), ("LDS", lds)]:
            courbe = correlation_par_decalage(feat, proxy)
            for k, r in zip(DECALAGES, courbe):
                lignes.append({"sujet": s, "lissage": nom, "decalage_fenetres": int(k), "correlation": r})
        print(f"alignement {s} ok", flush=True)
    return pd.DataFrame(lignes)


def partie_b(cfg) -> pd.DataFrame:
    lignes = []
    comparaisons = {
        "EEG frontal 2 Hz": (["eeg_2hz_front"], ["eeg_2hz_front_lds"]),
        "Fusion frontale 2 Hz": (["eeg_2hz_front", "eog"], ["eeg_2hz_front_lds", "eog"]),
    }
    for s in list_subjects(cfg):
        for nom, (mov, lds) in comparaisons.items():
            ligne = {"sujet": s, "modalites": nom}
            for etiquette, mods in [("movingAve", mov), ("LDS", lds)]:
                X, y = load_subject(cfg, s, mods)
                pred = np.full(len(y), np.nan)
                for tr, te in KFold(n_splits=5, shuffle=False).split(X):
                    m = make_models(cfg["seed"], "v1")["svr_rbf"]
                    m.fit(X[tr], y[tr])
                    pred[te] = m.predict(X[te])
                ligne[f"COR_{etiquette}"] = float(np.corrcoef(y, pred)[0, 1])
                ligne[f"RMSE_{etiquette}"] = float(np.sqrt(np.mean((y - pred) ** 2)))
            lignes.append(ligne)
        print(f"impact {s} ok", flush=True)
    return pd.DataFrame(lignes)


def main():
    cfg = load_config()
    Path("results").mkdir(exist_ok=True)

    align = partie_a(cfg)
    align.to_csv("results/lissage_alignement.csv", index=False)
    moy = align.groupby(["lissage", "decalage_fenetres"])["correlation"].mean().reset_index()
    print("\nDécalage optimal (moyenne sur les sujets, en fenêtres de 8 s) :")
    for nom, sous in moy.groupby("lissage"):
        i = sous["correlation"].idxmax()
        print(f"  {nom} : max r = {sous.loc[i, 'correlation']:.3f} à k = {int(sous.loc[i, 'decalage_fenetres'])}")
        print(f"  {nom} : r à k=0 = {sous.loc[sous['decalage_fenetres'] == 0, 'correlation'].iloc[0]:.3f}")

    impact = partie_b(cfg)
    impact.to_csv("results/lissage_impact.csv", index=False)
    print("\nImpact movingAve contre LDS (SVR v1, 23 sujets, appariés) :")
    for nom, sous in impact.groupby("modalites"):
        for m in ["COR", "RMSE"]:
            a, b = sous[f"{m}_movingAve"].to_numpy(), sous[f"{m}_LDS"].to_numpy()
            p = float(wilcoxon(a, b).pvalue) if np.any(a != b) else 1.0
            print(f"  {nom} {m}: movingAve {a.mean():.4f} | LDS {b.mean():.4f} | p = {p:.4f}")


if __name__ == "__main__":
    main()
