# Script oral guidé par le code — Théo et Joseph

Chaque écran suit le même ordre : **ouvrir les lignes → les montrer → donner l’explication juste dessous**. Les indications ne se lisent pas. Garder le bloc visible pendant son explication, puis passer au suivant. Les lignes correspondent au code actuel. Les blocs sont volontairement courts ; ne pas lire les commentaires Python à voix haute. Prévoir environ 18 à 22 minutes avec les manipulations, à mesurer en répétition.

## 1. Présenter le projet — Théo

### Écran 1.1

**Montrer : l’application.**

**À dire en pointant ce passage :**

On va vous présenter notre pricer. On a un Phoenix et un Plain, avec ou sans rappel. On va suivre les données jusqu’au prix, puis montrer un calcul dans l’application.

## 2. Les imports et le rôle du serveur — Théo

### Écran 2.1

**Montrer [main.py, ligne 4](../main.py#L4) — lignes 4 à 4.**

```python
from market_data_engine import search_tickers, get_spot, get_devise, get_vix, get_vol_historique
```

**À dire en pointant ce passage :**

Ici, on récupère les fonctions de marché. main.py peut les appeler sans recopier leur code.

### Écran 2.2

**Montrer [main.py, ligne 5](../main.py#L5) — lignes 5 à 6.**

```python
from strutu_engine import (analyse_phoenix, payoff_phoenix_maturite,
                           analyse_autocall_plain)
```

**À dire en pointant ce passage :**

Juste en dessous, on importe les fonctions qui calculent le Phoenix et le Plain. main.py fait le lien avec la page : il reçoit les paramètres, appelle ces fonctions et renvoie les résultats.

## 3. Charger les cours et appeler la volatilité — Théo

### Écran 3.1

**Montrer [market_data_engine.py, ligne 3](../market_data_engine.py#L3) — lignes 3 à 3.**

```python
from volatility_engine import historical_volatility
```

**À dire en pointant ce passage :**

Cet import est important : le calcul de volatilité est dans l’autre fichier. Ici, on va seulement l’appeler. Joseph va vous montrer son contenu juste après.

### Écran 3.2

**Montrer [market_data_engine.py, ligne 54](../market_data_engine.py#L54) — lignes 54 à 56.**

```python
    data = asset.history(
        period=periode,
        auto_adjust=True
```

**À dire en pointant ce passage :**

Avec history, on demande les cours sur la période choisie. auto_adjust=True demande les cours ajustés.

### Écran 3.3

**Montrer [market_data_engine.py, ligne 60](../market_data_engine.py#L60) — lignes 60 à 66.**

```python
    if data.empty:
        raise ValueError(
            f"Aucune donnée historique disponible pour {ticker}"
        )

    # 4. Extraction des cours de clôture
    prices = data["Close"].dropna()
```

**À dire en pointant ce passage :**

Si Yahoo ne renvoie rien, on arrête avec un message. Sinon, on garde la colonne Close et on retire les valeurs manquantes avec dropna.

### Écran 3.4

**Montrer [market_data_engine.py, ligne 89](../market_data_engine.py#L89) — lignes 89 à 98.**

```python
    cours = get_historical_prices(ticker, periode)

    # 2. Vérification du nombre de cours
    if len(cours) < 20:
        raise ValueError(
            "Pas assez d'historique pour calculer une volatilité."
        )

    # 3. Calcul de la volatilité historique
    vol = historical_volatility(cours)
```

**À dire en pointant ce passage :**

Dans get_vol_historique, on récupère ces cours. On exige au moins vingt observations, puis cette ligne appelle la fonction importée au début.

### Écran 3.5

**Montrer [market_data_engine.py, ligne 101](../market_data_engine.py#L101) — lignes 101 à 101.**

```python
    return float(vol * 100)
```

**À dire en pointant ce passage :**

Elle renvoie un décimal. Ici, on multiplie par cent pour le formulaire : 0,25 devient 25 %.

**Passage de parole :** « Joseph, tu peux nous montrer comment cette fonction calcule la volatilité ? »

## 4. Calculer la volatilité — Joseph

### Écran 4.1

**Montrer [volatility_engine.py, ligne 21](../volatility_engine.py#L21) — lignes 21 à 21.**

```python
    prices = np.asarray(prices, dtype=float)
```

**À dire en pointant ce passage :**

On reçoit les cours montrés par Théo. Cette ligne les transforme en tableau de nombres pour travailler avec NumPy.

### Écran 4.2

**Montrer [volatility_engine.py, ligne 32](../volatility_engine.py#L32) — lignes 32 à 32.**

```python
    returns = np.log(prices[1:] / prices[:-1])
```

**À dire en pointant ce passage :**

Ici, on compare chaque prix au précédent. Le premier morceau commence au deuxième cours ; le second s’arrête à l’avant-dernier. On divise les deux, puis on prend le logarithme. Trois cours donnent donc deux rendements.

### Écran 4.3

**Montrer [volatility_engine.py, ligne 58](../volatility_engine.py#L58) — lignes 58 à 61.**

```python
    returns = log_returns(prices)

    # 2. Vérification du nombre de rendements
    if len(returns) < 2:
```

**À dire en pointant ce passage :**

La fonction de volatilité appelle celle qu’on vient de voir. Elle demande au moins deux rendements, donc trois cours. Les vingt cours du module marché sont une exigence supplémentaire pour l’application.

### Écran 4.4

**Montrer [volatility_engine.py, ligne 73](../volatility_engine.py#L73) — lignes 73 à 73.**

```python
    daily_volatility = np.std(returns, ddof=1)
```

**À dire en pointant ce passage :**

np.std calcule la dispersion des rendements autour de leur moyenne. ddof=1 utilise le nombre de rendements moins un au dénominateur.

### Écran 4.5

**Montrer [volatility_engine.py, ligne 76](../volatility_engine.py#L76) — lignes 76 à 79.**

```python
    annual_volatility = daily_volatility * np.sqrt(annualization)

    # 6. Retour en décimal
    return float(annual_volatility)
```

**À dire en pointant ce passage :**

On annualise avec racine de 252 pour des cours journaliers. Le résultat reste en décimal. C’est ce résultat que market data multiplie par cent pour l’affichage.

**Passage de parole :** « Cette volatilité devient sigma dans le moteur. Théo, tu peux montrer où elle intervient ? »

## 5. Créer les trajectoires — Théo

### Écran 5.1

**Montrer [strutu_engine.py, ligne 29](../strutu_engine.py#L29) — lignes 29 à 31.**

```python
    n_dates = len(obs_dates)
    prix = np.zeros((n_simulations, n_dates + 1))
    prix[:, 0] = S0  # je fais partir tous les scénarios du même spot
```

**À dire en pointant ce passage :**

On crée une ligne par scénario et une colonne par constat, plus une pour le départ. Ici, les deux-points veulent dire toutes les lignes : tous les scénarios commencent à S0.

### Écran 5.2

**Montrer [strutu_engine.py, ligne 33](../strutu_engine.py#L33) — lignes 33 à 37.**

```python
    t_precedent = 0.0
    for i in range(n_dates):
        t = obs_dates[i]
        dt = t - t_precedent  # temps écoulé depuis la dernière obs
        Z = rng.standard_normal(n_simulations)  # je tire un choc par scénario
```

**À dire en pointant ce passage :**

À chaque date, dt mesure le temps écoulé. standard_normal tire un choc aléatoire par scénario.

### Écran 5.3

**Montrer [strutu_engine.py, ligne 39](../strutu_engine.py#L39) — lignes 39 à 42.**

```python
        croissance = (r - q - sigma**2 / 2) * dt
        choc = sigma * np.sqrt(dt) * Z
        prix[:, i + 1] = prix[:, i] * np.exp(croissance + choc)
        t_precedent = t
```

**À dire en pointant ce passage :**

On retrouve le sigma expliqué par Joseph. La croissance dépend du taux, du dividende et de la correction de variance. Le choc dépend de sigma et du tirage. Avec l’exponentielle, on obtient le nouveau cours à partir du précédent. C’est un modèle risque-neutre, pas une prévision de performance.

### Écran 5.4

**Montrer [strutu_engine.py, ligne 44](../strutu_engine.py#L44) — lignes 44 à 44.**

```python
    return prix
```

**À dire en pointant ce passage :**

On renvoie les cours, sans encore calculer de paiement. Le Phoenix et le Plain utilisent ce même simulateur, puis appliquent leurs propres règles.

## 6. Phoenix : coupons, mémoire, rappel et bonus — Théo

### Écran 6.1

**Montrer [strutu_engine.py, ligne 86](../strutu_engine.py#L86) — lignes 86 à 86.**

```python
        actifs = ~rappele
```

**À dire en pointant ce passage :**

On commence par garder les scénarios encore en vie. Le tilde inverse rappele : ceux qui sont déjà terminés ne doivent plus recevoir de paiement.

### Écran 6.2

**Montrer [strutu_engine.py, ligne 90](../strutu_engine.py#L90) — lignes 90 à 93.**

```python
        if has_autocall and k < n_dates:
            autocall_now = actifs & (S_k >= K_auto_level)
        else:
            autocall_now = np.zeros(n_simulations, dtype=bool)
```

**À dire en pointant ce passage :**

Si le rappel est activé, on teste sa barrière avant maturité. Sinon, aucun scénario n’est rappelé. Décocher la case fait donc aller le Phoenix jusqu’à la fin. k inférieur à n_dates réserve la dernière date au remboursement final.

### Écran 6.3

**Montrer [strutu_engine.py, ligne 95](../strutu_engine.py#L95) — lignes 95 à 95.**

```python
        coupon_du = actifs & (S_k >= B_phoenix_level)
```

**À dire en pointant ce passage :**

Le coupon a sa propre condition : le scénario doit être actif et au-dessus du seuil coupon. Ça reste vrai même quand on désactive le rappel : les coupons peuvent toujours être versés en cours de vie.

### Écran 6.4

**Montrer [strutu_engine.py, ligne 97](../strutu_engine.py#L97) — lignes 97 à 105.**

```python
        coupon_periode = coupon_schedule[k - 1]
        if memory:
            # j'accumule le coupon de la période, et je paie tout le stock dès que c'est au-dessus
            coupons_en_attente += np.where(actifs, coupon_periode, 0.0)
            montant_coupon = np.where(coupon_du, coupons_en_attente, 0.0)
            coupons_en_attente = np.where(coupon_du, 0.0, coupons_en_attente)  # je remets à 0 si c'est payé
        else:
            # sans mémoire un coupon raté est perdu
            montant_coupon = np.where(coupon_du, coupon_periode, 0.0)
```

**À dire en pointant ce passage :**

On prend le coupon de la période. Avec mémoire, on l’ajoute au stock en attente. Si le coupon est dû, on paie ce stock, puis on le remet à zéro. Sans mémoire, on paie seulement le coupon courant. Par exemple, un premier coupon de 4 % manqué puis un deuxième favorable donnent 8 % avec mémoire, contre 4 % sans mémoire.

### Écran 6.5

**Montrer [strutu_engine.py, ligne 107](../strutu_engine.py#L107) — lignes 107 à 113.**

```python
        coupons_actualises += montant_coupon * actualisation
        flux_actualises += montant_coupon * actualisation
        # si rappel : je rends le nominal (1 = 100 %)
        flux_actualises += np.where(autocall_now, 1.0 * actualisation, 0.0)

        date_rappel[autocall_now] = k - 1
        rappele = rappele | autocall_now
```

**À dire en pointant ce passage :**

On actualise le coupon à sa date. En cas de rappel, on rend aussi le nominal. Puis on conserve les scénarios déjà rappelés et on ajoute ceux qui viennent de l’être.

### Écran 6.6

**Montrer [strutu_engine.py, ligne 122](../strutu_engine.py#L122) — lignes 122 à 127.**

```python
    remboursement_T = np.where(S_T >= B_pdi_level, 1.0, S_T / strike_reference)
    if bonus_threshold is not None:
        bonus_du = non_rappelees & (S_T >= bonus_threshold * strike_reference)
        remboursement_T = remboursement_T + np.where(bonus_du, bonus_amount, 0.0)

    flux_actualises += np.where(non_rappelees, remboursement_T * actualisation_T, 0.0)
```

**À dire en pointant ce passage :**

À maturité, le capital vaut un si la protection est respectée, sinon le ratio du cours final sur la référence. Ensuite, ce bloc ajoute le bonus si un seuil est défini et atteint, et si le scénario n’a pas été rappelé. Avec une référence à 100, un seuil à 110 et un bonus de 5 %, finir à 115 ajoute 50 pour 1 000 investis. Le dernier coupon a déjà été traité dans la boucle : le bonus vient en plus. Enfin, on actualise ce remboursement final.

**Passage de parole :** « Joseph va montrer le Plain : il utilise les mêmes trajectoires, mais les coupons sont payés d’un coup. »

## 7. Plain : déterminer le rappel et les coupons — Joseph

### Écran 7.1

**Montrer [strutu_engine.py, ligne 296](../strutu_engine.py#L296) — lignes 296 à 297.**

```python
    for k in range(n_dates):
        au_dessus = prix[:, k + 1] >= K_auto * S0
```

**À dire en pointant ce passage :**

On reprend les trajectoires du simulateur de Théo. Ici, k commence à zéro, mais la colonne zéro contient S0 : on lit donc le cours dans la colonne k+1. On le compare au seuil de rappel.

### Écran 7.2

**Montrer [strutu_engine.py, ligne 298](../strutu_engine.py#L298) — lignes 298 à 302.**

```python
        if has_autocall:
            rappel_autorise = first_call_date is None or dates[k] >= first_call_date
            # La dernière observation relève du remboursement final, pas d'un rappel.
            if k < n_dates - 1 and rappel_autorise:
                rappel_du = (~rappele) & au_dessus
```

**À dire en pointant ce passage :**

Le rappel doit être activé, la première date autorisée doit être atteinte, et on doit être avant maturité. On ne garde ensuite que les scénarios encore actifs au-dessus du seuil.

### Écran 7.3

**Montrer [strutu_engine.py, ligne 303](../strutu_engine.py#L303) — lignes 303 à 307.**

```python
                coupons_payes[rappel_du] = coupon * (k + 1)
                nombre_coupons[rappel_du] = k + 1
                date_paiement[rappel_du] = dates[k]
                date_rappel[rappel_du] = k
                rappele[rappel_du] = True
```

**À dire en pointant ce passage :**

Pour ces scénarios, on stocke les coupons accumulés et la date du paiement. Au deuxième constat, k+1 vaut deux : avec 4 %, ça fait 8 % de coupons. Les crochets modifient seulement les scénarios rappelés. On les marque ensuite comme terminés. La date stockée servira à l’actualisation.

## 8. Plain sans rappel : la condition finale — Joseph

### Écran 8.1

**Montrer [strutu_engine.py, ligne 376](../strutu_engine.py#L376) — lignes 376 à 377.**

```python
def analyse_autocall_plain(S0, r, q, sigma, obs_dates, K_auto, B_pdi, coupon,
                            n_simulations=50000, first_call_date=None, seed=None, has_autocall=True):
```

**À dire en pointant ce passage :**

La même fonction reçoit has_autocall. Par défaut, le rappel est actif. La case décochée transmet faux et on ne passe plus dans le bloc de rappel que je viens de montrer.

### Écran 8.2

**Montrer [strutu_engine.py, ligne 309](../strutu_engine.py#L309) — lignes 309 à 314.**

```python
    non_rappeles = ~rappele
    S_T = prix[:, -1]
    # Le rappel est optionnel ; la condition finale des coupons reste identique.
    coupon_final_du = non_rappeles & (S_T >= K_auto * S0)
    coupons_payes[coupon_final_du] = coupon * n_dates
    nombre_coupons[coupon_final_du] = n_dates
```

**À dire en pointant ce passage :**

On traite ensuite ceux qui arrivent à maturité. Si le cours final atteint le seuil, on attribue tous les coupons. Sinon, ils restent à zéro. Avec six constats à 4 %, ça fait 24 % ou aucun coupon. Un constat favorable au début ne suffit pas à acquérir un coupon.

**Passage de parole :** « Théo va montrer la règle du capital : elle est indépendante du rappel et des coupons. »

## 9. Le remboursement du capital — Théo

### Écran 9.1

**Montrer [strutu_engine.py, ligne 291](../strutu_engine.py#L291) — lignes 291 à 291.**

```python
    remboursement = np.ones(n_simulations)
```

**À dire en pointant ce passage :**

Le remboursement commence à un pour chaque scénario, donc à cent pour cent du nominal.

### Écran 9.2

**Montrer [strutu_engine.py, ligne 316](../strutu_engine.py#L316) — lignes 316 à 319.**

```python
    perte_capital = np.zeros(n_simulations, dtype=bool)
    if B_pdi is not None:
        perte_capital = non_rappeles & (S_T < B_pdi * S0)
        remboursement[perte_capital] = S_T[perte_capital] / S0
```

**À dire en pointant ce passage :**

Si une barrière est définie, on sélectionne les scénarios non rappelés strictement sous cette barrière. Pour eux, on remplace le nominal par S_T sur S0. Un départ à 100 et une arrivée à 50 donnent donc 50 % du capital. À la barrière exactement, le nominal reste entier. Si B_pdi vaut None, ce bloc ne s’exécute pas : le capital reste à un.

**Passage de parole :** « Joseph, maintenant qu’on a les montants et leurs dates, comment on obtient le prix ? »

## 10. Passer des flux au prix — Joseph

### Écran 10.1

**Montrer [strutu_engine.py, ligne 346](../strutu_engine.py#L346) — lignes 346 à 347.**

```python
    actualisation = np.exp(-r * res["date_paiement"])
    flux = (res["remboursement"] + res["coupons"]) * actualisation
```

**À dire en pointant ce passage :**

Dans res, on récupère les tableaux calculés juste avant. On additionne le capital et les coupons, puis on actualise chaque scénario à sa date de sortie avec exp de moins r fois t.

### Écran 10.2

**Montrer [strutu_engine.py, ligne 350](../strutu_engine.py#L350) — lignes 350 à 351.**

```python
    valeur = float(np.mean(flux))
    erreur_type = float(np.std(flux, ddof=1) / np.sqrt(n_simulations))
```

**À dire en pointant ce passage :**

np.mean fait la moyenne : c’est le prix pour un nominal de un. Si on obtient 0,95, ça représente 950 pour 1 000 investis. Le capital est déjà inclus, donc on n’ajoute pas un zéro-coupon à côté. La ligne suivante mesure la précision de cette moyenne, pas l’incertitude sur toutes les hypothèses du modèle.

**Passage de parole :** « Théo va vous montrer les autres résultats tirés de ces mêmes scénarios. »

## 11. Calculer les indicateurs — Théo

### Écran 11.1

**Montrer [strutu_engine.py, ligne 363](../strutu_engine.py#L363) — lignes 363 à 368.**

```python
        "proba_rappel_par_date": [float(np.mean(res["date_rappel"] == k)) for k in range(len(dates))],
        "proba_maturite": float(np.mean(res["date_rappel"] == -1)),
        "proba_perte_capital": float(np.mean(perte)),
        "remboursement_moyen_si_perte": remboursement_si_perte,
        "duree_de_vie_moyenne": float(np.mean(res["date_paiement"])),
        "coupons_moyens_actualises": float(np.mean(res["coupons"] * actualisation)),
```

**À dire en pointant ce passage :**

Ici, on rassemble les statistiques. Moins un dans date_rappel veut dire jamais rappelé. La moyenne de cette condition donne la probabilité de maturité : vrai compte pour un, faux pour zéro. Pour la durée moyenne, on moyenne les dates de paiement. Les coupons sont eux aussi moyennés après actualisation. On ne simule pas de nouveaux cours pour chaque indicateur.

## 12. Relier le moteur au navigateur — Théo

### Écran 12.1

**Montrer [main.py, ligne 232](../main.py#L232) — lignes 232 à 232.**

```python
        sigma = float(data["sigma"]) / 100
```

**À dire en pointant ce passage :**

Dans la route Phoenix, on récupère sigma et on divise par cent. Le formulaire donne 25 ; le moteur doit recevoir 0,25. La route Plain fait la même conversion.

### Écran 12.2

**Montrer [main.py, ligne 378](../main.py#L378) — lignes 378 à 378.**

```python
        res = analyse_autocall_plain(**arguments, first_call_date=premiere, has_autocall=has_autocall)
```

**À dire en pointant ce passage :**

Dans la route Plain, cet appel lance l’analyse présentée par Joseph. Les deux étoiles transmettent le dictionnaire comme paramètres nommés. On transmet aussi la date de premier rappel et la case has_autocall.

### Écran 12.3

**Montrer [main.py, ligne 297](../main.py#L297) — lignes 297 à 298.**

```python
            "prix": round(res["prix"] * nominal, 4),
            "prix_pct": pct(res["prix"]),
```

**À dire en pointant ce passage :**

Pour le Phoenix, cette réponse montre les deux affichages : le prix normalisé fois le nominal donne le montant, et pct le transforme en pourcentage. Le Plain renvoie lui aussi ces deux informations.

### Écran 12.4

**Montrer [templates/index.html, ligne 729](../templates/index.html#L729) — lignes 729 à 732.**

```javascript
      const response=await fetch('/api/autocall',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload),signal:controller.signal});
      const data=await response.json();if(!response.ok)throw new Error(data.error||'Calcul indisponible.');
      if(version!==acSelectionVersion)return;
      afficherAutocall(data);status.textContent='Calcul terminé.';
```

**À dire en pointant ce passage :**

Dans le JavaScript, fetch envoie les paramètres au serveur. On lit sa réponse JSON et, si elle est correcte, afficherAutocall met les résultats à l’écran. Les calculs financiers restent en Python. On va maintenant montrer ce parcours dans l’application.

## 13. Manipuler les options dans l’application — Théo puis Joseph

### Écran 13.1

**Montrer : l’application.**

**À dire en pointant ce passage :**

Théo : Je montre d’abord les options du Phoenix. Sans rappel, les coupons restent périodiques et le produit va jusqu’à maturité. Pour le bonus, on renseigne un seuil et un montant ; il est ajouté à la fin si sa condition est remplie et si le produit est encore en vie.

Joseph : Pour le Plain, on prend trois ans, des constats semestriels et 4 % par constat. On calcule avec rappel, puis sans rappel, en gardant la même graine. Sans rappel, on doit voir trois ans de durée moyenne, cent pour cent à maturité et aucun rappel. Si le seuil final est atteint, les six coupons font 24 %, donc 1 240 versés pour 1 000 investis. Ce paiement futur n’est pas le prix aujourd’hui.

## 14. Montrer un test concret — Théo

### Écran 14.1

**Montrer [tests/test_engine.py, ligne 23](../tests/test_engine.py#L23) — lignes 23 à 31.**

```python
    def test_final_condition_not_intermediate_acquisition(self):
        paths=np.array([[100,110,80],[100,90,110],[100,120,50]],float)
        with patch.object(engine,'simulate_observation_dates',return_value=paths):
            result=engine.analyse_autocall_plain(100,0,0,.2,[1,2],1,.6,.04,3,has_autocall=False)
        self.assertAlmostEqual(result['prix'],(1+1.08+.5)/3)
        self.assertEqual(result['proba_rappel_par_date'],[0,0])
        self.assertEqual(result['proba_maturite'],1)
        self.assertEqual(result['duree_de_vie_moyenne'],2)
        self.assertAlmostEqual(result['coupons_moyens_actualises'],.08/3)
```

**À dire en pointant ce passage :**

Ce test donne directement trois trajectoires au moteur. La première passe au-dessus du seuil puis finit à 80 : aucun coupon. La deuxième finit à 110 : deux coupons de 4 %. La troisième finit à 50 : perte de la moitié du principal. La moyenne attendue est donc un, plus un virgule zéro huit, plus zéro virgule cinq, le tout divisé par trois. Les assertions vérifient aussi qu’il n’y a aucun rappel. Ça permet de contrôler la règle sans dépendre d’un tirage aléatoire.

## 15. Conclure — Joseph

### Écran 15.1

**Montrer : l’application.**

**À dire en pointant ce passage :**

On a donc suivi les cours, la volatilité, les trajectoires, les paiements et leur actualisation. Le modèle reste simplifié : taux, dividende et volatilité constants, sans smile ni défaut de l’émetteur. Les probabilités sont celles du modèle risque-neutre. Pour aller plus loin, on pourrait utiliser une courbe de taux et une volatilité calibrée sur les options.

