from sqlalchemy import Column, String, ForeignKey, DateTime, func, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from src.database import Base


class Activity(Base):
    __tablename__ = "activities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    deal_id = Column(UUID(as_uuid=True), ForeignKey("deals.id"))
    contact_id = Column(UUID(as_uuid=True), ForeignKey("contacts.id"))
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"))
    type = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    organization = relationship("Organization", backref="activities")
    user = relationship("User", backref="activities")
    deal = relationship("Deal", backref="activities")
    contact = relationship("Contact", backref="activities")
    task = relationship("Task", backref="activities")

