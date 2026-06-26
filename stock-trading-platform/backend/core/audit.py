import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_log_lock = threading.Lock()
_max_bytes: int = int(os.environ.get("AUDIT_LOG_MAX_BYTES", str(50 * 1024 * 1024)))
_log_dir: str = os.environ.get("AUDIT_LOG_DIR", "logs")
_log_file: str = os.environ.get("AUDIT_LOG_FILE", "audit.log")


def _log_path() -> Path:
    return Path(_log_dir) / _log_file


def _ensure_log_dir() -> Path:
    path = _log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _rotate_if_needed(log_path: Path) -> None:
    if not log_path.exists():
        return
    try:
        size = log_path.stat().st_size
    except OSError:
        return
    if size <= _max_bytes:
        return
    for i in range(1, 1000):
        rotated = Path(f"{log_path}.{i}")
        if not rotated.exists():
            try:
                log_path.rename(rotated)
            except OSError:
                pass
            return


def audit_log(
    event: str,
    user: str = "anonymous",
    ip: str = "unknown",
    details: Optional[dict] = None,
) -> None:
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "user": user,
        "ip": ip,
        "details": details or {},
    }
    with _log_lock:
        try:
            log_path = _ensure_log_dir()
            _rotate_if_needed(log_path)
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, default=str, ensure_ascii=False) + "\n")
        except OSError as e:
            import logging

            logging.getLogger(__name__).error("audit_log write failed: %s", e)


def set_max_bytes(size: int) -> None:
    global _max_bytes
    _max_bytes = size


def set_log_path(directory: str, filename: str = "audit.log") -> None:
    global _log_dir, _log_file
    _log_dir = directory
    _log_file = filename
