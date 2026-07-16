from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class WorkspaceItem(Base):
    __tablename__ = "workspace_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    artifact_type: Mapped[str] = mapped_column(String(100), index=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    input_payload: Mapped[str] = mapped_column(Text())
    output_payload: Mapped[str | None] = mapped_column(Text(), nullable=True)
    pipeline: Mapped[str] = mapped_column(String(50), index=True)
    status: Mapped[str] = mapped_column(String(50), default="queued")
