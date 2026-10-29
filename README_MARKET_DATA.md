# market_data_engine.py — charger le marché

[Retour au guide général](README.md)

Ce fichier utilise `yfinance` pour rechercher un sous-jacent et récupérer les données utiles au formulaire. Il délègue le calcul de la volatilité à `volatility_engine.py`.

## Données et unités

| Fonction | Résultat |
|---|---|
| `search_tickers` | Liste de symboles, noms et places de cotation, huit résultats au maximum par défaut |
| `get_spot` | Dernier prix disponible, dans la devise de cotation |
| `get_historical_prices` | Série de clôtures ajustées avec leurs dates |
| `get_vol_historique` | Volatilité annualisée en pourcentage : 25 signifie 25 % |
| `get_devise` | Code de devise fourni par Yahoo |
| `get_vix` | Niveau de l’indice `^VIX`, en points de volatilité |

Le téléchargement historique utilise `auto_adjust=True`, extrait `Close` et retire les valeurs manquantes avec `dropna()`. Les cours ajustés peuvent différer des cours bruts, notamment lors d’opérations sur titres. Le calcul par défaut porte sur un an, pas sur une fenêtre glissante de 20 jours.

Il faut au moins deux cours pour renvoyer l’historique ; la fonction de volatilité de ce module exige au moins vingt cours avant d’appeler le calcul. Ce seuil de vingt est un garde-fou, pas la taille d’une fenêtre glissante.

## Parcours concret

Une recherche « apple » renvoie éventuellement AAPL. Après sélection, `/api/market/AAPL` demande le spot, la devise, l’historique et le VIX. Si le calcul de volatilité renvoie 0,25, ce module le transforme en 25 ; lors du pricing, `main.py` divise cette valeur par 100 pour retrouver 0,25.

Le VIX est un indice lié au S&P 500, pas la volatilité implicite propre à AAPL. Sa sélection constitue une hypothèse de volatilité pour le modèle. Les taux et dividendes restent saisis manuellement. Le code ne fait aucune conversion de devises.

## Disponibilité

Les appels exigent Internet et dépendent de Yahoo Finance. La recherche masque les exceptions et renvoie `[]` : aucun résultat peut donc signifier une panne. Les autres fonctions laissent remonter les erreurs ; la route marché traite séparément l’absence du VIX et celle de l’historique. Le spot peut rester utilisable si la volatilité historique manque.

Ces fonctions ne construisent pas un instantané synchronisé ni un cache commun : des appels successifs peuvent fournir des cours légèrement différents. La saisie manuelle permet de calculer sans ces appels externes. Aucun exemple chiffré de ce guide ne prétend être une cotation actuelle.


## Code actuel expliqué fonction par fonction

Les extraits suivants reproduisent les fonctions du fichier source au moment de la rédaction. Les fonctions commençant par `_` sont des aides internes.

### `search_tickers`

```python
def search_tickers(query, max_results=8):
    """Cherche des tickers sur Yahoo Finance (barre de recherche du site).

    Renvoie : une liste de dicts {symbol, name, exchange}, ou une liste vide
    si Yahoo ne répond pas.
    """
    try:
        resultats = yf.Search(query, max_results=max_results).quotes
    except Exception:
        return []  # si yahoo répond pas je renvoie juste rien

    return [
        {
            "symbol": r.get("symbol"),
            "name": r.get("shortname") or r.get("longname") or r.get("symbol"),
            "exchange": r.get("exchange"),
        }
        for r in resultats
        if r.get("symbol")
    ]
```

**Traduction en phrase :** Je demande des correspondances à Yahoo, je ne garde que les résultats avec un symbole et je choisis un nom disponible ; si la recherche échoue, je renvoie une liste vide.

### `get_spot`

```python
def get_spot(ticker):
    return float(yf.Ticker(ticker).fast_info["last_price"])
```

**Traduction en phrase :** Je lis le dernier prix disponible et le transforme en nombre Python.

### `get_historical_prices`

```python
def get_historical_prices(ticker, periode="1y"):
    """
    Récupère les cours historiques d'un sous-jacent
    depuis Yahoo Finance.

    Paramètres
    ----------
    ticker : str
        Symbole Yahoo Finance (AAPL, MSFT, etc.).

    periode : str
        Période historique : 1mo, 3mo, 6mo, 1y, 2y, 5y.

    Retour
    ------
    pandas.Series
        Série chronologique des cours de clôture ajustés.
    """

    # 1. Connexion à Yahoo Finance
    asset = yf.Ticker(ticker)

    # 2. Récupération des données historiques
    data = asset.history(
        period=periode,
        auto_adjust=True
    )

    # 3. Vérification des données
    if data.empty:
        raise ValueError(
            f"Aucune donnée historique disponible pour {ticker}"
        )

    # 4. Extraction des cours de clôture
    prices = data["Close"].dropna()

    # 5. Vérification du nombre de cours
    if len(prices) < 2:
        raise ValueError(
            "Historique insuffisant pour calculer les rendements."
        )

    return prices
```

**Traduction en phrase :** Je télécharge les cours ajustés, conserve les clôtures non manquantes et refuse un historique vide ou trop court.

### `get_vol_historique`

```python
def get_vol_historique(ticker, periode="1y"):
    """
    Récupère les cours historiques et calcule
    leur volatilité annualisée.

    Le calcul est effectué dans volatility_engine.py.

    Retour :
        volatilité annualisée en pourcentage.
    """

    # 1. Récupération des cours historiques
    cours = get_historical_prices(ticker, periode)

    # 2. Vérification du nombre de cours
    if len(cours) < 20:
        raise ValueError(
            "Pas assez d'historique pour calculer une volatilité."
        )

    # 3. Calcul de la volatilité historique
    vol = historical_volatility(cours)

    # 4. Conversion en pourcentage
    return float(vol * 100)
```

**Traduction en phrase :** Je charge les cours, exige au moins vingt observations, puis convertis la volatilité calculée en pourcentage.

### `get_devise`

```python
def get_devise(ticker):
    return yf.Ticker(ticker).fast_info["currency"]
```

**Traduction en phrase :** Je renvoie la devise annoncée pour ce ticker, sans convertir les montants.

### `get_vix`

```python
def get_vix():
    return float(yf.Ticker("^VIX").fast_info["last_price"])
```

**Traduction en phrase :** Je lis le dernier niveau disponible du symbole Yahoo ^VIX.
