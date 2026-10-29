# Fiche Théo — architecture, Phoenix, indicateurs et intégration

Temps cible : **7 minutes**. Suivre le [script commun](01_SCRIPT_VIDEO.md). Les rôles organisent la présentation du projet commun.

Tu présentes l’architecture et les fonctions communes du pricer, puis le Phoenix. Tu montres aussi comment main.py et JavaScript relient le formulaire aux calculs. Tu expliques aussi les deux cases du Plain et les indicateurs affichés, puis tu termines sur les tests.

## Fonctions à préparer

- [`market_data_engine.py` — `get_historical_prices`, ligne 31](../market_data_engine.py#L31)
- [`market_data_engine.py` — `get_vol_historique`, ligne 77](../market_data_engine.py#L77)
- [`strutu_engine.py` — `simulate_observation_dates`, ligne 15](../strutu_engine.py#L15)
- [`strutu_engine.py` — `_simuler_phoenix`, ligne 51](../strutu_engine.py#L51)
- [`main.py` — `api_phoenix`, ligne 218](../main.py#L218)
- [`main.py` — `api_autocall`, ligne 328](../main.py#L328)

## Ce qu’il faut savoir expliquer sans lire

- **Marché :** Yahoo fournit le spot et les clôtures ajustées. La recherche vide peut aussi signaler une indisponibilité. Les appels ne forment pas un instantané synchronisé.
- **Phoenix :** `actifs = ~rappele` exclut les contrats déjà terminés ; `coupon_du` combine activité et seuil coupon. `coupons_en_attente` stocke les coupons manqués avec mémoire et revient à zéro après paiement.
- **Référence :** les barrières Phoenix sont relatives à `strike_pct * S0`. Avec le réglage usuel de 100 %, la référence est S0.
- **Serveur :** une saisie de 4 % devient 0,04 ; une valeur de 0,95 devient 95 % et 950 pour 1 000 investis.

## Exemple à raconter

Phoenix, coupon 4 %, seuil coupon 70 et référence 100 : un premier constat à 65 ne verse rien. Un second constat à 80 verse 4 % sans mémoire ou 8 % avec mémoire si le premier coupon attend encore. Ces montants s’ajoutent aux autres règles du produit et sont actualisés à leur date de paiement.

## Montrer le lien avec JavaScript

Dans `templates/index.html`, rechercher `fetch('/api/autocall'`, `renderStructuredMetrics` et `renderChart`. Expliquer : envoi des paramètres, réception du JSON, affichage des indicateurs et tracé du SVG. JavaScript ne simule pas les trajectoires financières. Les formulaires effectuent aussi des vérifications, mais le serveur contrôle à nouveau les données.

## À éviter à l’oral

Ne pas dire que le VIX est la volatilité d’une action particulière, que tous les coupons sont garantis, ni que 4 % par semestre signifie 4 % par an. Ne pas présenter les clôtures ajustées et le dernier spot comme strictement identiques en convention ou synchronisés.
