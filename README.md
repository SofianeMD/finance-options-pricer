# Options Pricer

Pricer d'options développé dans un objectif d'apprentissage : comprendre les modèles de pricing en les implémentant, plutôt qu'en les consommant.

## Objectif

Pricing d'options (vanille dans un premier temps), calcul de grecques et visualisation des résultats.

## Versions

| Langage | Statut | Notes |
|---|---|---|
| Python | En cours | Version initiale |
| C# | À venir | Refonte orientée objet |

## Références

- *Options, Futures and Other Derivatives* — John C. Hull
- *_S&P Academy courses_
---
<sub>Projet d'apprentissage — toute remarque constructive est bienvenue.</sub>

## Pricer complet (Flask)

La version complète (options, 11 stratégies, Phoenix, Athéna, accumulateur, décumulateur, DRA Daily, grecs, bascule Black-Scholes / Monte Carlo, interface) est décrite dans [README_PRICER.md](README_PRICER.md). Lancer avec `pip install -r requirements.txt` puis `python main.py` (http://127.0.0.1:5001). Guide du code ajouté : [README_NOUVEAUX_MOTEURS.md](README_NOUVEAUX_MOTEURS.md).
