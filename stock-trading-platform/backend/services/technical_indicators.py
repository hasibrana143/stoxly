import numpy as np
from typing import List, Dict, Optional


def calculate_sma(prices: List[float], period: int = 20) -> List[Optional[float]]:
    if not prices or len(prices) < period:
        return [None] * len(prices) if prices else []

    arr = np.array(prices, dtype=np.float64)
    result = [None] * (period - 1)
    cumsum = np.cumsum(arr)
    sma = (cumsum[period - 1:] - np.concatenate([[0], cumsum[:-period]])) / period
    result.extend(sma.tolist())
    return result


def calculate_ema(prices: List[float], period: int = 20) -> List[Optional[float]]:
    if not prices or len(prices) < period:
        return [None] * len(prices) if prices else []

    arr = np.array(prices, dtype=np.float64)
    multiplier = 2.0 / (period + 1)
    result: List[Optional[float]] = [None] * (period - 1)
    ema_prev = np.mean(arr[:period])
    result.append(float(ema_prev))

    for price in arr[period:]:
        ema_prev = (price - ema_prev) * multiplier + ema_prev
        result.append(float(ema_prev))

    return result


def calculate_rsi(prices: List[float], period: int = 14) -> List[Optional[float]]:
    if not prices or len(prices) < period + 1:
        return [None] * len(prices) if prices else []

    arr = np.array(prices, dtype=np.float64)
    deltas = np.diff(arr)
    result: List[Optional[float]] = [None] * period

    gain = np.where(deltas > 0, deltas, 0.0)
    loss = np.where(deltas < 0, -deltas, 0.0)

    avg_gain = np.mean(gain[:period])
    avg_loss = np.mean(loss[:period])

    if avg_loss == 0:
        result.append(100.0)
    else:
        rs = avg_gain / avg_loss
        result.append(float(100.0 - (100.0 / (1.0 + rs))))

    for i in range(period, len(deltas)):
        avg_gain = ((avg_gain * (period - 1)) + gain[i]) / period
        avg_loss = ((avg_loss * (period - 1)) + loss[i]) / period

        if avg_loss == 0:
            result.append(100.0)
        else:
            rs = avg_gain / avg_loss
            result.append(float(100.0 - (100.0 / (1.0 + rs))))

    return result


def calculate_macd(prices: List[float]) -> Dict[str, List[Optional[float]]]:
    result: Dict[str, List[Optional[float]]] = {
        "macd_line": [],
        "signal_line": [],
        "histogram": [],
    }

    if not prices or len(prices) < 26:
        n = len(prices)
        result["macd_line"] = [None] * n
        result["signal_line"] = [None] * n
        result["histogram"] = [None] * n
        return result

    ema12 = calculate_ema(prices, 12)
    ema26 = calculate_ema(prices, 26)

    macd_line: List[Optional[float]] = [None] * len(prices)
    for i in range(len(prices)):
        if ema12[i] is not None and ema26[i] is not None:
            macd_line[i] = ema12[i] - ema26[i]

    macd_vals = [v for v in macd_line if v is not None]
    fill = len(prices) - len(macd_vals)

    if len(macd_vals) < 9:
        signal_line = [None] * len(prices)
        histogram = [None] * len(prices)
        return {"macd_line": macd_line, "signal_line": signal_line, "histogram": histogram}

    signal_raw = calculate_ema(macd_vals, 9)
    signal_line = [None] * fill + signal_raw

    histogram: List[Optional[float]] = [None] * len(prices)
    for i in range(len(prices)):
        if macd_line[i] is not None and signal_line[i] is not None:
            histogram[i] = macd_line[i] - signal_line[i]

    return {"macd_line": macd_line, "signal_line": signal_line, "histogram": histogram}


def calculate_bollinger_bands(
    prices: List[float], period: int = 20, std_dev: float = 2.0
) -> Dict[str, List[Optional[float]]]:
    result: Dict[str, List[Optional[float]]] = {
        "upper": [],
        "middle": [],
        "lower": [],
    }

    if not prices or len(prices) < period:
        n = len(prices)
        result["upper"] = [None] * n
        result["middle"] = [None] * n
        result["lower"] = [None] * n
        return result

    arr = np.array(prices, dtype=np.float64)
    middle = calculate_sma(prices, period)

    upper: List[Optional[float]] = [None] * (period - 1)
    lower: List[Optional[float]] = [None] * (period - 1)

    for i in range(period - 1, len(prices)):
        window = arr[i - period + 1 : i + 1]
        std = np.std(window, ddof=0)
        mid = middle[i]
        if mid is not None:
            upper.append(float(mid + std_dev * std))
            lower.append(float(mid - std_dev * std))
        else:
            upper.append(None)
            lower.append(None)

    return {"upper": upper, "middle": middle, "lower": lower}


