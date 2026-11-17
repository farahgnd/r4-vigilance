# R4 – Vigilance : EEG et EOG (Zheng et Lu 2017, SEED-VIG)

Projet ECUE DMI-BCI – EPISEN. Groupe : Farah Guendouci, Fatima Zohra Chadli, Erica Pereira Dias Barreto.

Reproduction de : W.-L. Zheng et B.-L. Lu, *A multimodal approach to estimating vigilance using EEG and forehead EOG*, J. Neural Eng. 14 (2017) 026017.

## Installation

```bash
python -m venv .venv
# Windows : .venv\Scripts\activate    |  Mac/Linux : source .venv/bin/activate
pip install -r requirements.txt
```

## Données

Les données ne sont pas dans le dépôt (accès fourni par l'enseignant, pas de redistribution).
Voir `data/README.md`, puis renseigner `data_dir` dans `configs/config.json`.

## Commandes

```bash
python src/explore.py --data-dir "CHEMIN/VERS/SEED-VIG"   # étape 1 : inventaire des fichiers
python src/baselines.py --modalities eog --max-subjects 2   # essai rapide
python src/baselines.py --modalities eog                    # baselines EOG
python src/baselines.py --modalities eeg_2hz                # baselines EEG
python src/baselines.py --modalities eeg_2hz eog            # fusion
```

Les résultats sont écrits dans `results/`.

## Structure

| Dossier | Contenu |
| --- | --- |
| `data/` | Instructions de récupération (pas les données) |
| `src/` | Code |
| `configs/` | Chemins, noms de variables, graine |
| `notebooks/` | Exploration |
| `results/` | Résultats bruts (CSV) |
| `figures/` | Figures |
| `reports/` | Carte, protocole, écarts, extension, rapport |
