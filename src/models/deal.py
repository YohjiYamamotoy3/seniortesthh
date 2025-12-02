from sqlalchemy import Column, String, ForeignKey, DateTime, func, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from src.database import Base


class Deal(Base):
    __tablename__ = "deals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("contacts.id"), nullable=False)
    title = Column(String(255), nullable=False)
    value = Column(Numeric(12, 2))
    stage = Column(String(100), nullable=False, default="new")
    status = Column(String(50), nullable=False, default="open")
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    closed_at = Column(DateTime(timezone=True))

    organization = relationship("Organization", backref="deals")
    contact = relationship("Contact", backref="deals")

