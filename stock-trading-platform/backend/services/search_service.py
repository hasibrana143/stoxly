from typing import List, Dict, Optional


def _get_scorer():
    try:
        from rapidfuzz import fuzz, process
        return fuzz, process, True
    except ImportError:
        import difflib

        class _FuzzFallback:
            @staticmethod
            def ratio(s1, s2):
                return difflib.SequenceMatcher(None, s1.lower(), s2.lower()).ratio() * 100

            @staticmethod
            def partial_ratio(s1, s2):
                s1l, s2l = s1.lower(), s2.lower()
                shorter, longer = (s1l, s2l) if len(s1l) <= len(s2l) else (s2l, s1l)
                best = 0
                for i in range(len(longer) - len(shorter) + 1):
                    score = difflib.SequenceMatcher(None, shorter, longer[i:i + len(shorter)]).ratio() * 100
                    if score > best:
                        best = score
                return best

            @staticmethod
            def token_sort_ratio(s1, s2):
                def sort_words(s):
                    return " ".join(sorted(s.lower().split()))
                return difflib.SequenceMatcher(None, sort_words(s1), sort_words(s2)).ratio() * 100

        class _ProcessFallback:
            @staticmethod
            def extract(query, choices, limit, scorer=None):
                scored = []
                for c in choices:
                    if scorer:
                        score = scorer(query, c)
                    else:
                        score = _FuzzFallback.ratio(query, c)
                    scored.append((c, score))
                scored.sort(key=lambda x: x[1], reverse=True)
                return scored[:limit]

            @staticmethod
            def extractOne(query, choices, scorer=None):
                scored = _ProcessFallback.extract(query, choices, 1, scorer)
                return scored[0] if scored else (None, 0)

        return _FuzzFallback(), _ProcessFallback(), False


fuzz, process, _has_rapidfuzz = _get_scorer()


def _text_fields(stock: Dict) -> str:
    parts = [
        str(stock.get("symbol", "")),
        str(stock.get("name", "")),
        str(stock.get("sector", "")),
    ]
    return " ".join(p for p in parts if p)


def smart_search(query: str, stocks: List[Dict], limit: int = 10) -> List[Dict]:
    """
    Fuzzy search across symbol, name, sector.
    stocks: [{symbol, name, sector, ...}]
    Returns sorted results with score.
    """
    if not query or not stocks:
        return []

    query = query.strip()
    choices = {s.get("symbol", ""): s for s in stocks if s.get("symbol")}
    seen = set()

    # Priority 1: prefix match on symbol
    for sym, stock in choices.items():
        if sym.lower().startswith(query.lower()):
            if sym not in seen:
                seen.add(sym)
                stock["_score"] = 100
                stock["_match_type"] = "prefix_symbol"

    # Priority 2: fuzzy on symbol + name + sector combined text
    remaining = [s for s in stocks if s.get("symbol") not in seen]
    if remaining:
        text_index = {_text_fields(s): s for s in remaining}
        texts = list(text_index.keys())
        results = process.extract(query, texts, limit=limit * 3, scorer=fuzz.token_sort_ratio)
        for text, score, _ in results:
            stock = text_index[text]
            sym = stock.get("symbol", "")
            if sym not in seen and score >= 30:
                seen.add(sym)
                stock["_score"] = round(score, 1)
                stock["_match_type"] = "fuzzy"

    out = [s for s in stocks if s.get("symbol") in seen]
    out.sort(key=lambda x: x.get("_score", 0), reverse=True)
    return out[:limit]


def autocomplete(query: str, stocks: List[Dict], limit: int = 5) -> List[Dict]:
    """
    Fast prefix + fuzzy match for autocomplete dropdowns.
    Returns: [{symbol, name, sector, type: 'stock'|'sector'}]
    """
    if not query or not stocks:
        return []

    query = query.strip().lower()
    results = []

    for s in stocks:
        symbol = str(s.get("symbol", "")).lower()
        name = str(s.get("name", "")).lower()
        sector = str(s.get("sector", "")).lower()

        if symbol.startswith(query) or name.startswith(query):
            results.append({
                "symbol": s.get("symbol"),
                "name": s.get("name"),
                "sector": s.get("sector"),
                "type": "stock",
                "_score": 90,
            })

    if len(results) < limit:
        existing_symbols = {r["symbol"] for r in results}
        for s in stocks:
            if s.get("symbol") in existing_symbols:
                continue
            symbol = str(s.get("symbol", "")).lower()
            name = str(s.get("name", "")).lower()
            combined = symbol + " " + name
            score = fuzz.partial_ratio(query, combined)
            if score >= 60:
                results.append({
                    "symbol": s.get("symbol"),
                    "name": s.get("name"),
                    "sector": s.get("sector"),
                    "type": "stock",
                    "_score": round(score, 1),
                })

    # Add sector suggestions
    sectors_seen = set()
    for s in stocks:
        sector = str(s.get("sector", "")).lower()
        if sector and query in sector and sector not in sectors_seen:
            sectors_seen.add(sector)
            results.append({
                "symbol": "",
                "name": "",
                "sector": s.get("sector"),
                "type": "sector",
                "_score": 80,
            })

    results.sort(key=lambda x: x.get("_score", 0), reverse=True)
    return results[:limit]


def search_by_sector(sector: str, stocks: List[Dict]) -> List[Dict]:
    """Filter stocks by sector (case-insensitive partial match)"""
    if not sector or not stocks:
        return []
    sector_lower = sector.strip().lower()
    return [s for s in stocks if sector_lower in str(s.get("sector", "")).lower()]


def search_by_market_cap(stocks: List[Dict], category: str) -> List[Dict]:
    """
    category: 'large' (>=20000cr), 'mid' (5000-20000cr), 'small' (<5000cr)
    """
    if not stocks:
        return []

    category = category.strip().lower()

    def _cap_value(stock: Dict) -> float:
        val = stock.get("market_cap", 0)
        if val is None:
            return 0
        return float(val)

    if category == "large":
        return [s for s in stocks if _cap_value(s) >= 20_000]
    elif category == "mid":
        return [s for s in stocks if 5_000 <= _cap_value(s) < 20_000]
    elif category == "small":
        return [s for s in stocks if _cap_value(s) < 5_000]
    else:
        return []
