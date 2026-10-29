# strutu_engine.py — comprendre le pricing

[Retour au guide général](README.md)

Ce moteur simule des cours, applique les règles contractuelles à chaque trajectoire, puis fait la moyenne des flux actualisés. Il ne télécharge aucune donnée et ne connaît pas le montant investi : 1 signifie 100 % du nominal, 0,04 signifie 4 %.

## Simulation du sous-jacent

Entre deux constats séparés de `dt` années :

`S_suivant = S_actuel × exp((r − q − sigma²/2) × dt + sigma × sqrt(dt) × Z)`

`Z` est un tirage normal standard indépendant par scénario et par intervalle. `r` est le taux, `q` le rendement de dividende continu, `sigma` la volatilité annualisée. La dérive est risque-neutre : le moteur n’utilise pas un rendement espéré historique de l’action. Les paramètres sont constants ; la simulation aux seuls constats convient aux règles discrètes implémentées. Elle ne surveille aucune barrière en continu.

Une matrice de 50 000 scénarios et 6 constats contient 50 000 lignes et 7 colonnes : la colonne 0 stocke le cours initial, les suivantes les cours aux constats.

## Phoenix : coupons conditionnels périodiques

À chaque constat, un scénario encore actif reçoit le coupon si le cours atteint la barrière coupon. Avec mémoire, les coupons manqués sont stockés et payés lors d’un constat favorable ; sans mémoire, ils sont perdus. Un rappel autorisé avant maturité rend le nominal, paie le coupon dû et arrête le produit. À maturité, les scénarios non rappelés rendent 1 si la protection finale est respectée, sinon `S_T / strike_reference`. Un bonus optionnel peut s’ajouter.

Les seuils du Phoenix portent sur `strike_reference = strike_pct × S0`. Avec le réglage habituel `strike_pct=1`, cette référence est simplement S0. Un coupon scalaire est répété à chaque date ; une liste permet un calendrier variable, notamment le step-up construit par l’interface.

Exemple, nominal 1 000, référence 100, coupon 4 %, seuil coupon 70, protection 60 : au premier constat à 65, aucun coupon ; au second à 80, versement de 40 sans mémoire, ou de 80 avec mémoire si le premier coupon attend encore. Sans rappel, un cours final à 50 rend 500 de principal. À 60 exactement, le principal est 1 000. Les coupons suivent leur propre condition.

## Plain : coupons accumulés au remboursement

Le produit public `analyse_autocall_plain` rappelle si le cours atteint le seuil de rappel à une date autorisée avant maturité. À la k-ième observation, il paie `1 + k × coupon`. Avant cette sortie, aucun coupon périodique n’est versé. Décaler le premier rappel autorisé ne décale pas l’accumulation des coupons.

Sans rappel anticipé, tous les coupons sont versés à maturité si le cours final atteint le seuil final (le même paramètre que le rappel), sinon aucun. Avec une barrière de protection, le principal vaut 1 au-dessus ou à égalité, et `S_T/S0` en dessous. Avec `B_pdi=None`, le principal vaut toujours 1 dans ce modèle. Désactiver la case de protection supprime donc la perte conditionnelle de principal ; cela ne signifie pas supprimer toute protection.

Exemple : S0=100, nominal=1 000, six constats semestriels, coupon=4 %, rappel=100 %, protection=60 %. Un rappel au deuxième constat paie 1 080 à un an. Sans rappel, un cours final à 105 paie 1 240 à trois ans ; à 80, il paie 1 000 ; à 50, il paie 500. Protection désactivée, ce dernier scénario paie 1 000. Cette description porte sur la mécanique du code ; le libellé commercial d’un produit ne suffit pas à définir son contrat.

La branche héritée qui acquérait les coupons à chaque constat a été retirée. La fonction publique reçoit maintenant `has_autocall` (vrai par défaut). Faux supprime uniquement le rappel ; les coupons restent conditionnés au niveau final.

## Prix et indicateurs

Pour chaque scénario i, on additionne les paiements `CF_i(t) × exp(-r × t)`. Le prix est la moyenne de ces sommes. Pour un flux unique de 1 080 à un an et r=3 %, la valeur actualisée est environ 1 048,08. Les coupons du Phoenix peuvent être actualisés à plusieurs dates ; ceux du Plain à la date unique de sortie.