def calculate_stochastic(
    prices_high: List[float],
    prices_low: List[float],
    prices_close: List[float],
    period: int = 14,
) -> Dict[str, List[Optional[float]]]:
    result: Dict[str, List[Optional[float]]] = {"k": [], "d": []}

    if not prices_close or len(prices_close) < period:
        n = len(prices_close)
        result["k"] = [None] * n
        result["d"] = [None] * n
        return result

    n = len(prices_close)
    k_vals: List[Optional[float]] = [None] * (period - 1)

    for i in range(period - 1, n):
        high_i = max(prices_high[i - period + 1 : i + 1])
        low_i = min(prices_low[i - period + 1 : i + 1])
        close_i = prices_close[i]

        if high_i == low_i:
            k_vals.append(50.0)
        else:
            k = ((close_i - low_i) / (high_i - low_i)) * 100.0
            k_vals.append(float(k))

    k_slice = [v for v in k_vals if v is not None]

    if len(k_slice) < 3:
        d_vals: List[Optional[float]] = [None] * n
    else:
        d_vals = [None] * (period - 1 + 2)
        for i in range(2, len(k_slice)):
            d = np.mean(k_slice[i - 2 : i + 1])
            d_vals.append(float(d))

    return {"k": k_vals, "d": d_vals}


def calculate_atr(
    high: List[float], low: List[float], close: List[float], period: int = 14
) -> List[Optional[float]]:
    if not high or len(high) < period:
        return [None] * len(high) if high else []

    h = np.array(high, dtype=np.float64)
    l = np.array(low, dtype=np.float64)
    c = np.array(close, dtype=np.float64)

    tr = np.zeros(len(h))
    tr[0] = h[0] - l[0]
    for i in range(1, len(h)):
        tr[i] = max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1]))

    result: List[Optional[float]] = [None] * (period - 1)

    atr_prev = np.mean(tr[:period])
    result.append(float(atr_prev))

    for i in range(period, len(tr)):
        atr_prev = ((atr_prev * (period - 1)) + tr[i]) / period
        result.append(float(atr_prev))

    return result


def calculate_obv(close: List[float], volume: List[float]) -> List[float]:
    if not close or len(close) != len(volume):
        return []

    c = np.array(close, dtype=np.float64)
    v = np.array(volume, dtype=np.float64)
    obv = np.zeros_like(c)

    obv[0] = v[0]
    for i in range(1, len(c)):
        if c[i] > c[i - 1]:
            obv[i] = obv[i - 1] + v[i]
        elif c[i] < c[i - 1]:
            obv[i] = obv[i - 1] - v[i]
        else:
            obv[i] = obv[i - 1]

    return obv.tolist()


def calculate_all_indicators(prices: List[float]) -> Dict:
    sma = calculate_sma(prices)
    ema = calculate_ema(prices)
    rsi = calculate_rsi(prices)
    macd = calculate_macd(prices)
    bb = calculate_bollinger_bands(prices)

    current = {}
    if prices:
        current["price"] = prices[-1]
        current["sma"] = sma[-1] if sma else None
        current["ema"] = ema[-1] if ema else None
        current["rsi"] = rsi[-1] if rsi else None
        current["macd"] = macd["macd_line"][-1] if macd["macd_line"] else None
        current["macd_signal"] = macd["signal_line"][-1] if macd["signal_line"] else None
        current["macd_histogram"] = macd["histogram"][-1] if macd["histogram"] else None
        current["bb_upper"] = bb["upper"][-1] if bb["upper"] else None
        current["bb_middle"] = bb["middle"][-1] if bb["middle"] else None
        current["bb_lower"] = bb["lower"][-1] if bb["lower"] else None

    return {
        "sma": sma,
        "ema": ema,
        "rsi": rsi,
        "macd": macd,
        "bollinger_bands": bb,
        "current": current,
    }
