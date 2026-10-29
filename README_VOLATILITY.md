# volatility_engine.py — rendements et volatilité

[Retour au guide général](README.md)

Cette copie autonome contient exactement deux fonctions : les rendements logarithmiques et la volatilité historique close-to-close. EWMA, GARCH et volatilités glissantes ne sont pas implémentés ici, même si une docstring mentionne leurs usages possibles dans un module plus général.

## Pourquoi calculer une volatilité ?

Le simulateur a besoin de `sigma` pour mesurer l’amplitude des chocs aléatoires. La volatilité historique fournit une estimation à partir des variations passées, sans prévoir leur direction. Elle ne garantit pas la volatilité future et n’est pas automatiquement la volatilité implicite d’une option.

## Étape 1 : rendements logarithmiques

`r_t = log(S_t / S_precedent)`.

Avec les prix `[100, 101, 100]`, les deux rendements valent environ `[0,00995033, -0,00995033]`. Trois prix donnent deux rendements. `prices[1:]` garde les prix à partir du deuxième ; `prices[:-1]` garde tous les prix sauf le dernier. Leur division met donc chaque prix en face de son prédécesseur. Le logarithme transforme ces ratios en rendements qui s’additionnent dans le temps.

Le code convertit la série en tableau numérique à une dimension et refuse les valeurs nulles, négatives, infinies ou manquantes : le logarithme du ratio ne serait pas exploitable.

## Étape 2 : dispersion, puis annualisation

`vol_journaliere = sqrt(somme((r_t - moyenne(r))²) / (n - 1))`

`vol_annuelle = vol_journaliere × sqrt(252)`.

`ddof=1` demande la division par n−1 pour l’écart-type d’échantillon. Le calcul mesure la dispersion autour du rendement moyen ; il ne mesure pas simplement la taille moyenne des variations. Pour les trois prix précédents, la volatilité annualisée est environ 22,34 %. Ce minuscule exemple explique le calcul mais ne constitue pas une estimation robuste.

Le facteur 252 suppose des observations journalières et 252 séances par an. Pour des données mensuelles, il faudrait choisir un facteur adapté, par exemple 12. Le facteur doit être positif. Il faut au moins trois prix pour obtenir deux rendements et un écart-type d’échantillon ; le module marché impose en plus un minimum de vingt cours.

## Unités à suivre

Cette fonction renvoie un décimal : 0,25 signifie 25 %. `market_data_engine.get_vol_historique` multiplie par 100 pour le formulaire. `main.py` redivise par 100 avant le moteur de simulation. Ne pas appliquer deux fois la même conversion.

Des prix constants produisent une volatilité nulle ; une hausse parfaitement régulière en rendement logarithmique produit également une dispersion nulle ou quasi nulle. Une hausse moyenne et une volatilité sont deux informations différentes.


## Code actuel expliqué fonction par fonction

Les extraits suivants reproduisent les fonctions du fichier source au moment de la rédaction. Les fonctions commençant par `_` sont des aides internes.

### `log_returns`

```python
def log_returns(prices):
    """
    Calcule les log-rendements d'une série de prix.

    Formule :
        r_t = ln(S_t / S_{t-1})

    Les log-rendements servent ensuite de base au calcul de la
    volatilité historique, EWMA, GARCH, etc.

    Paramètre :
        prices : série de prix du sous-jacent

    Renvoie :
        tableau des log-rendements
    """
    # Conversion des prix en tableau NumPy
    prices = np.asarray(prices, dtype=float)

    # Vérification du nombre de prix
    if prices.ndim != 1 or len(prices) < 2:
        raise ValueError("Il faut au moins deux prix.")

    # Vérification des valeurs
    if not np.all(np.isfinite(prices)) or np.any(prices <= 0):
        raise ValueError("Les prix doivent être positifs et finis.")

    # Calcul des rendements logarithmiques
    returns = np.log(prices[1:] / prices[:-1])

    return returns
```

**Traduction en phrase :** Je compare chaque prix au précédent et je prends le logarithme du ratio ; avec n prix, je renvoie n−1 rendements.

### `historical_volatility`

```python
def historical_volatility(prices, annualization=252):
    """
    Calcule la volatilité historique close-to-close.

    Étapes :
    1. calculer les log-rendements ;
    2. calculer leur écart-type ;
    3. annualiser la volatilité.

    Pour des données journalières, on utilise généralement :
        sigma_annuelle = sigma_journalière * sqrt(252)

    Paramètres :
        prices          : série de prix de clôture
        annualization   : nombre de périodes dans une année

    Renvoie :
        volatilité historique annualisée en décimal
        Exemple : 0.25 = 25 %
    """
    # 1. Calcul des rendements logarithmiques
    returns = log_returns(prices)

    # 2. Vérification du nombre de rendements
    if len(returns) < 2:
        raise ValueError(
        "Il faut au moins trois prix pour calculer la volatilité."
    )

    # 3. Vérification du facteur d'annualisation
    if annualization <= 0:
        raise ValueError(
        "Le facteur d'annualisation doit être positif."
    )

    # 4. Calcul de l'écart-type des rendements
    daily_volatility = np.std(returns, ddof=1)

    # 5. Annualisation
    annual_volatility = daily_volatility * np.sqrt(annualization)

    # 6. Retour en décimal
    return float(annual_volatility)
```

**Traduction en phrase :** Je calcule l’écart-type des rendements, avec la correction n−1, puis je le multiplie par la racine du nombre de séances annuelles.