| Indicateur | Calcul |
|---|---|
| Prix théorique | Moyenne des flux actualisés, puis ×100 pour le pourcentage |
| Valeur monétaire | Prix normalisé × nominal |
| Marge émetteur affichée | `(1 − prix) × 100`, avant coûts, couverture et défaut |
| Perte du principal | Nombre de trajectoires non rappelées sous la protection finale / nombre total |
| Durée moyenne | Moyenne de la date de sortie, rappel ou maturité |
| Arrive à maturité | Part des trajectoires jamais rappelées |
| Principal moyen si perte | Moyenne des remboursements du principal uniquement parmi les trajectoires en perte |
| Coupons moyens actualisés | Moyenne des coupons actualisés, y compris les zéros |

Si aucun scénario ne perd de principal, le remboursement conditionnel est `None`, affiché comme absent. Il ne vaut pas zéro. Les probabilités de rappel par date et la probabilité de maturité se partagent toutes les trajectoires.

L’erreur type vaut `écart-type(flux, ddof=1) / sqrt(N)` ; l’intervalle approché à 95 % vaut `prix ± 1,96 × erreur_type`. Multiplier N par quatre divise approximativement l’erreur par deux. Cet intervalle décrit le bruit de simulation, pas l’incertitude du modèle. Une graine fixe reproduit les tirages à paramètres identiques ; sans graine, deux calculs peuvent varier.

Les probabilités sont celles du modèle risque-neutre. La perte de principal ne mesure pas le gain total après coupons. Le modèle ne comprend ni défaut de l’émetteur, ni frais, ni smile de volatilité, ni courbe complète de taux. La volatilité historique utilisée comme entrée n’est pas une calibration aux prix des options.

## Lire NumPy dans ce fichier

`prix[:, k]` signifie : toutes les lignes (scénarios), colonne k (date). Dans la boucle Phoenix, k commence à 1 : `obs_dates[k-1]` et `coupon_schedule[k-1]` correspondent donc à cette même date. Dans la boucle Plain, k commence à 0 et le cours est dans `prix[:, k+1]` car la colonne initiale est réservée à S0.

`rappele` est un tableau de booléens. `~rappele` sélectionne les scénarios encore actifs. `&` exige deux conditions à la fois ; `|` en accepte une des deux. `np.where(condition, a, b)` choisit a si la condition est vraie, sinon b, scénario par scénario. `date_rappel=-1` signifie jamais rappelé. `tableau[perte]` ne garde que les lignes en perte. `np.mean` d’un tableau de booléens donne leur proportion, car vrai compte pour 1 et faux pour 0.


## Rappel anticipé optionnel

Le Plain reçoit `has_autocall=True` par défaut. La case décochée envoie `False` : aucune sortie anticipée, tous les coupons payables uniquement si le seuil final est atteint à maturité, protection du capital inchangée. Le premier rappel autorisé est alors ignoré. Les constats intermédiaires ne créent aucun coupon acquis. Exemple : quatre constats à 4 % donnent 16 % à maturité si le seuil final est atteint, sinon 0 %.

## Code actuel expliqué fonction par fonction

Les extraits suivants reproduisent les fonctions du fichier source au moment de la rédaction. Les fonctions commençant par `_` sont des aides internes.

### `simulate_observation_dates`

