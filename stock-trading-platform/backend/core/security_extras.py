import re
from datetime import datetime, timedelta
from typing import Dict, Tuple


class BruteForceProtection:
    def __init__(self, max_attempts: int = 5, lockout_minutes: int = 15):
        self.max_attempts = max_attempts
        self.lockout_minutes = lockout_minutes
        self.attempts: Dict[str, list] = {}

    def record_attempt(self, key: str, success: bool):
        now = datetime.utcnow()
        if key not in self.attempts:
            self.attempts[key] = []
        self.attempts[key] = [t for t in self.attempts[key] if t > now - timedelta(minutes=self.lockout_minutes)]
        if not success:
            self.attempts[key].append(now)

    def is_locked(self, key: str) -> Tuple[bool, int]:
        now = datetime.utcnow()
        if key not in self.attempts:
            return False, 0
        self.attempts[key] = [t for t in self.attempts[key] if t > now - timedelta(minutes=self.lockout_minutes)]
        if len(self.attempts[key]) >= self.max_attempts:
            return True, (self.attempts[key][-1] + timedelta(minutes=self.lockout_minutes) - now).seconds
        return False, self.max_attempts - len(self.attempts[key])

    def reset(self, key: str):
        self.attempts.pop(key, None)


brute_force_protection = BruteForceProtection()


def validate_password(password: str) -> Tuple[bool, str]:
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    return True, ""


def sanitize_input(text: str) -> str:
    if not text:
        return text
    text = re.sub(r"<[^>]*>", "", text)
    text = text.strip()[:500]
    return text
