from sqlalchemy.orm import Session
from models import Portfolio, Holding


class PortfolioRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id_and_user(self, portfolio_id: int, user_id: int) -> Portfolio | None:
        return self.db.query(Portfolio).filter(
            Portfolio.id == portfolio_id, Portfolio.user_id == user_id
        ).first()

    def get_by_user_id(self, user_id: int) -> list[Portfolio]:
        return self.db.query(Portfolio).filter(Portfolio.user_id == user_id).all()

    def create(self, name: str, description: str | None, user_id: int) -> Portfolio:
        portfolio = Portfolio(name=name, description=description, user_id=user_id)
        self.db.add(portfolio)
        self.db.commit()
        self.db.refresh(portfolio)
        return portfolio


class HoldingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_portfolio_and_symbol(self, portfolio_id: int, symbol: str) -> Holding | None:
        return self.db.query(Holding).filter(
            Holding.portfolio_id == portfolio_id, Holding.symbol == symbol
        ).first()

    def get_by_id_and_portfolio(self, holding_id: int, portfolio_id: int) -> Holding | None:
        return self.db.query(Holding).filter(
            Holding.id == holding_id, Holding.portfolio_id == portfolio_id
        ).first()

    def get_by_portfolio_id(self, portfolio_id: int) -> list[Holding]:
        return self.db.query(Holding).filter(Holding.portfolio_id == portfolio_id).all()

    def create(self, portfolio_id: int, symbol: str, quantity: float, average_price: float) -> Holding:
        holding = Holding(
            portfolio_id=portfolio_id, symbol=symbol,
            quantity=quantity, average_price=average_price
        )
        self.db.add(holding)
        self.db.commit()
        self.db.refresh(holding)
        return holding

    def delete(self, holding: Holding) -> None:
        self.db.delete(holding)
        self.db.commit()
