# main.py — du formulaire au résultat

[Retour au guide général](README.md)

Ce fichier fait le lien entre le navigateur et les moteurs. Flask reçoit les demandes, vérifie les paramètres, convertit les unités, appelle le moteur et renvoie du JSON. Il ne calcule pas la volatilité lui-même.

## Parcours d’un calcul

1. Le navigateur envoie les paramètres à `/api/phoenix` ou `/api/autocall`.
2. Le serveur transforme par exemple `sigma=25` en `sigma=0.25` et les mois de premier rappel en années.
3. Le moteur calcule une valeur pour un nominal de 1.
4. Le serveur multiplie par le nominal pour la valeur monétaire et par 100 pour les champs `_pct`.
5. Le HTML affiche les indicateurs, le graphique SVG et le calendrier.

Exemple : une valeur moteur de 0,95 donne un prix de 95 % et une valeur de 950 pour 1 000 investis. La marge affichée est 100 − 95 = 5 points du nominal ; ce n’est pas un bénéfice net de couverture et de frais.

## Routes

| Méthode | Adresse | Rôle |
|---|---|---|
| GET | `/` | Affiche `templates/index.html` |
| GET | `/api/search_ticker?q=apple` | Recherche des symboles |
| GET | `/api/market/AAPL` | Spot, devise, volatilité historique et VIX |
| POST | `/api/phoenix` | Phoenix : prix, statistiques et graphique |
| POST | `/api/autocall` | Plain : prix, statistiques et graphique |

Le Plain exige `produit="autocall_plain"`. Le mode sans rappel est une option du Plain : `has_autocall=false`, sans produit séparé. Aucun endpoint de volatilité dédié n’est présent dans cette copie autonome.

## Paramètres et contrôles

`S0` est un cours, `nominal` un montant investi, `r`, `q`, `sigma`, les coupons et les barrières sont en pourcentage dans le JSON. `T` et `obs_dates` sont en années, `frequence` en observations par an. Le formulaire convertit la maturité saisie en mois avant l’appel. Les fréquences autorisées sont 1, 2, 4 et 12 ; une maturité doit tomber exactement sur un constat.

Les routes limitent les simulations à 1 000–500 000 et la maturité à 30 ans. Le Plain limite aussi le nombre total de constats simulés à 6 millions. Le Plain accepte une volatilité nulle, utile pour un scénario déterministe ; le validateur Phoenix demande une volatilité strictement positive. Les vérifications des deux routes ne sont donc pas identiques : lire leurs conditions exactes ci-dessous.

Une erreur de paramètres produit généralement un JSON `error` et un statut 400. Une erreur interne inattendue du Plain produit un statut 500. Les exceptions de la recherche de tickers peuvent se traduire par une liste vide. Le VIX et l’historique sont facultatifs dans la réponse marché : leur absence ne doit pas être confondue avec une volatilité nulle.

## Graphiques et interface

Les graphiques montrent des remboursements non actualisés selon le cours final, en supposant que le produit n’a pas été rappelé. Le Phoenix ne montre que le dernier coupon, sans reconstruire les coupons antérieurs ni la mémoire. Le Plain montre tous les coupons accumulés si le seuil final est atteint. `pnl = payoff - nominal`. Ces courbes ne représentent pas la valeur théorique aujourd’hui.

Le Plain ajoute les points exacts des barrières et un point immédiatement inférieur avec `np.nextafter` afin de rendre visibles les sauts de remboursement. À égalité, les comparaisons `>=` donnent le remboursement favorable.

Le HTML gère les formulaires, les états de chargement, les erreurs, les huit indicateurs communs et les interactions du SVG. Il ne remplace pas les contrôles du serveur. Les probabilités de rappel du calendrier sont calculées sur toutes les simulations, pas uniquement celles encore en vie.

## Démarrage

La dernière instruction lance Flask sur `127.0.0.1`, port 5001 par défaut, avec `debug=False`. `PORT` permet de changer le port. Après une modification Python, arrêter puis relancer le serveur.


## Rappel anticipé optionnel

Le Plain reçoit `has_autocall=True` par défaut. La case décochée envoie `False` : aucune sortie anticipée, tous les coupons payables uniquement si le seuil final est atteint à maturité, protection du capital inchangée. Le premier rappel autorisé est alors ignoré. Les constats intermédiaires ne créent aucun coupon acquis. Exemple : quatre constats à 4 % donnent 16 % à maturité si le seuil final est atteint, sinon 0 %.