```python
def simulate_observation_dates(S0, r, q, sigma, obs_dates, n_simulations, rng=None):
    """Simule le sous-jacent uniquement aux dates d'observation.

    Je n'ai pas besoin du chemin jour par jour pour un Phoenix : seuls les
    constats comptent. J'utilise le mouvement brownien géométrique entre deux
    dates (même formule que mon Monte Carlo pour les options).

    Paramètres : S0, r, q, sigma (en décimal), obs_dates (liste croissante en
    années), n_simulations, rng (générateur numpy, optionnel).
    Renvoie : une matrice (n_simulations, n_dates + 1), colonne 0 = S0.
    """
    if rng is None:
        rng = np.random.default_rng()

    n_dates = len(obs_dates)
    prix = np.zeros((n_simulations, n_dates + 1))
    prix[:, 0] = S0  # je fais partir tous les scénarios du même spot

    t_precedent = 0.0
    for i in range(n_dates):
        t = obs_dates[i]
        dt = t - t_precedent  # temps écoulé depuis la dernière obs
        Z = rng.standard_normal(n_simulations)  # je tire un choc par scénario
        # mouvement brownien géométrique (j'ai repris la formule de mon Monte Carlo options)
        croissance = (r - q - sigma**2 / 2) * dt
        choc = sigma * np.sqrt(dt) * Z
        prix[:, i + 1] = prix[:, i] * np.exp(croissance + choc)
        t_precedent = t

    return prix
```

**Traduction en phrase :** Je crée une ligne par scénario, je pars de S0 et je tire un nouveau choc à chaque intervalle pour remplir les cours aux dates de constat.

### `_simuler_phoenix`

```python
def _simuler_phoenix(S0, r, q, sigma, obs_dates, K_auto, B_phoenix, B_pdi, coupon_schedule,
                     n_simulations, memory, has_autocall, bonus_threshold, bonus_amount,
                     strike_pct, rng):
    """Suit les flux du Phoenix pour chaque scénario.

    À chaque date : rappel si S >= barrière de rappel, coupon si S >= barrière
    coupon (avec ou sans effet mémoire). À maturité : 100 % si S_T >= barrière
    de protection, sinon S_T / strike. Je garde le détail par scénario pour
    pouvoir calculer les stats ensuite. Les paramètres sont déjà vérifiés
    dans main.py.

    Renvoie : un dict avec les flux actualisés, les coupons actualisés, la date
    de rappel (-1 si jamais), S_T et un masque des scénarios en perte.
    """
    n_dates = len(obs_dates)
    prix = simulate_observation_dates(S0, r, q, sigma, obs_dates, n_simulations, rng)

    # je passe les barrières en niveau de prix (ex : 70 % d'un strike à 100 -> 70)
    strike_reference = strike_pct * S0
    K_auto_level = K_auto * strike_reference
    B_phoenix_level = B_phoenix * strike_reference
    B_pdi_level = B_pdi * strike_reference

    flux_actualises = np.zeros(n_simulations)      # tout ce que le client reçoit, actualisé
    coupons_actualises = np.zeros(n_simulations)   # seulement la partie coupons
    rappele = np.zeros(n_simulations, dtype=bool)  # False tant que pas rappelé
    date_rappel = np.full(n_simulations, -1)       # -1 = jamais rappelé
    coupons_en_attente = np.zeros(n_simulations)   # j'en ai besoin pour l'effet mémoire

    for k in range(1, n_dates + 1):
        t_k = obs_dates[k - 1]
        S_k = prix[:, k]
        actualisation = np.exp(-r * t_k)

        # je ne regarde que les scénarios encore en vie
        actifs = ~rappele

        # je bloque le rappel à la dernière date, à maturité je passe par le remboursement final
        # (sinon mon bonus ne serait jamais versé)
        if has_autocall and k < n_dates:
            autocall_now = actifs & (S_k >= K_auto_level)
        else:
            autocall_now = np.zeros(n_simulations, dtype=bool)

        coupon_du = actifs & (S_k >= B_phoenix_level)

        coupon_periode = coupon_schedule[k - 1]
        if memory:
            # j'accumule le coupon de la période, et je paie tout le stock dès que c'est au-dessus
            coupons_en_attente += np.where(actifs, coupon_periode, 0.0)
            montant_coupon = np.where(coupon_du, coupons_en_attente, 0.0)
            coupons_en_attente = np.where(coupon_du, 0.0, coupons_en_attente)  # je remets à 0 si c'est payé
        else:
            # sans mémoire un coupon raté est perdu
            montant_coupon = np.where(coupon_du, coupon_periode, 0.0)

        coupons_actualises += montant_coupon * actualisation
        flux_actualises += montant_coupon * actualisation
        # si rappel : je rends le nominal (1 = 100 %)
        flux_actualises += np.where(autocall_now, 1.0 * actualisation, 0.0)

        date_rappel[autocall_now] = k - 1
        rappele = rappele | autocall_now

    # maturité : je traite ceux qui n'ont jamais été rappelés
    S_T = prix[:, n_dates]
    actualisation_T = np.exp(-r * obs_dates[-1])
    non_rappelees = ~rappele

    # au-dessus de la barrière de protection : 100 % du capital
    # en dessous : je rembourse S_T/strike, donc la perte du sous-jacent (ex : 50/100 -> 50 %)
    remboursement_T = np.where(S_T >= B_pdi_level, 1.0, S_T / strike_reference)
    if bonus_threshold is not None:
        bonus_du = non_rappelees & (S_T >= bonus_threshold * strike_reference)
        remboursement_T = remboursement_T + np.where(bonus_du, bonus_amount, 0.0)

    flux_actualises += np.where(non_rappelees, remboursement_T * actualisation_T, 0.0)

    return {
        "flux": flux_actualises,
        "coupons": coupons_actualises,
        "date_rappel": date_rappel,
        "S_T": S_T,
        "perte_capital": non_rappelees & (S_T < B_pdi_level),
        "strike_reference": strike_reference,
    }
```

