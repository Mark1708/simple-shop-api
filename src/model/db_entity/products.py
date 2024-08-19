import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID

from src.db.postgres import Base


class Product(Base):
    """Shop Product"""

    __tablename__ = "shop_product"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
        doc="Product's ID."
    )
    name = Column(
        String(32),
        nullable=False,
        unique=True,
        doc="Product's name."
    )

    def __repr__(self) -> str:
        return f'<Product {self.name}>'