## Code actuel expliqué fonction par fonction

Les extraits suivants reproduisent les fonctions du fichier source au moment de la rédaction. Les fonctions commençant par `_` sont des aides internes.

### `_grid`

```python
def _grid(centres, n_points=121, low=0.4, high=1.6):
    """Construit la grille de prix finaux S_T pour les graphes.

    Je vais de min(centres) x low à max(centres) x high, avec n_points points.
    """
    lo = max(0.01, min(centres) * low)
    hi = max(centres) * high
    return np.linspace(lo, hi, n_points)
```

**Traduction en phrase :** Je fabrique une série régulière de cours finaux autour des niveaux utiles afin de tracer le remboursement.

### `_err`

```python
def _err(message, code=400):
    """Renvoie une erreur au site (affichée en rouge sous le bouton)."""
    return jsonify({"error": message}), code
```

**Traduction en phrase :** Je renvoie un message d’erreur JSON accompagné de son statut HTTP.

### `api_search_ticker`

```python
@app.get("/api/search_ticker")
def api_search_ticker():
    """Route GET /api/search_ticker?q=... : suggestions de tickers."""
    query = request.args.get("q", "").strip()
    if len(query) < 1:
        return jsonify({"results": []})
    try:
        return jsonify({"results": search_tickers(query)})
    except Exception as e:
        return _err(str(e))
```

**Traduction en phrase :** Je récupère le texte recherché et renvoie les correspondances de symboles au navigateur.

### `api_market`

```python
@app.get("/api/market/<ticker>")
def api_market(ticker):
    """Route GET /api/market/<ticker> : spot, devise, VIX et vol historique.

    Si la vol historique n'est pas dispo (ticker récent), je renvoie None et
    le site se rabat sur le VIX.
    """
    try:
        S0 = get_spot(ticker)
        devise = get_devise(ticker)
        try:
            vix = get_vix()
        except Exception:
            vix = None  # Le VIX ne doit pas bloquer le spot ni la volatilité historique.
        # si pas assez d'historique (ticker récent) je mets None, le site prendra le VIX
        try:
            vol_hist = round(get_vol_historique(ticker), 4)
        except Exception:
            vol_hist = None
        return jsonify({
            "S0": round(S0, 4),
            "devise": devise,
            "vix": None if vix is None else round(vix, 4),
            "vol_hist": vol_hist,
        })
    except Exception as e:
        return _err(f"Impossible de récupérer les données pour '{ticker}' : {e}")
```

**Traduction en phrase :** Je récupère les données du titre ; une absence du VIX ou de l’historique peut être signalée par une valeur manquante sans empêcher le retour des autres données.

### `index`

```python
@app.get("/")
def index():
    """Route GET / : affiche la page du site."""
    return render_template("index.html")
```

**Traduction en phrase :** Je fournis au navigateur le fichier HTML qui contient l’interface du pricer.

### `_est_fini`

```python
def _est_fini(x):
    """Vrai si x est un vrai nombre fini.

    J'ai besoin de ce check car NaN passe le test "sigma <= 0"
    (NaN <= 0 donne False).
    """
    return isinstance(x, (int, float)) and not isinstance(x, bool) and np.isfinite(x)
```

**Traduction en phrase :** Je vérifie que la valeur est un nombre réel fini et pas un booléen.

### `valider_parametres_phoenix`