**Traduction en phrase :** Je parcours les dates et je ne paie que les scénarios encore actifs. Je règle les coupons dus, puis le capital au rappel ou à maturité, en actualisant chaque paiement à sa propre date.

### `analyse_phoenix`

```python
def analyse_phoenix(S0, r, q, sigma, obs_dates, K_auto, B_phoenix, B_pdi, coupon,
                    n_simulations, memory=False, has_autocall=True,
                    bonus_threshold=None, bonus_amount=0.0, strike_pct=1.0, seed=None):
    """Price le Phoenix et calcule les stats des scénarios.

    Paramètres : S0, r, q, sigma en décimal, obs_dates en années, barrières
    K_auto / B_phoenix / B_pdi en fraction du strike (0.7 = 70 %), coupon
    (un nombre ou une liste pour un step-up), n_simulations, memory,
    has_autocall, bonus_threshold / bonus_amount (optionnels), strike_pct,
    seed (pour retomber sur les mêmes tirages).

    Renvoie : un dict avec le prix, l'erreur type et l'intervalle de confiance
    à 95 %, la marge émetteur, la proba de rappel à chaque date, la proba
    d'aller à maturité, la proba de perte en capital, le remboursement moyen
    si perte et la durée de vie moyenne.
    """
    dates = np.asarray(obs_dates, dtype=float)
    # coupon fixe -> je mets le même à chaque date, sinon j'ai une liste (step-up)
    if np.isscalar(coupon):
        coupon_schedule = np.full(dates.size, float(coupon))
    else:
        coupon_schedule = np.asarray(coupon, dtype=float)

    rng = np.random.default_rng(seed)  # avec une seed je retombe sur les mêmes tirages
    res = _simuler_phoenix(S0, r, q, sigma, dates, K_auto, B_phoenix, B_pdi, coupon_schedule,
                           n_simulations, memory, has_autocall, bonus_threshold, bonus_amount,
                           strike_pct, rng)

    flux = res["flux"]
    date_rappel = res["date_rappel"]
    n_dates = dates.size

    # mon prix = moyenne des flux actualisés
    prix = float(np.mean(flux))
    # erreur type MC (écart-type / racine de n), je m'en sers pour l'intervalle de confiance
    erreur_type = float(np.std(flux, ddof=1) / np.sqrt(n_simulations))

    # pour chaque date je compte la part des scénarios rappelés
    proba_rappel = [float(np.mean(date_rappel == k)) for k in range(n_dates)]
    proba_maturite = float(np.mean(date_rappel == -1))

    # durée de vie : je prends la date du rappel, ou la maturité si jamais rappelé
    duree = np.where(date_rappel >= 0, dates[np.maximum(date_rappel, 0)], dates[-1])

    # je compte une perte en capital si pas rappelé + sous la protection à maturité
    perte = res["perte_capital"]
    proba_perte = float(np.mean(perte))
    if perte.any():
        # je regarde combien le client récupère en moyenne quand il perd
        remboursement_moyen_si_perte = float(np.mean(res["S_T"][perte] / res["strike_reference"]))
    else:
        remboursement_moyen_si_perte = None

    return {
        "prix": prix,
        "erreur_type": erreur_type,
        "ic95": (prix - 1.96 * erreur_type, prix + 1.96 * erreur_type),
        "marge_emetteur": 1.0 - prix,   # le client paie 100 %, le produit vaut "prix"
        "proba_rappel_par_date": proba_rappel,
        "proba_maturite": proba_maturite,
        "proba_perte_capital": proba_perte,
        "remboursement_moyen_si_perte": remboursement_moyen_si_perte,
        "duree_de_vie_moyenne": float(np.mean(duree)),
        "coupons_moyens_actualises": float(np.mean(res["coupons"])),
        "obs_dates": dates.tolist(),
        "coupon_schedule": coupon_schedule.tolist(),
    }
```

