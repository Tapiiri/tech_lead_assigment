from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app import schemas, crud
from app.db import get_db

router = APIRouter()


@router.post(
    "/", response_model=schemas.FeedbackRead, status_code=status.HTTP_201_CREATED
)
def create_feedback(payload: schemas.FeedbackCreate, db: Session = Depends(get_db)):
    return crud.create_feedback(db, payload)


@router.get("/", response_model=List[schemas.FeedbackRead])
def list_feedback(db: Session = Depends(get_db)):
    return crud.get_feedbacks(db)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_feedback(db: Session = Depends(get_db)):
    crud.soft_delete_feedbacks(db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
