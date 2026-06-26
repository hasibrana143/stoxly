import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
import logging
from scipy.optimize import minimize, Bounds, LinearConstraint

logger = logging.getLogger(__name__)


def calculate_returns(prices: List[Dict[str, float]]) -> pd.DataFrame:
    if not prices or len(prices) < 2:
        logger.warning("Insufficient price data to calculate returns")
        return pd.DataFrame()

    df = pd.DataFrame(prices)
    if df.empty:
        return df

    pct_returns = df.pct_change().dropna(inplace=False)
    if pct_returns.empty:
        logger.warning("All price changes are zero or NaN; no valid returns")
    return pct_returns


def _mean_cov_from_prices(
    symbols: List[str], historical_prices: Dict[str, List[float]]
) -> Tuple[Optional[np.ndarray], Optional[np.ndarray], Optional[pd.DataFrame]]:
    if len(symbols) < 2:
        logger.error("Need at least 2 symbols for portfolio optimization")
        return None, None, None

    prices_dict = {}
    for sym in symbols:
        vals = historical_prices.get(sym)
        if vals is None or len(vals) < 2:
            logger.error(f"Insufficient historical data for {sym}")
            return None, None, None
        prices_dict[sym] = vals

    df = pd.DataFrame(prices_dict)
    returns_df = df.pct_change().dropna()
    if returns_df.empty:
        logger.error("No valid return observations after pct_change")
        return None, None, None
    if len(returns_df) < 2:
        logger.error("Need at least 2 return observations for covariance estimation")
        return None, None, None

    mean_returns = returns_df.mean().values
    cov_matrix = returns_df.cov().values
    return mean_returns, cov_matrix, returns_df


def portfolio_stats(
    weights: np.ndarray,
    mean_returns: np.ndarray,
    cov_matrix: np.ndarray,
    risk_free_rate: float,
) -> Tuple[float, float, float]:
    port_return = np.dot(weights, mean_returns) * 252
    port_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
    sharpe = (port_return - risk_free_rate) / port_volatility if port_volatility > 1e-12 else 0.0
    return float(port_return), float(port_volatility), float(sharpe)


def min_variance_portfolio(
    mean_returns: np.ndarray, cov_matrix: np.ndarray
) -> np.ndarray:
    n = len(mean_returns)
    bounds = Bounds(0, 1)
    constraints = LinearConstraint(np.ones(n), [1], [1])

    result = minimize(
        lambda w: np.sqrt(np.dot(w.T, np.dot(cov_matrix, w))),
        x0=np.array([1.0 / n] * n),
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"ftol": 1e-10, "maxiter": 5000},
    )
    if not result.success:
        logger.warning(f"Min-variance optimization did not converge: {result.message}")
    return result.x


def max_sharpe_portfolio(
    mean_returns: np.ndarray, cov_matrix: np.ndarray, risk_free_rate: float
) -> np.ndarray:
    n = len(mean_returns)
    bounds = Bounds(0, 1)
    constraints = LinearConstraint(np.ones(n), [1], [1])

    def neg_sharpe(w: np.ndarray) -> float:
        r = np.dot(w, mean_returns) * 252
        vol = np.sqrt(np.dot(w.T, np.dot(cov_matrix, w))) * np.sqrt(252)
        if vol < 1e-12:
            return 0.0
        return -(r - risk_free_rate) / vol

    result = minimize(
        neg_sharpe,
        x0=np.array([1.0 / n] * n),
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"ftol": 1e-10, "maxiter": 5000},
    )
    if not result.success:
        logger.warning(f"Max-Sharpe optimization did not converge: {result.message}")
    return result.x


