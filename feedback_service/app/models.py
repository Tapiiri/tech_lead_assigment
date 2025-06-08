from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    feedback = Column(String, nullable=False, doc="The feedback text")
    created_at = Column(
        DateTime, default=datetime.utcnow, nullable=False,
        doc="Timestamp when this feedback was created"
    )
    deleted = Column(
        Boolean, default=False, nullable=False,
        doc="Soft-delete flag; True means this feedback is considered deleted"
    )