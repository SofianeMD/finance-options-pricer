# Fiche Joseph — volatilité et Plain avec et sans rappel

Temps cible : **6 minutes**. Suivre le [script commun](01_SCRIPT_VIDEO.md). Les rôles organisent la présentation du projet commun.

Tu présentes le Plain, ses deux configurations et leurs flux. Tu prends aussi la volatilité, la valorisation, la démonstration du Plain et les limites : ces sujets forment une partie cohérente de la présentation collective.

## Fonctions à préparer

- [`volatility_engine.py` — `log_returns`, ligne 4](../volatility_engine.py#L4)
- [`volatility_engine.py` — `historical_volatility`, ligne 37](../volatility_engine.py#L37)
- [`strutu_engine.py` — `_valider_autocall`, ligne 256](../strutu_engine.py#L256)
- [`strutu_engine.py` — `_flux_autocall`, ligne 280](../strutu_engine.py#L280)
- [`strutu_engine.py` — `analyse_autocall_plain`, ligne 376](../strutu_engine.py#L376)
- [`strutu_engine.py` — `_analyse_autocall`, ligne 332](../strutu_engine.py#L332)

## Ce qu’il faut savoir expliquer sans lire

- **Volatilité :** avec les prix 100, 101, 100, les rendements logarithmiques sont environ +0,00995033 et −0,00995033 ; leur volatilité annualisée vaut environ 22,34 %. C’est un exemple pédagogique très court, pas un historique exploitable.
- **Indices :** `prices[1:]` commence au deuxième prix ; `prices[:-1]` finit à l’avant-dernier. Chaque division compare deux jours successifs.
- **Modèle :** `croissance = (r-q-sigma**2/2)*dt` et `choc = sigma*sqrt(dt)*Z` déterminent le multiplicateur du prochain cours. `Z` varie par scénario et intervalle.
- **Matrice :** `prix[:, k+1]` lit tous les scénarios à une date ; la colonne zéro est le départ. La boucle Plain commence à k=0, donc `k+1` est le nombre d’observations écoulées.
- **Plain :** à la sortie anticipée, `coupon*(k+1)` est payé en une fois. À maturité, tous les coupons sont conditionnés au seuil final. Décocher le rappel ne change pas cette condition.
- **Principal :** sous la protection finale, remboursement `S_T/S0`. La barrière est observée seulement à maturité, pas en continu. `B_pdi=None` supprime cette perte conditionnelle.
- **Prix :** moyenne des paiements actualisés. Le Phoenix paie éventuellement à plusieurs dates, le Plain à sa date de sortie.
- **Précision :** erreur type = écart-type des flux / racine du nombre de simulations ; IC approximatif = prix ± 1,96 erreur type. Quatre fois plus de simulations réduit environ de moitié l’erreur type.

## Exemple à raconter

Nominal 1 000, six constats, coupon 4 % : rappel au deuxième constat, 1 080 versés. Sans rappel, à maturité et au-dessus du seuil final, 1 240 versés ; en dessous du seuil coupon mais au-dessus de la protection, 1 000 ; sous une protection de 60 % avec un cours final égal à 50 % du cours initial, 500. Ces montants futurs ne sont pas les valeurs actuelles.

Un paiement de 1 080 à un an avec un taux continu de 3 % vaut environ 1 048,08 aujourd’hui. Le moteur moyenne des paiements de ce type sur toutes les trajectoires.

## Lire les indicateurs correctement

La probabilité de perte compte les scénarios avec principal réduit, divisés par toutes les simulations. Le remboursement moyen si perte ne moyenne que les scénarios en perte et exclut les coupons. S’il n’y en a aucun, la valeur est absente, pas zéro. Les rappels par date sont des proportions inconditionnelles ; leur somme plus la probabilité de maturité vaut 100 %, aux arrondis près.

## À éviter à l’oral

Ne pas qualifier la marge affichée de profit certain. Ne pas appeler l’intervalle de confiance une garantie sur la juste valeur. Ne pas dire que Monte Carlo prédit le marché ou que le graphique est le prix théorique.
