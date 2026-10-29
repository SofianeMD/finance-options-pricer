"""Volatilité historique nécessaire aux paramètres de marché."""
import numpy as np

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