def _max_return_portfolio(
    mean_returns: np.ndarray, cov_matrix: np.ndarray
) -> np.ndarray:
    n = len(mean_returns)
    bounds = Bounds(0, 1)
    constraints = LinearConstraint(np.ones(n), [1], [1])

    result = minimize(
        lambda w: -np.dot(w, mean_returns),
        x0=np.array([1.0 / n] * n),
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"ftol": 1e-10, "maxiter": 5000},
    )
    if not result.success:
        logger.warning(f"Max-return optimization did not converge: {result.message}")
    return result.x


def calculate_efficient_frontier(
    mean_returns: np.ndarray, cov_matrix: np.ndarray, num_portfolios: int = 20
) -> List[Dict]:
    n = len(mean_returns)
    if n < 2:
        return []

    min_w = min_variance_portfolio(mean_returns, cov_matrix)
    max_w = _max_return_portfolio(mean_returns, cov_matrix)

    min_ret = float(np.dot(min_w, mean_returns) * 252)
    max_ret = float(np.dot(max_w, mean_returns) * 252)

    if max_ret - min_ret < 1e-12:
        target_returns = np.linspace(min_ret, min_ret + 0.01, num_portfolios)
    else:
        target_returns = np.linspace(min_ret, max_ret, num_portfolios)

    bounds = Bounds(0, 1)
    constraints_list = [LinearConstraint(np.ones(n), [1], [1])]

    frontier: List[Dict] = []
    for tr in target_returns:
        target_constraint = LinearConstraint(mean_returns * 252, [tr], [tr])
        result = minimize(
            lambda w: np.sqrt(np.dot(w.T, np.dot(cov_matrix, w))) * np.sqrt(252),
            x0=np.array([1.0 / n] * n),
            method="SLSQP",
            bounds=bounds,
            constraints=constraints_list + [target_constraint],
            options={"ftol": 1e-10, "maxiter": 5000},
        )
        if result.success:
            vol = float(result.fun)
            frontier.append(
                {
                    "return": round(tr, 6),
                    "volatility": round(vol, 6),
                    "weights": {f"asset_{i}": round(w, 6) for i, w in enumerate(result.x)},
                }
            )
        else:
            frontier.append(
                {
                    "return": round(tr, 6),
                    "volatility": None,
                    "weights": None,
                }
            )

    return frontier


def optimize_portfolio(
    symbols: List[str],
    historical_prices: Dict[str, List[float]],
    risk_free_rate: float = 0.065,
) -> Dict:
    mean_ret, cov_mat, returns_df = _mean_cov_from_prices(symbols, historical_prices)
    if mean_ret is None:
        return {
            "optimal_weights": {},
            "expected_return": 0.0,
            "expected_volatility": 0.0,
            "sharpe_ratio": 0.0,
            "efficient_frontier": [],
            "individual_metrics": {},
        }

    min_w = min_variance_portfolio(mean_ret, cov_mat)
    sharpe_w = max_sharpe_portfolio(mean_ret, cov_mat, risk_free_rate)

    exp_return, exp_vol, sharpe = portfolio_stats(sharpe_w, mean_ret, cov_mat, risk_free_rate)

    efficient_frontier = calculate_efficient_frontier(mean_ret, cov_mat, num_portfolios=20)

    individual_metrics = {}
    for i, sym in enumerate(symbols):
        w = np.zeros(len(symbols))
        w[i] = 1.0
        r, v, s = portfolio_stats(w, mean_ret, cov_mat, risk_free_rate)
        individual_metrics[sym] = {
            "return": round(r, 6),
            "volatility": round(v, 6),
            "sharpe_ratio": round(s, 6),
        }

    optimal_weights = {sym: round(float(sharpe_w[i]), 6) for i, sym in enumerate(symbols)}

    return {
        "optimal_weights": optimal_weights,
        "expected_return": round(exp_return, 6),
        "expected_volatility": round(exp_vol, 6),
        "sharpe_ratio": round(sharpe, 6),
        "efficient_frontier": efficient_frontier,
        "individual_metrics": individual_metrics,
    }


