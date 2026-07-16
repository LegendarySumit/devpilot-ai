from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Documentation(Base):
    __tablename__ = "documentation"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    doc_type: Mapped[str] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(Text())