```python
def valider_parametres_phoenix(S0, r, q, sigma, obs_dates, K_auto, B_phoenix, B_pdi,
                                coupon, n_simulations, has_autocall,
                                bonus_threshold, bonus_amount, strike_pct):
    # tout doit être un vrai nombre
    """Vérifie tous les paramètres du Phoenix avant la simulation.

    Mon formulaire bloque déjà les valeurs absurdes, mais on peut le contourner,
    donc je revérifie tout ici : nombres finis, vol et taux réalistes,
    protection <= coupon <= rappel, dates strictement croissantes, coupons
    positifs, nombre de simulations raisonnable.
    Les valeurs arrivent déjà en décimal (0.25 = 25 %).
    Lève une ValueError avec un message clair à la première erreur.
    """
    for nom, valeur in [("Le spot", S0), ("Le taux", r), ("Le dividende", q),
                        ("La volatilité", sigma), ("La barrière de rappel", K_auto),
                        ("La barrière coupon", B_phoenix), ("La barrière de protection", B_pdi),
                        ("Le bonus", bonus_amount), ("Le strike", strike_pct)]:
        if not _est_fini(valeur):
            raise ValueError(f"{nom} doit être un nombre.")

    # marché
    if S0 <= 0:
        raise ValueError("Le spot doit être strictement positif.")
    if sigma <= 0:
        raise ValueError("La volatilité doit être strictement positive.")
    if sigma > SIGMA_MAX:
        raise ValueError(f"Volatilité de {sigma:.0%} irréaliste (max {SIGMA_MAX:.0%}).")
    if abs(r) > TAUX_MAX:
        raise ValueError(f"Taux de {r:.0%} irréaliste (entre -{TAUX_MAX:.0%} et {TAUX_MAX:.0%}).")
    if q < 0 or q > TAUX_MAX:
        raise ValueError(f"Le dividende doit être compris entre 0 et {TAUX_MAX:.0%}.")

    # barrières : protection <= coupon <= rappel
    if strike_pct <= 0:
        raise ValueError("Le strike doit être strictement positif.")
    if min(K_auto, B_phoenix, B_pdi) <= 0:
        raise ValueError("Les barrières doivent être strictement positives.")
    if B_pdi > B_phoenix:
        raise ValueError("La barrière de protection doit être inférieure ou égale "
                         "à la barrière coupon.")
    if has_autocall and B_phoenix > K_auto:
        raise ValueError("La barrière coupon doit être inférieure ou égale "
                         "à la barrière de rappel.")

    # dates : au moins une, positives, dans l'ordre
    if not obs_dates:
        raise ValueError("Il faut au moins une date d'observation.")
    if not all(_est_fini(t) for t in obs_dates):
        raise ValueError("Les dates d'observation doivent être des nombres.")
    if obs_dates[0] <= 0:
        raise ValueError("La première date d'observation doit être après aujourd'hui.")
    for avant, apres in zip(obs_dates, obs_dates[1:]):
        if apres <= avant:
            raise ValueError(f"Les dates d'observation doivent être strictement croissantes "
                             f"(problème entre {avant} et {apres}).")
    if obs_dates[-1] > MATURITE_MAX:
        raise ValueError(f"Maturité de {obs_dates[-1]} ans irréaliste (max {MATURITE_MAX:.0f}).")

    # coupons : un seul montant ou une liste (step-up) avec un coupon par date
    coupons = coupon if isinstance(coupon, list) else [coupon]
    if isinstance(coupon, list) and len(coupon) != len(obs_dates):
        raise ValueError(f"Il faut un coupon par date d'observation "
                         f"({len(obs_dates)} dates, {len(coupon)} coupons).")
    for c in coupons:
        if not _est_fini(c):
            raise ValueError("Les coupons doivent être des nombres.")
        if c < 0:
            raise ValueError("Un coupon ne peut pas être négatif.")
        if c > COUPON_MAX:
            raise ValueError(f"Coupon de {c:.0%} sur une période irréaliste "
                             f"(max {COUPON_MAX:.0%}).")

    # bonus
    if bonus_amount < 0:
        raise ValueError("Le bonus ne peut pas être négatif.")
    if bonus_threshold is not None and (not _est_fini(bonus_threshold) or bonus_threshold <= 0):
        raise ValueError("Le seuil du bonus doit être strictement positif.")

    # simulations
    if not N_SIM_MIN <= n_simulations <= N_SIM_MAX:
        raise ValueError(f"Le nombre de simulations doit être entre {N_SIM_MIN:,} et "
                         f"{N_SIM_MAX:,}.".replace(",", " "))
```

**Traduction en phrase :** Je contrôle les paramètres de marché, l’ordre des barrières, les dates et les coupons avant le lancement du Phoenix.

### `_to_bool`

```python
def _to_bool(valeur, nom):
    """Convertit un true/false venu du JSON en vrai booléen.

    Attention : bool("false") donne True en Python, d'où cette fonction.
    """
    if isinstance(valeur, bool):
        return valeur
    if isinstance(valeur, str) and valeur.strip().lower() in ("true", "1", "oui", "yes"):
        return True
    if isinstance(valeur, str) and valeur.strip().lower() in ("false", "0", "non", "no"):
        return False
    if valeur in (0, 1):
        return bool(valeur)
    raise ValueError(f"{nom} doit valoir true ou false (reçu : {valeur!r}).")
```

**Traduction en phrase :** Je traduis explicitement les valeurs autorisées en vrai ou faux ; le texte false ne doit pas devenir vrai simplement parce qu’il est non vide.

### `_optionnel`

