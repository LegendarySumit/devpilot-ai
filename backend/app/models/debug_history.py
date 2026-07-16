from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class DebugHistory(Base):
    __tablename__ = "debug_history"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    error_message: Mapped[str] = mapped_column(Text())
    resolution: Mapped[str | None] = mapped_column(Text(), nullable=True)
