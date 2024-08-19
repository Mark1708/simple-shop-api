import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID

from src.db.postgres import Base


class Category(Base):
    """Shop Category"""

    __tablename__ = "shop_category"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
        doc="Category's ID."
    )
    name = Column(
        String(32),
        nullable=False,
        unique=True,
        doc="Category's name."
    )


    def __repr__(self) -> str:
        return f'<Category {self.name}>'