**Traduction en phrase :** Je répète le coupon si nécessaire, je simule les flux, puis je calcule leur moyenne et les statistiques sur l’ensemble des scénarios.

### `price_phoenix`

```python
def price_phoenix(S0, r, q, sigma, obs_dates, K_auto, B_phoenix, B_pdi, coupon,
                  n_simulations, memory=False, has_autocall=True,
                  bonus_threshold=None, bonus_amount=0.0, strike_pct=1.0, seed=None):
    """Version courte d'analyse_phoenix : je renvoie juste le prix
    (en % du nominal).
    """
    return analyse_phoenix(S0, r, q, sigma, obs_dates, K_auto, B_phoenix, B_pdi, coupon,
                           n_simulations, memory, has_autocall, bonus_threshold,
                           bonus_amount, strike_pct, seed)["prix"]
```

**Traduction en phrase :** Je réutilise l’analyse complète et je ne garde que sa valeur normalisée ; pour 1 000 investis, il faut encore la multiplier par 1 000.

### `payoff_phoenix_maturite`

```python
def payoff_phoenix_maturite(ST, S0, B_phoenix, B_pdi, coupon_final, strike_pct=1.0,
                            bonus_threshold=None, bonus_amount=0.0):
    """Payoff à maturité d'un Phoenix qui n'a PAS été rappelé.

    Je m'en sers pour le graphe, en fonction du prix final S_T.
    Limite : je ne compte que le dernier coupon. Avec l'effet mémoire, le
    coupon final dépend du chemin, donc je ne peux pas le lire sur un graphe
    en fonction de S_T.

    Renvoie : un dict avec le remboursement, le coupon, le bonus et le total
    (en % du nominal) pour chaque point de la grille.
    """
    ST = np.asarray(ST, dtype=float)
    strike_reference = strike_pct * S0

    remboursement = np.where(ST >= B_pdi * strike_reference, 1.0, ST / strike_reference)
    coupon = np.where(ST >= B_phoenix * strike_reference, coupon_final, 0.0)
    if bonus_threshold is not None:
        bonus = np.where(ST >= bonus_threshold * strike_reference, bonus_amount, 0.0)
    else:
        bonus = np.zeros_like(ST)

    return {
        "remboursement": remboursement,
        "coupon": coupon,
        "bonus": bonus,
        "total": remboursement + coupon + bonus,
    }
```

**Traduction en phrase :** Pour chaque cours final donné, je calcule le capital, le dernier coupon et le bonus éventuel, sans reconstituer les paiements antérieurs.

### `_valider_autocall`

