import asyncio
import json
import logging
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List

import sentry_sdk
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.openapi.utils import get_openapi
from sqlalchemy import text
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware

from core.config import settings
from core.database import get_db, engine
from core.security import get_password_hash, verify_token
from models import User, create_tables
from middleware.error_handler import global_exception_handler
from middleware.rate_limiter import RateLimitMiddleware
from middleware.security_headers import SecurityHeadersMiddleware
from comprehensive_indian_stocks import mock_provider

logging.basicConfig(level=logging.INFO)
logging.getLogger('yfinance').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass


manager = ConnectionManager()


async def broadcast_stock_updates():
    while True:
        try:
            stocks = mock_provider.get_all_stocks()
            updates = [{"symbol": s["symbol"], "price": s["current_price"], "change": s["change"], "change_percent": s["change_percent"]} for s in stocks]
            await manager.broadcast(json.dumps({"type": "PRICE_UPDATE", "data": updates}))
            await asyncio.sleep(5)
        except Exception as e:
            logger.error(f"Error broadcasting stock updates: {e}")
            await asyncio.sleep(5)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    logger.info("Database tables created successfully")
    broadcast_task = asyncio.create_task(broadcast_stock_updates())

    db = next(get_db())
    try:
        demo_email = "demo@stoxly.ai"
        user = db.query(User).filter(User.email == demo_email).first()
        if not user:
            logger.info("Creating demo user")
            hashed_password = get_password_hash("demo123")
            demo_user = User(username="Demo User", email=demo_email, hashed_password=hashed_password)
            db.add(demo_user)
            db.commit()
    except Exception as e:
        logger.error(f"Error creating demo user: {e}")
    finally:
        db.close()

    yield
    broadcast_task.cancel()
    logger.info("Application shutting down")


if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=0.1,
        environment="production" if not settings.DEBUG else "development",
    )

app = FastAPI(title=settings.APP_NAME, description="Stoxly.ai - Indian stock trading platform with AI-powered chat, portfolio optimization, and screener", version=settings.VERSION, lifespan=lifespan, contact={"name": "Stoxly Team", "url": "https://stoxly.ai"}, license_info={"name": "Proprietary"})

app.add_exception_handler(Exception, global_exception_handler)

app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS, allow_credentials=True, allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"], allow_headers=["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"])
app.add_middleware(RateLimitMiddleware)
app.add_middleware(SecurityHeadersMiddleware)


class RequestBodyLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method in ("POST", "PUT", "PATCH"):
            cl = request.headers.get("content-length")
            if cl and int(cl) > 1_048_576:
                raise HTTPException(status_code=413, detail="Request body too large (max 1MB)")
        return await call_next(request)


app.add_middleware(RequestBodyLimitMiddleware)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/api/v1/health")
async def health_check():
    db_ok = False
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            db_ok = True
    except Exception:
        pass
    return {"status": "healthy" if db_ok else "degraded", "database": "connected" if db_ok else "disconnected", "timestamp": datetime.utcnow().isoformat(), "version": settings.VERSION, "environment": "production" if not settings.DEBUG else "development"}


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(title=settings.APP_NAME, version=settings.VERSION, description="Stoxly.ai API - Indian stock trading platform", routes=app.routes)
    openapi_schema["info"]["x-logo"] = {"url": "https://stoxly.ai/logo.png"}
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

from api.v1 import auth, stocks, portfolio, watchlist, screener, indian_stocks, chat, profile, recommendations

app.include_router(auth.router)
app.include_router(stocks.router)
app.include_router(portfolio.router)
app.include_router(watchlist.router)
app.include_router(screener.router)
app.include_router(indian_stocks.router)
app.include_router(chat.router)
app.include_router(profile.router)
app.include_router(recommendations.router)

import profile_endpoints
app.include_router(profile_endpoints.router)


@app.websocket("/ws/stocks")
async def websocket_endpoint(websocket: WebSocket, token: str = ""):
    token = websocket.query_params.get("token", token)
    if not token:
        await websocket.close(code=4001, reason="Missing auth token")
        return
    try:
        verify_token(token)
    except Exception:
        await websocket.close(code=4001, reason="Invalid auth token")
        return
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
