from sqlalchemy.orm import Session
from models import WatchList, Stock


class StockRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, stock_id: int) -> Stock | None:
        return self.db.query(Stock).filter(Stock.id == stock_id).first()

    def get_by_symbol(self, symbol: str) -> Stock | None:
        return self.db.query(Stock).filter(Stock.symbol == symbol).first()

    def create(self, symbol: str, name: str, exchange: str | None = None,
               sector: str | None = None, market_cap: float | None = None) -> Stock:
        stock = Stock(
            symbol=symbol, name=name, exchange=exchange,
            sector=sector, market_cap=market_cap
        )
        self.db.add(stock)
        self.db.commit()
        self.db.refresh(stock)
        return stock


class WatchListRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: int) -> list[WatchList]:
        return self.db.query(WatchList).filter(WatchList.user_id == user_id).all()

    def get_by_user_and_stock(self, user_id: int, stock_id: int) -> WatchList | None:
        return self.db.query(WatchList).filter(
            WatchList.user_id == user_id, WatchList.stock_id == stock_id
        ).first()

    def get_by_id_and_user(self, item_id: int, user_id: int) -> WatchList | None:
        return self.db.query(WatchList).filter(
            WatchList.id == item_id, WatchList.user_id == user_id
        ).first()

    def create(self, user_id: int, stock_id: int) -> WatchList:
        item = WatchList(user_id=user_id, stock_id=stock_id)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, item: WatchList) -> None:
        self.db.delete(item)
        self.db.commit()
