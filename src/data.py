"""Chargement des features et des labels SEED-VIG, sujet par sujet."""
import json
from pathlib import Path

import numpy as np
from scipy.io import loadmat


def load_config(path="configs/config.json") -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def list_subjects(cfg: dict) -> list[str]:
    """Noms des fichiers (sans dossier) présents dans le dossier des labels."""
    label_dir = Path(cfg["data_dir"]) / cfg["label_dir"]
    return sorted(p.name for p in label_dir.glob("*.mat"))


def _to_2d(x: np.ndarray) -> np.ndarray:
    """Met les features au format (n_fenetres, n_features).

    Formats réels de SEED-VIG (vérifiés à l'étape 1, voir reports/carte.md) :
      - EEG : (canaux, fenêtres, bandes), ex. (17, 885, 25) ou (17, 885, 5).
              L'axe des fenêtres est donc l'axe 1, documenté dans Readme_English.txt.
      - EOG : (fenêtres, features), ex. (885, 36) : déjà au bon format.
    On place les fenêtres en premier, puis on aplatit canaux et bandes en
    une seule dimension de features (17 x 25 = 425 pour le 2 Hz).
    """
    x = np.asarray(x, dtype=float)
    if x.ndim == 1:
        return x[:, None]
    if x.ndim == 2:
        return x  # EOG : (fenêtres, features)
    if x.ndim == 3:
        x = np.moveaxis(x, 1, 0)  # (canaux, fenêtres, bandes) -> (fenêtres, canaux, bandes)
        return x.reshape(x.shape[0], -1)
    raise ValueError(f"Forme inattendue : {x.shape}")


def load_subject(cfg: dict, fname: str, modalities: list[str]):
    """Retourne X (n_fenetres, n_features) et y (n_fenetres,) pour un sujet."""
    root = Path(cfg["data_dir"])
    y = loadmat(root / cfg["label_dir"] / fname)[cfg["label_key"]].ravel().astype(float)
    blocks = []
    for m in modalities:
        spec = cfg["modalities"][m]
        x = _to_2d(loadmat(root / spec["dir"] / fname)[spec["key"]])
        if x.shape[0] != len(y):
            raise ValueError(f"{fname} / {m} : {x.shape[0]} fenêtres mais {len(y)} labels")
        blocks.append(x)
    return np.hstack(blocks), y
