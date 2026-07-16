from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Prompt(Base):
    __tablename__ = "prompts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    input_text: Mapped[str] = mapped_column(Text())
    output_text: Mapped[str | None] = mapped_column(Text(), nullable=True)
