import numpy as np
import yfinance as yf


def get_fx_rate(from_currency: str, to_currency: str = 'EUR') -> float:
    """
    Get live FX rate from Yahoo. Returns 1.0 if from/to are the same.
    """
    if from_currency == to_currency:
        return 1.0
    pair = f"{from_currency}{to_currency}=X"
    try:
        data = yf.Ticker(pair).history(period="1d")
        return data["Close"].iloc[-1]
    except Exception as e:
        print(f"Error fetching FX rate: {e}")
        return np.nan


def get_price_eur(row, fx_cache) -> float:
    """
    Fetch Yahoo price in native currency and convert to EUR.
    """
    try:
        price_native = (
            yf.Ticker(row['Ticker'])
            .history(period="1d")['Close']
            .iloc[-1]
        )
        fx_rate = fx_cache.get(row['Currency Yahoo'], 1.0)  # default 1.0
        return price_native * fx_rate
    except Exception as e:
        print(f"Error fetching {row['Ticker']}: {e}")
        return np.nan