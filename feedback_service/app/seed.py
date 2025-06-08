from sqlalchemy.orm import Session
from app.crud import create_feedback, get_feedbacks
from app.schemas import FeedbackCreate


def seed_feedback(db: Session):
    """
    Insert a couple of sample feedback entries if none exist.
    """
    existing = get_feedbacks(db)
    if existing:
        return

    samples = [
        FeedbackCreate(
            feedback="Great team culture, clear communication, and strong support for growth."
        ),
        FeedbackCreate(
            feedback="The process was smooth and the team was very supportive."
        ),
    ]

    for feedback_data in samples:
        create_feedback(db, feedback_data)
