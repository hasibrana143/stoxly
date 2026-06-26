import random
import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from comprehensive_indian_stocks import mock_provider
from services.technical_indicators import (
    calculate_all_indicators,
    calculate_sma,
    calculate_ema,
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
    calculate_stochastic,
    calculate_atr,
    calculate_obv,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/indicators", tags=["Technical Indicators"])


def _generate_sample_prices(current_price: float, days: int = 100) -> List[float]:
    prices = [current_price]
    for _ in range(days - 1):
        change = prices[-1] * random.uniform(-0.03, 0.03)
        prices.append(round(prices[-1] + change, 2))
    return prices


def _generate_ohlcv(current_price: float, days: int = 100):
    closes = _generate_sample_prices(current_price, days)
    highs = []
    lows = []
    for c in closes:
        spread = c * random.uniform(0.005, 0.02)
        highs.append(round(c + spread, 2))
        lows.append(round(c - spread, 2))
    volumes = [random.randint(100000, 50000000) for _ in range(days)]
    return closes, highs, lows, volumes


@router.get("/{symbol}")
async def get_technical_indicators(
    symbol: str,
    period: int = Query(20, description="Lookback period for moving averages"),
    rsi_period: int = Query(14, description="RSI period"),
):
    """Get all technical indicators for a stock"""
    try:
        stock = mock_provider.get_current_price(symbol)
        current_price = stock["current_price"]
        closes, highs, lows, volumes = _generate_ohlcv(current_price)

        sma = calculate_sma(closes, period)
        ema = calculate_ema(closes, period)
        rsi_vals = calculate_rsi(closes, rsi_period)
        macd = calculate_macd(closes)
        bb = calculate_bollinger_bands(closes, period)
        stoch = calculate_stochastic(highs, lows, closes, 14)
        atr_vals = calculate_atr(highs, lows, closes, 14)
        obv_vals = calculate_obv(closes, volumes)

        sma_current = sma[-1] if sma and len(sma) > 0 else None
        ema_current = ema[-1] if ema and len(ema) > 0 else None
        rsi_current = rsi_vals[-1] if rsi_vals and len(rsi_vals) > 0 else None
        stoch_k = stoch["k"][-1] if stoch["k"] and len(stoch["k"]) > 0 else None
        stoch_d = stoch["d"][-1] if stoch["d"] and len(stoch["d"]) > 0 else None
        atr_current = atr_vals[-1] if atr_vals and len(atr_vals) > 0 else None

        return {
            "symbol": symbol,
            "name": stock["name"],
            "current_price": current_price,
            "indicators": {
                "sma": {"value": sma_current, "series": sma},
                "ema": {"value": ema_current, "series": ema},
                "rsi": {"value": rsi_current, "series": rsi_vals},
                "macd": {
                    "macd_line": macd["macd_line"][-1] if macd["macd_line"] else None,
                    "signal_line": macd["signal_line"][-1] if macd["signal_line"] else None,
                    "histogram": macd["histogram"][-1] if macd["histogram"] else None,
                    "series": macd,
                },
                "bollinger_bands": {
                    "upper": bb["upper"][-1] if bb["upper"] else None,
                    "middle": bb["middle"][-1] if bb["middle"] else None,
                    "lower": bb["lower"][-1] if bb["lower"] else None,
                    "series": bb,
                },
                "stochastic": {
                    "k": stoch_k,
                    "d": stoch_d,
                    "series": stoch,
                },
                "atr": {"value": atr_current, "series": atr_vals},
                "obv": {"value": obv_vals[-1] if obv_vals else None, "series": obv_vals},
            },
        }
    except ValueError:
        raise HTTPException(status_code=404, detail="Stock not found")
    except Exception as e:
        logger.error(f"Technical indicators error for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to compute technical indicators")


@router.get("/{symbol}/sma")
async def get_sma(symbol: str, period: int = 20):
    """Simple Moving Average"""
    try:
        stock = mock_provider.get_current_price(symbol)
        closes, _, _, _ = _generate_ohlcv(stock["current_price"])
        sma = calculate_sma(closes, period)
        return {"symbol": symbol, "period": period, "value": sma[-1] if sma else None, "series": sma}
    except ValueError:
        raise HTTPException(status_code=404, detail="Stock not found")
    except Exception as e:
        logger.error(f"SMA error for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to compute SMA")


@router.get("/{symbol}/ema")
async def get_ema(symbol: str, period: int = 20):
    """Exponential Moving Average"""
    try:
        stock = mock_provider.get_current_price(symbol)
        closes, _, _, _ = _generate_ohlcv(stock["current_price"])
        ema = calculate_ema(closes, period)
        return {"symbol": symbol, "period": period, "value": ema[-1] if ema else None, "series": ema}
    except ValueError:
        raise HTTPException(status_code=404, detail="Stock not found")
    except Exception as e:
        logger.error(f"EMA error for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to compute EMA")


@router.get("/{symbol}/rsi")
async def get_rsi(symbol: str, period: int = 14):
    """Relative Strength Index"""
    try:
        stock = mock_provider.get_current_price(symbol)
        closes, _, _, _ = _generate_ohlcv(stock["current_price"])
        rsi_vals = calculate_rsi(closes, period)
        rsi_current = rsi_vals[-1] if rsi_vals else None
        signal = None
        if rsi_current is not None:
            signal = "overbought" if rsi_current >= 70 else "oversold" if rsi_current <= 30 else "neutral"
        return {"symbol": symbol, "period": period, "value": rsi_current, "signal": signal, "series": rsi_vals}
    except ValueError:
        raise HTTPException(status_code=404, detail="Stock not found")
    except Exception as e:
        logger.error(f"RSI error for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to compute RSI")


@router.get("/{symbol}/macd")
async def get_macd(symbol: str):
    """MACD"""
    try:
        stock = mock_provider.get_current_price(symbol)
        closes, _, _, _ = _generate_ohlcv(stock["current_price"])
        macd = calculate_macd(closes)
        return {
            "symbol": symbol,
            "macd_line": macd["macd_line"][-1] if macd["macd_line"] else None,
            "signal_line": macd["signal_line"][-1] if macd["signal_line"] else None,
            "histogram": macd["histogram"][-1] if macd["histogram"] else None,
            "series": macd,
        }
    except ValueError:
        raise HTTPException(status_code=404, detail="Stock not found")
    except Exception as e:
        logger.error(f"MACD error for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to compute MACD")


@router.get("/{symbol}/bollinger")
async def get_bollinger(symbol: str, period: int = 20, std_dev: float = 2.0):
    """Bollinger Bands"""
    try:
        stock = mock_provider.get_current_price(symbol)
        closes, _, _, _ = _generate_ohlcv(stock["current_price"])
        bb = calculate_bollinger_bands(closes, period, std_dev)
        return {
            "symbol": symbol,
            "period": period,
            "std_dev": std_dev,
            "upper": bb["upper"][-1] if bb["upper"] else None,
            "middle": bb["middle"][-1] if bb["middle"] else None,
            "lower": bb["lower"][-1] if bb["lower"] else None,
            "series": bb,
        }
    except ValueError:
        raise HTTPException(status_code=404, detail="Stock not found")
    except Exception as e:
        logger.error(f"Bollinger Bands error for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to compute Bollinger Bands")


@router.get("/{symbol}/stochastic")
async def get_stochastic(symbol: str, period: int = 14):
    """Stochastic Oscillator"""
    try:
        stock = mock_provider.get_current_price(symbol)
        closes, highs, lows, _ = _generate_ohlcv(stock["current_price"])
        stoch = calculate_stochastic(highs, lows, closes, period)
        return {"symbol": symbol, "period": period, "k": stoch["k"][-1] if stoch["k"] else None, "d": stoch["d"][-1] if stoch["d"] else None, "series": stoch}
    except ValueError:
        raise HTTPException(status_code=404, detail="Stock not found")
    except Exception as e:
        logger.error(f"Stochastic error for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to compute Stochastic Oscillator")


@router.get("/{symbol}/atr")
async def get_atr(symbol: str, period: int = 14):
    """Average True Range"""
    try:
        stock = mock_provider.get_current_price(symbol)
        closes, highs, lows, _ = _generate_ohlcv(stock["current_price"])
        atr_vals = calculate_atr(highs, lows, closes, period)
        return {"symbol": symbol, "period": period, "value": atr_vals[-1] if atr_vals else None, "series": atr_vals}
    except ValueError:
        raise HTTPException(status_code=404, detail="Stock not found")
    except Exception as e:
        logger.error(f"ATR error for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to compute ATR")


@router.get("/{symbol}/obv")
async def get_obv(symbol: str):
    """On-Balance Volume"""
    try:
        stock = mock_provider.get_current_price(symbol)
        closes, _, _, volumes = _generate_ohlcv(stock["current_price"])
        obv_vals = calculate_obv(closes, volumes)
        return {"symbol": symbol, "value": obv_vals[-1] if obv_vals else None, "series": obv_vals}
    except ValueError:
        raise HTTPException(status_code=404, detail="Stock not found")
    except Exception as e:
        logger.error(f"OBV error for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to compute OBV")
