from datetime import datetime
from typing import Dict
import threading
from jose import jwt


_blacklist: Dict[str, float] = {}
_lock = threading.Lock()
_operation_count = 0


def blacklist_token(token: str) -> None:
    global _operation_count
    claims = jwt.get_unverified_claims(token)
    jti = claims.get("jti")
    exp = claims.get("exp")
    if jti is None or exp is None:
        return
    with _lock:
        _blacklist[jti] = float(exp)
        _operation_count += 1
        if _operation_count >= 100:
            _operation_count = 0
            cleanup_blacklist()


def is_token_blacklisted(token: str) -> bool:
    claims = jwt.get_unverified_claims(token)
    jti = claims.get("jti")
    if jti is None:
        return False
    return is_token_blacklisted_by_jti(jti)


def is_token_blacklisted_by_jti(jti: str) -> bool:
    with _lock:
        entry = _blacklist.get(jti)
        if entry is None:
            return False
        if datetime.utcnow().timestamp() >= entry:
            del _blacklist[jti]
            return False
        return True


def cleanup_blacklist() -> None:
    now = datetime.utcnow().timestamp()
    with _lock:
        expired = [jti for jti, exp in _blacklist.items() if now >= exp]
        for jti in expired:
            del _blacklist[jti]
