from sqlalchemy.orm import Session
from . import models, schemas

def create_feedback(db: Session, fb: schemas.FeedbackCreate) -> models.Feedback:
    db_fb = models.Feedback(feedback=fb.feedback)
    db.add(db_fb)
    db.commit()
    db.refresh(db_fb)
    return db_fb

def get_feedbacks(db: Session):
    return db.query(models.Feedback).filter(models.Feedback.deleted == False).all()

def soft_delete_feedbacks(db: Session):
    db.query(models.Feedback).filter(models.Feedback.deleted == False).update({models.Feedback.deleted: True})
    db.commit()