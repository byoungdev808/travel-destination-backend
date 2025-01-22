from sqlalchemy import Column, Integer, Text, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Destination(Base):
    __tablename__ = "destinations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    knowledge_bases = relationship("KnowledgeBase", back_populates="destination", cascade="all, delete-orphan")

class KnowledgeBase(Base):
    __tablename__ = "knowledge_bases"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    vector_db_doc_id = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Foreign Key to Destination
    destination_id = Column(Integer, ForeignKey("destinations.id"))

    # Relationship to Destination
    destination = relationship("Destination", back_populates="knowledge_bases")

