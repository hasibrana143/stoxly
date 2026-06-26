from sqlalchemy.orm import Session
from models import UserScreenerFilter


class UserScreenerFilterRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: int) -> list[UserScreenerFilter]:
        return self.db.query(UserScreenerFilter).filter(
            UserScreenerFilter.user_id == user_id
        ).order_by(UserScreenerFilter.id.desc()).all()

    def get_by_id_and_user(self, filter_id: int, user_id: int) -> UserScreenerFilter | None:
        return self.db.query(UserScreenerFilter).filter(
            UserScreenerFilter.id == filter_id,
            UserScreenerFilter.user_id == user_id
        ).first()

    def create(self, user_id: int, filter_name: str,
               filter_criteria: str) -> UserScreenerFilter:
        user_filter = UserScreenerFilter(
            user_id=user_id, filter_name=filter_name,
            filter_criteria=filter_criteria
        )
        self.db.add(user_filter)
        self.db.commit()
        self.db.refresh(user_filter)
        return user_filter

    def delete(self, user_filter: UserScreenerFilter) -> None:
        self.db.delete(user_filter)
        self.db.commit()
