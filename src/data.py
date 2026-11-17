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

    Les features EEG sont souvent stockées en (canaux, fenetres, bandes) :
    on met l'axe des fenêtres en premier puis on aplatit le reste.
    """
    x = np.asarray(x, dtype=float)
    if x.ndim == 1:
        return x[:, None]
    if x.ndim == 2:
        return x
    if x.ndim == 3:
        # l'axe des fenêtres est le plus long en général (885)
        win_axis = int(np.argmax(x.shape))
        x = np.moveaxis(x, win_axis, 0)
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