def calculate_var(returns: np.ndarray, confidence_level: float = 0.95) -> float:
    if len(returns) == 0:
        return 0.0
    return float(np.percentile(returns, (1 - confidence_level) * 100))


def calculate_cvar(returns: np.ndarray, confidence_level: float = 0.95) -> float:
    var = calculate_var(returns, confidence_level)
    tail = returns[returns <= var]
    if len(tail) == 0:
        return var
    return float(tail.mean())


def rebalance_suggestion(
    current_weights: Dict[str, float],
    target_weights: Dict[str, float],
    threshold: float = 0.05,
) -> List[Dict]:
    all_symbols = set(current_weights.keys()) | set(target_weights.keys())
    suggestions = []
    for sym in all_symbols:
        cw = current_weights.get(sym, 0.0)
        tw = target_weights.get(sym, 0.0)
        diff = tw - cw
        if abs(diff) < threshold:
            action = "hold"
        elif diff > 0:
            action = "buy"
        else:
            action = "sell"
        suggestions.append(
            {
                "symbol": sym,
                "current_weight": round(cw, 6),
                "target_weight": round(tw, 6),
                "difference": round(diff, 6),
                "action": action,
            }
        )
    return suggestions


def black_litterman(
    market_caps: Dict[str, float],
    views: List[Dict],
    confidence: float = 0.5,
) -> Dict:
    if not market_caps or len(market_caps) < 2:
        return {"posterior_returns": {}, "posterior_weights": {}}

    symbols = list(market_caps.keys())
    caps = np.array([market_caps[s] for s in symbols])
    market_weights = caps / caps.sum()

    tau = 0.05
    delta = 2.5

    if not views:
        return {
            "posterior_returns": {s: round(float(r), 6) for s, r in zip(symbols, market_weights)},
            "posterior_weights": {s: round(float(w), 6) for s, w in zip(symbols, market_weights)},
        }

    n = len(symbols)
    sym_to_idx = {s: i for i, s in enumerate(symbols)}

    P_rows = []
    Q_vals = []
    omega_diag = []

    for view in views:
        if "symbol" in view and "expected_return" in view:
            idx = sym_to_idx.get(view["symbol"])
            if idx is None:
                continue
            row = np.zeros(n)
            row[idx] = 1.0
            P_rows.append(row)
            Q_vals.append(view["expected_return"])
            omega_diag.append(1.0 - confidence)
        elif "symbol" in view and "will_outperform" in view:
            idx1 = sym_to_idx.get(view["symbol"])
            idx2 = sym_to_idx.get(view["will_outperform"])
            if idx1 is None or idx2 is None:
                continue
            row = np.zeros(n)
            row[idx1] = 1.0
            row[idx2] = -1.0
            P_rows.append(row)
            Q_vals.append(0.05)
            omega_diag.append(1.0 - confidence)

    if not P_rows:
        return {
            "posterior_returns": {s: round(float(r), 6) for s, r in zip(symbols, market_weights)},
            "posterior_weights": {s: round(float(w), 6) for s, w in zip(symbols, market_weights)},
        }

    P = np.array(P_rows)
    Q = np.array(Q_vals)
    Omega = np.diag(omega_diag)

    Sigma = np.eye(n) * 0.1
    Pi = delta * Sigma @ market_weights

    A = np.linalg.inv(tau * Sigma)
    B = P.T @ np.linalg.inv(Omega) @ P
    C = np.linalg.inv(tau * Sigma) @ Pi + P.T @ np.linalg.inv(Omega) @ Q

    posterior_cov_inv = A + B
    posterior_returns = np.linalg.solve(posterior_cov_inv, C)

    posterior_weights = market_weights.copy()

    return {
        "posterior_returns": {
            s: round(float(posterior_returns[i]), 6) for i, s in enumerate(symbols)
        },
        "posterior_weights": {
            s: round(float(posterior_weights[i]), 6) for i, s in enumerate(symbols)
        },
    }
