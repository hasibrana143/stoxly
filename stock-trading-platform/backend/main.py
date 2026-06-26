import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from core.config import settings
from core.database import get_db
from core.security import get_password_hash
from models import User, create_tables
from middleware.error_handler import global_exception_handler
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


app = FastAPI(title=settings.APP_NAME, description="Comprehensive stock trading platform with AI chat and portfolio optimization", version=settings.VERSION, lifespan=lifespan)

app.add_exception_handler(Exception, global_exception_handler)

app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

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
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
