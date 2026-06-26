from sqlalchemy.orm import Session
from models import ChatHistory


class ChatHistoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: int) -> list[ChatHistory]:
        return self.db.query(ChatHistory).filter(
            ChatHistory.user_id == user_id
        ).order_by(ChatHistory.created_at.desc()).all()

    def get_by_id(self, chat_id: int) -> ChatHistory | None:
        return self.db.query(ChatHistory).filter(ChatHistory.id == chat_id).first()

    def create(self, user_id: int, message: str, response: str) -> ChatHistory:
        entry = ChatHistory(user_id=user_id, message=message, response=response)
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def delete(self, entry: ChatHistory) -> None:
        self.db.delete(entry)
        self.db.commit()
