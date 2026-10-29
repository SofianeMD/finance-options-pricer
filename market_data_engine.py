"""Recherche de ticker et données de marché pour les produits structurés."""
import yfinance as yf
from volatility_engine import historical_volatility

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


def get_spot(ticker):
    return float(yf.Ticker(ticker).fast_info["last_price"])


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


def get_devise(ticker):
    return yf.Ticker(ticker).fast_info["currency"]


def get_vix():
    return float(yf.Ticker("^VIX").fast_info["last_price"])