```python
def _optionnel(data, cle, defaut=None):
    """Renvoie la valeur par défaut si le champ est absent ou vide dans le formulaire."""
    valeur = data.get(cle, defaut)
    return defaut if valeur in (None, "") else valeur
```

**Traduction en phrase :** Si une valeur est absente ou vide, je prends sa valeur par défaut.

### `_dates_observation`

```python
def _dates_observation(data):
    """Construit la liste des dates d'observation (en années).

    Deux possibilités : une liste directe (obs_dates), ou la maturité T
    + la fréquence (1, 2, 4 ou 12 obs par an). C'est la deuxième que
    j'utilise sur le site.
    """
    if _optionnel(data, "obs_dates") is not None:
        dates = data["obs_dates"]
        if not isinstance(dates, list):
            raise ValueError("obs_dates doit être une liste, ex : [0.5, 1, 1.5, 2].")
        return [float(t) for t in dates]

    T = float(data["T"])
    frequence = int(data.get("frequence", 1))
    if frequence not in (1, 2, 4, 12):
        raise ValueError("La fréquence doit être 1 (annuelle), 2, 4 ou 12 (mensuelle).")
    # T doit tomber pile sur un nombre entier de périodes
    n_obs = T * frequence
    if T <= 0 or abs(n_obs - round(n_obs)) > 1e-9:
        raise ValueError(f"Avec une fréquence de {frequence}/an, la maturité doit être un "
                         f"multiple de {1 / frequence:g} an (reçu : T = {T}).")
    return [k / frequence for k in range(1, int(round(n_obs)) + 1)]
```

**Traduction en phrase :** Je conserve une liste de dates fournie ou je construis des constats réguliers à partir de la maturité et de la fréquence.

### `api_phoenix`

```python
@app.post("/api/phoenix")
def api_phoenix():
    """Route POST /api/phoenix : prix, stats des scénarios et graphe du Phoenix.

    Barrières, coupons et bonus arrivent en % (70 = 70 %), comme r, q et sigma.
    Je renvoie les montants en devise du nominal, et en % du nominal pour
    les champs qui finissent par _pct.
    """
    try:
        data = request.get_json(force=True)

        # marché
        S0 = float(data["S0"])
        r = float(data["r"]) / 100
        q = float(data.get("q", 0)) / 100
        sigma = float(data["sigma"]) / 100
        nominal = float(data.get("nominal", 1000))
        if not np.isfinite(nominal) or nominal <= 0:
            return _err("Le nominal doit être strictement positif.")

        # produit
        obs_dates = _dates_observation(data)
        K_auto = float(data.get("K_auto", 100)) / 100
        B_phoenix = float(data["B_phoenix"]) / 100
        B_pdi = float(data["B_pdi"]) / 100
        strike_pct = float(data.get("strike_pct", 100)) / 100

        coupon_brut = data["coupon"]
        if isinstance(coupon_brut, list):
            coupon = [float(c) / 100 for c in coupon_brut]   # step-up
        else:
            coupon = float(coupon_brut) / 100                # coupon fixe

        memory = _to_bool(data.get("memory", False), "memory")
        has_autocall = _to_bool(data.get("has_autocall", True), "has_autocall")

        bonus_threshold = _optionnel(data, "bonus_threshold")
        if bonus_threshold is not None:
            bonus_threshold = float(bonus_threshold) / 100
        bonus_amount = float(_optionnel(data, "bonus_amount", 0)) / 100

        n_simulations = int(data.get("n_simulations", 50000))
        seed = _optionnel(data, "seed")
        seed = int(seed) if seed is not None else None

        # je vérifie tout avant de lancer la simu
        valider_parametres_phoenix(S0, r, q, sigma, obs_dates, K_auto, B_phoenix, B_pdi,
                                   coupon, n_simulations, has_autocall,
                                   bonus_threshold, bonus_amount, strike_pct)

        # prix + stats des scénarios
        res = analyse_phoenix(S0, r, q, sigma, obs_dates, K_auto, B_phoenix, B_pdi, coupon,
                              n_simulations, memory=memory, has_autocall=has_autocall,
                              bonus_threshold=bonus_threshold, bonus_amount=bonus_amount,
                              strike_pct=strike_pct, seed=seed)

        # je passe les barrières en prix pour les tracer sur le graphe
        strike_reference = strike_pct * S0
        niveaux = {
            "strike": strike_reference,
            "autocall": K_auto * strike_reference if has_autocall else None,
            "coupon": B_phoenix * strike_reference,
            "protection": B_pdi * strike_reference,
        }
        centres = [S0] + [v for v in niveaux.values() if v is not None]
        ST_grid = _grid(centres, n_points=241, low=0.6, high=1.3)

        # payoff à maturité si pas rappelé
        coupon_final = res["coupon_schedule"][-1]
        payoff = payoff_phoenix_maturite(ST_grid, S0, B_phoenix, B_pdi, coupon_final,
                                         strike_pct, bonus_threshold, bonus_amount)
        payoff_total = payoff["total"] * nominal
        # P&L du client : il a payé le nominal (100 %), pas le prix théorique
        pnl = payoff_total - nominal

        # petit raccourci que je me suis fait pour passer en % arrondi
        def pct(x):
            return round(100 * float(x), 4)

        return jsonify({
            "prix": round(res["prix"] * nominal, 4),
            "prix_pct": pct(res["prix"]),
            "ic95_pct": [pct(res["ic95"][0]), pct(res["ic95"][1])],
            "marge_emetteur_pct": pct(res["marge_emetteur"]),
            "duree_de_vie_moyenne": round(res["duree_de_vie_moyenne"], 4),
            "coupons_moyens_actualises_pct": pct(res["coupons_moyens_actualises"]),
            "obs_dates": res["obs_dates"],
            "coupon_schedule_pct": [pct(c) for c in res["coupon_schedule"]],
            "proba_rappel_par_date_pct": [pct(p) for p in res["proba_rappel_par_date"]],
            "proba_maturite_pct": pct(res["proba_maturite"]),
            "proba_perte_capital_pct": pct(res["proba_perte_capital"]),
            "remboursement_moyen_si_perte_pct": (
                None if res["remboursement_moyen_si_perte"] is None
                else pct(res["remboursement_moyen_si_perte"])
            ),
            "niveaux": {k: (None if v is None else round(float(v), 4)) for k, v in niveaux.items()},
            "ST_grid": [round(float(x), 4) for x in ST_grid],
            "payoff": [round(float(x), 4) for x in payoff_total],
            "pnl": [round(float(x), 4) for x in pnl],
        })

    except KeyError as e:
        return _err(f"Paramètre manquant : {e}")
    except (TypeError, ValueError) as e:
        # mes messages de vérif, ou un float("abc") venu du formulaire
        return _err(str(e))
    except Exception as e:
        return _err(f"Erreur inattendue : {e}", 500)
```