```python
def _valider_autocall(S0, r, q, sigma, obs_dates, K_auto, B_pdi, coupon,
                      n_simulations, first_call_date):
    """Vérifie les paramètres du Plain."""
    for valeur in (S0, r, q, sigma, K_auto, coupon):
        if not np.isscalar(valeur) or not np.isfinite(valeur):
            raise ValueError("Les paramètres doivent être des nombres finis.")
    if S0 <= 0 or sigma < 0 or K_auto <= 0 or coupon < 0:
        raise ValueError("Spot et barrière strictement positifs ; volatilité et coupon positifs ou nuls.")
    dates = np.asarray(obs_dates, dtype=float)
    if dates.ndim != 1 or dates.size == 0 or not np.all(np.isfinite(dates)):
        raise ValueError("Il faut une liste non vide de dates finies, en années.")
    if dates[0] <= 0 or np.any(np.diff(dates) <= 0):
        raise ValueError("Les dates doivent être positives et strictement croissantes.")
    if B_pdi is not None:
        if not np.isscalar(B_pdi) or not np.isfinite(B_pdi) or not 0 < B_pdi <= min(1.0, K_auto):
            raise ValueError("La protection doit être dans ]0 ; min(1, barrière de rappel/coupon)].")
    if isinstance(n_simulations, (bool, np.bool_)) or not isinstance(n_simulations, (int, np.integer)) or n_simulations < 2:
        raise ValueError("Il faut un nombre entier de simulations supérieur ou égal à 2.")
    if first_call_date is not None:
        if not np.isscalar(first_call_date) or not np.isfinite(first_call_date) or not 0 <= first_call_date <= dates[-1]:
            raise ValueError("La première date de rappel doit être entre 0 et la maturité.")
    return dates
```

**Traduction en phrase :** Je refuse les données incompatibles avec les règles du moteur avant de créer les trajectoires. Les limites supplémentaires de l’application se trouvent dans main.py.

### `_flux_autocall`

```python
def _flux_autocall(prix, S0, dates, K_auto, B_pdi, coupon, has_autocall,
                   first_call_date):
    """Suit les remboursements de trajectoires déjà simulées.

    Montants en fraction du nominal. La colonne 0 de prix contient S0.
    La protection est observée uniquement à maturité (barrière européenne).
    """
    n_simulations = prix.shape[0]
    n_dates = len(dates)
    rappele = np.zeros(n_simulations, dtype=bool)
    date_rappel = np.full(n_simulations, -1)
    remboursement = np.ones(n_simulations)
    coupons_payes = np.zeros(n_simulations)
    date_paiement = np.full(n_simulations, dates[-1])
    nombre_coupons = np.zeros(n_simulations)

    for k in range(n_dates):
        au_dessus = prix[:, k + 1] >= K_auto * S0
        if has_autocall:
            rappel_autorise = first_call_date is None or dates[k] >= first_call_date
            # La dernière observation relève du remboursement final, pas d'un rappel.
            if k < n_dates - 1 and rappel_autorise:
                rappel_du = (~rappele) & au_dessus
                coupons_payes[rappel_du] = coupon * (k + 1)
                nombre_coupons[rappel_du] = k + 1
                date_paiement[rappel_du] = dates[k]
                date_rappel[rappel_du] = k
                rappele[rappel_du] = True

    non_rappeles = ~rappele
    S_T = prix[:, -1]
    # Le rappel est optionnel ; la condition finale des coupons reste identique.
    coupon_final_du = non_rappeles & (S_T >= K_auto * S0)
    coupons_payes[coupon_final_du] = coupon * n_dates
    nombre_coupons[coupon_final_du] = n_dates

    perte_capital = np.zeros(n_simulations, dtype=bool)
    if B_pdi is not None:
        perte_capital = non_rappeles & (S_T < B_pdi * S0)
        remboursement[perte_capital] = S_T[perte_capital] / S0

    # Traduction en phrase : à la date de sortie, on rend le capital et les coupons dus.
    return {
        "remboursement": remboursement,
        "coupons": coupons_payes,
        "date_paiement": date_paiement,
        "date_rappel": date_rappel,
        "perte_capital": perte_capital,
        "nombre_coupons": nombre_coupons,
    }
```

**Traduction en phrase :** À chaque constat autorisé, je paie en une fois le nominal et les coupons accumulés des scénarios rappelés. À la fin, je traite ceux qui restent et leur éventuelle perte de capital.

### `_analyse_autocall`

