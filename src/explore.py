"""Étape 1 – Explorer le dossier SEED-VIG.

Liste les sous-dossiers, le nombre de fichiers .mat, puis ouvre UN fichier
de chaque sous-dossier et affiche les variables qu'il contient avec leur forme.

Usage :
    python src/explore.py --data-dir "C:/chemin/vers/SEED-VIG"
"""
import argparse
from pathlib import Path

import numpy as np
from scipy.io import loadmat


def describe_mat(path: Path) -> None:
    try:
        mat = loadmat(path)
    except NotImplementedError:
        # Fichiers .mat v7.3 (format HDF5)
        import h5py
        with h5py.File(path, "r") as f:
            for k in f.keys():
                print(f"      {k:<30} shape={f[k].shape}  (HDF5)")
        return
    for k, v in mat.items():
        if k.startswith("__"):
            continue
        if isinstance(v, np.ndarray):
            print(f"      {k:<30} shape={v.shape}  dtype={v.dtype}")
        else:
            print(f"      {k:<30} type={type(v).__name__}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True, help="Dossier racine de SEED-VIG")
    args = ap.parse_args()
    root = Path(args.data_dir)
    if not root.exists():
        raise SystemExit(f"Dossier introuvable : {root}")

    print(f"Dossier : {root.resolve()}\n")
    dirs = [root] + sorted(p for p in root.rglob("*") if p.is_dir())
    for d in dirs:
        mats = sorted(d.glob("*.mat"))
        others = [p for p in d.iterdir() if p.is_file() and p.suffix != ".mat"]
        if not mats and not others:
            continue
        print(f"[{d.relative_to(root) if d != root else '.'}]  {len(mats)} fichiers .mat, "
              f"{len(others)} autres fichiers")
        for p in others[:5]:
            print(f"    (autre) {p.name}")
        if mats:
            print(f"    exemple : {mats[0].name}")
            describe_mat(mats[0])
        print()


if __name__ == "__main__":
    main()