**Traduction en phrase :** Je lis le formulaire Phoenix, transforme les pourcentages en décimaux, contrôle les données, appelle le moteur puis prépare les indicateurs et le graphique.

### `api_autocall`

```python
@app.post("/api/autocall")
def api_autocall():
    """Entrées du formulaire en %, calculs en décimal, montants en devise du nominal."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return _err("Le formulaire doit être un objet JSON.")
    try:
        produit = data.get("produit")
        if produit not in ("autocall_plain",):
            return _err("Produit autocall inconnu.")

        def nombre(cle, defaut=None):
            valeur = data.get(cle, defaut)
            if isinstance(valeur, bool) or valeur in (None, ""):
                raise ValueError(f"Paramètre manquant ou invalide : {cle}.")
            valeur = float(valeur)
            if not np.isfinite(valeur):
                raise ValueError(f"Le paramètre {cle} doit être fini.")
            return valeur

        S0 = nombre("S0")
        r, q, sigma = nombre("r") / 100, nombre("q", 0) / 100, nombre("sigma") / 100
        nominal = nombre("nominal", 1000)
        T, frequence = nombre("T"), nombre("frequence", 2)
        n = nombre("n_simulations", 50000)
        if not 0 < S0 <= 1e9 or not 0 < nominal <= 1e12:
            return _err("Spot et montant investi doivent être positifs et dans les limites autorisées.")
        if not -.5 <= r <= .5 or not 0 <= q <= .5 or not 0 <= sigma <= 2:
            return _err("Taux r : −50 à 50 %, dividende : 0 à 50 %, volatilité : 0 à 200 %.")
        if not 0 < T <= 30 or frequence not in (1, 2, 4, 12):
            return _err("Maturité : 0 à 30 ans ; fréquence : 1, 2, 4 ou 12 observations par an.")
        if not n.is_integer() or not 1000 <= n <= 500000:
            return _err("Le nombre de simulations doit être un entier entre 1 000 et 500 000.")
        dates = _dates_observation({"T": T, "frequence": int(frequence)})
        if int(n) * len(dates) > 6000000:
            return _err("Calcul trop volumineux : réduisez les simulations ou la fréquence (maximum 6 millions de constats simulés).")
        K_auto = nombre("K_auto", 100) / 100
        coupon = nombre("coupon") / 100
        if not 0 < K_auto <= 3 or not 0 <= coupon <= 1:
            return _err("Barrière : 0 à 300 % ; coupon par observation : 0 à 100 %.")
        protection = _to_bool(data.get("protection", True), "protection")
        B_pdi = nombre("B_pdi", 60) / 100 if protection else None
        has_autocall = _to_bool(data.get("has_autocall", True), "has_autocall")
        premiere = None
        if has_autocall:
            premiere = nombre("first_call_months", 0) / 12
        seed = nombre("seed", 42)
        if not seed.is_integer() or not 0 <= seed <= 2**32 - 1:
            return _err("La graine doit être un entier entre 0 et 4 294 967 295.")
        arguments = dict(S0=S0, r=r, q=q, sigma=sigma, obs_dates=dates, K_auto=K_auto,
                         B_pdi=B_pdi, coupon=coupon, n_simulations=int(n), seed=int(seed))
        res = analyse_autocall_plain(**arguments, first_call_date=premiere, has_autocall=has_autocall)
        # Remboursement final du Plain, sous l'hypothèse d'absence de rappel.
        niveaux = {"autocall": K_auto * S0 if has_autocall else None, "coupon": K_auto * S0,
                   "protection": None if B_pdi is None else B_pdi * S0}
        centres = [S0] + [v for v in niveaux.values() if v is not None]
        grille = _grid(centres, n_points=241, low=0.6, high=1.3)
        # Deux points de part et d'autre des seuils montrent leurs discontinuités.
        seuils = [v for v in niveaux.values() if v is not None]
        grille = np.unique(np.concatenate([grille, seuils, [np.nextafter(v, 0) for v in seuils]]))
        capital = np.ones_like(grille)
        if B_pdi is not None:
            capital = np.where(grille >= B_pdi * S0, 1.0, grille / S0)
        coupons_finaux = np.where(grille >= K_auto * S0, coupon * len(dates), 0.0)
        remboursement = (capital + coupons_finaux) * nominal
        return jsonify({
            "ST_grid": grille.tolist(), "payoff": remboursement.tolist(),
            "pnl": (remboursement - nominal).tolist(), "niveaux": niveaux,
            "marge_emetteur_pct": round(res["marge_emetteur"] * 100, 4),
            "produit": produit, "has_autocall": has_autocall,
            "prix": round(res["prix"] * nominal, 4),
            "prix_pct": round(res["prix"] * 100, 4),
            "ic95_pct": [round(v * 100, 4) for v in res["ic95"]],
            "erreur_type": round(res["erreur_type"] * nominal, 6),
            "ecart_souscription_pct": round(res["marge_emetteur"] * 100, 4),
            "proba_perte_capital_pct": round(res["proba_perte_capital"] * 100, 4),
            "proba_maturite_pct": round(res["proba_maturite"] * 100, 4),
            "proba_rappel_par_date_pct": [round(v * 100, 4) for v in res["proba_rappel_par_date"]],
            "duree_de_vie_moyenne": round(res["duree_de_vie_moyenne"], 4),
            "coupons_moyens_actualises_pct": round(res["coupons_moyens_actualises"] * 100, 4),
            "nombre_moyen_coupons": round(res["nombre_moyen_coupons"], 4),
            "remboursement_moyen_si_perte_pct": None if res["remboursement_moyen_si_perte"] is None else round(res["remboursement_moyen_si_perte"] * 100, 4),
            "obs_dates": res["obs_dates"], "nominal": nominal, "S0": S0,
            "coupon_pct": coupon * 100, "K_auto_pct": K_auto * 100,
            "B_pdi_pct": None if B_pdi is None else B_pdi * 100,
            "first_call_date": premiere, "n_simulations": int(n), "seed": int(seed),
        })
    except (TypeError, ValueError, OverflowError) as e:
        return _err(str(e))
    except Exception:
        return _err("Le calcul autocall a échoué. Vérifiez les paramètres et réessayez.", 500)
```

**Traduction en phrase :** Je vérifie que le produit demandé est le Plain, valide ses paramètres, calcule sa valeur puis prépare les mêmes indicateurs et un remboursement final pour le graphique.