```python
def _analyse_autocall(S0, r, q, sigma, obs_dates, K_auto, B_pdi, coupon,
                       n_simulations, has_autocall, first_call_date, seed):
    """Calcul commun : simulation indépendante, suivi des flux, puis statistiques."""
    dates = _valider_autocall(S0, r, q, sigma, obs_dates, K_auto, B_pdi, coupon,
                              n_simulations, first_call_date)
    rng = np.random.default_rng(seed)
    # On réutilise exactement le simulateur existant du Phoenix.
    # Les trajectoires sont indépendantes : pas de paires antithétiques à traiter.
    prix = simulate_observation_dates(S0, r, q, sigma, dates, n_simulations, rng)
    if not np.all(np.isfinite(prix)):
        raise ValueError("Simulation non finie : vérifiez les paramètres de marché.")
    res = _flux_autocall(prix, S0, dates, K_auto, B_pdi, coupon,
                         has_autocall, first_call_date)

    actualisation = np.exp(-r * res["date_paiement"])
    flux = (res["remboursement"] + res["coupons"]) * actualisation
    if not np.all(np.isfinite(flux)):
        raise ValueError("Flux actualisés non finis : vérifiez les paramètres.")
    valeur = float(np.mean(flux))
    erreur_type = float(np.std(flux, ddof=1) / np.sqrt(n_simulations))
    perte = res["perte_capital"]
    remboursement_si_perte = None
    if perte.any():
        remboursement_si_perte = float(np.mean(res["remboursement"][perte]))

    # Traduction en phrase : chaque probabilité porte sur TOUTES les simulations.
    return {
        "prix": valeur,
        "erreur_type": erreur_type,
        "ic95": (valeur - 1.96 * erreur_type, valeur + 1.96 * erreur_type),
        "marge_emetteur": 1.0 - valeur,
        "proba_rappel_par_date": [float(np.mean(res["date_rappel"] == k)) for k in range(len(dates))],
        "proba_maturite": float(np.mean(res["date_rappel"] == -1)),
        "proba_perte_capital": float(np.mean(perte)),
        "remboursement_moyen_si_perte": remboursement_si_perte,
        "duree_de_vie_moyenne": float(np.mean(res["date_paiement"])),
        "coupons_moyens_actualises": float(np.mean(res["coupons"] * actualisation)),
        "nombre_moyen_coupons": float(np.mean(res["nombre_coupons"])),
        "obs_dates": dates.tolist(),
        "coupon_schedule": [float(coupon)] * len(dates),
        "n_simulations": int(n_simulations),
    }
```

**Traduction en phrase :** Je contrôle les entrées, simule les cours, détermine les paiements, les actualise et calcule la valeur moyenne ainsi que les probabilités.

### `analyse_autocall_plain`

```python
def analyse_autocall_plain(S0, r, q, sigma, obs_dates, K_auto, B_pdi, coupon,
                            n_simulations=50000, first_call_date=None, seed=None, has_autocall=True):
    """Autocall Plain : coupon accumulé jusqu'au rappel ou à maturité.

    Conventions identiques au Phoenix : r, q, sigma et coupon en décimal,
    barrières en fraction de S0, dates en années, montants en fraction du nominal.
    Exemple : coupon=0.02 signifie 2 % PAR OBSERVATION (pas par an).

    Rappel avant maturité si S >= K_auto*S0 : paiement de 1 + coupon*(k+1).
    Sans rappel, à maturité : tous les coupons si S_T >= K_auto*S0 ; sinon
    aucun coupon. Capital : 1, sauf sous B_pdi*S0 où il vaut S_T/S0.
    has_autocall=False supprime seulement les rappels : les coupons restent
    conditionnés au niveau final, sans acquisition à chaque constat.
    B_pdi=None désactive la perte conditionnelle de capital.
    first_call_date décale le début des rappels, sans décaler l'accumulation.
    La protection n'est jamais surveillée entre les dates ni avant maturité.

    Traduction en phrase : on attend le rappel, puis on paie d'un coup le
    nominal et les coupons accumulés. Ce n'est pas un Phoenix à coupons périodiques.
    """
    return _analyse_autocall(S0, r, q, sigma, obs_dates, K_auto, B_pdi, coupon,
                              n_simulations, has_autocall, first_call_date, seed)
```

**Traduction en phrase :** Je lance le calcul commun en activant la mécanique de rappel du Plain ; le début autorisé des rappels et la graine sont transmis au calcul.
