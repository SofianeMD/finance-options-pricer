# Répartition de l’oral

| Créneau | Qui ? | Sujet | Fichier principal |
|---|---|---|---|
| 00:00–00:30 | Théo | Objectif du projet de groupe | Application |
| 00:30–01:15 | Théo | Architecture du pricer | main.py et index.html |
| 01:15–02:00 | Théo | Données de marché | market_data_engine.py |
| 02:00–03:00 | Joseph | Rendements et volatilité | volatility_engine.py |
| 03:00–04:00 | Théo | Simulation commune | strutu_engine.py : simulate_observation_dates |
| 04:00–05:00 | Théo | Phoenix, coupons et mémoire | strutu_engine.py : _simuler_phoenix |
| 05:00–06:30 | Joseph | Plain et flux contractuels | strutu_engine.py : _flux_autocall |
| 06:30–07:30 | Joseph | Option sans rappel | strutu_engine.py : analyse_autocall_plain |
| 07:30–08:15 | Théo | Protection du capital | strutu_engine.py : _flux_autocall |
| 08:15–09:15 | Joseph | Actualisation et prix | strutu_engine.py : _analyse_autocall |
| 09:15–10:00 | Théo | Indicateurs et graphique | Résultats Plain |
| 10:00–11:00 | Théo | Intégration et démonstration Phoenix | main.py et application |
| 11:00–12:00 | Joseph | Démonstration Plain avec/sans rappel | Application |
| 12:00–12:30 | Théo | Tests | tests/ |
| 12:30–13:00 | Joseph | Limites et extensions | Résultats |

**Total : Théo 7 minutes ; Joseph 6 minutes.**

## Pourquoi cette répartition ?

Théo présente l’architecture commune et le Phoenix. Joseph présente la volatilité et le Plain dans ses deux modes. Il explique aussi l’actualisation et les statistiques en prenant les flux du Plain comme exemple : cela prolonge naturellement son sujet et équilibre le temps. La simulation commune reste dans ta partie.

La version intégrée a été adaptée pour que le rappel soit une case. Présenter la mécanique actuelle sans lui attribuer mot pour mot l’ancienne branche « Sans rappel » : les coupons de la version actuelle dépendent du niveau final, pas du nombre de constats intermédiaires favorables.

## Qui répond en premier aux questions ?

| Question | Réponse principale | Complément |
|---|---|---|
| D’où viennent les données ? | Théo | Joseph explique leur usage pour la volatilité |
| Pourquoi cette simulation du cours ? | Théo | Joseph fait le lien avec les flux Plain |
| Comment fonctionne la mémoire Phoenix ? | Théo | Joseph distingue les coupons accumulés Plain |
| Que change le mode sans rappel ? | Joseph | Théo montres le passage interface/API |
| Que fait la protection finale ? | Joseph sur Plain | Théo précises la référence Phoenix |
| Comment est calculé le prix ? | Joseph | Théo expliques les conversions et l’affichage |
| Que mesure l’intervalle de confiance ? | Joseph | Théo peux montrer les tests |
| Comment le formulaire déclenche le calcul ? | Théo | Joseph montre les paramètres de le Plain |

## Répétition commune

Chacun doit savoir expliquer en une phrase le produit de l’autre. Joseph prépare particulièrement les exemples de remboursement et les deux cases indépendantes du Plain. Joseph prépare aussi les log-rendements, ddof=1 et l’annualisation. Théo, prépare particulièrement les unités, le simulateur, la mémoire et les indicateurs. Mesurez une répétition : ajustez la longueur des explications et les manipulations pour respecter l’équilibre, plutôt que partager un même calcul entre deux voix toutes les vingt secondes.
