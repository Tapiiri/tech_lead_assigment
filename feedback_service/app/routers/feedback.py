from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import crud, schemas, models, db

router = APIRouter(prefix="/feedback", tags=["feedback"])

def get_db():
    session = db.SessionLocal()
    try:
        yield session
    finally:
        session.close()

@router.post("/", response_model=schemas.FeedbackRead, status_code=status.HTTP_201_CREATED)
def create_feedback(fb: schemas.FeedbackCreate, session: Session = Depends(get_db)):
    return crud.create_feedback(session, fb)

@router.get("/", response_model=list[schemas.FeedbackRead])
def list_feedback(session: Session = Depends(get_db)):
    return crud.get_feedbacks(session)

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_feedback(session: Session = Depends(get_db)):
    crud.soft_delete_feedbacks(session)
    return None