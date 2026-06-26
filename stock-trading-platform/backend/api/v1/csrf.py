import secrets

from fastapi import APIRouter, Response


router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.get("/csrf-token")
async def get_csrf_token(response: Response):
    token = secrets.token_hex(32)
    response.set_cookie(
        key="csrf_token",
        value=token,
        httponly=True,
        samesite="strict",
        path="/",
    )
    return {"csrf_token": token}
