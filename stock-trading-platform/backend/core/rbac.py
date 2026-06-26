from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from core.security import verify_token
from repositories.user_repository import UserRepository

security_scheme = HTTPBearer()

ROLE_HIERARCHY = {"free": 0, "premium": 10, "pro": 20, "admin": 99}


def require_role(min_role: str):
    def dependency(
        authorization: HTTPAuthorizationCredentials = Depends(security_scheme),
        db: Session = Depends(get_db),
    ):
        email = verify_token(authorization.credentials)
        user = UserRepository(db).get_by_email(email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        if ROLE_HIERARCHY.get(user.role, -1) < ROLE_HIERARCHY.get(min_role, 0):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user

    return Depends(dependency)


require_admin = require_role("admin")
