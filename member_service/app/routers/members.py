from typing import List
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.db import get_db

router = APIRouter()


@router.post(
    "/", response_model=schemas.MemberRead, status_code=status.HTTP_201_CREATED
)
def create_member(payload: schemas.MemberCreate, db: Session = Depends(get_db)):
    return crud.create_member(db, payload)


@router.get(
    "/", response_model=List[schemas.MemberRead], status_code=status.HTTP_200_OK
)
def list_members(db: Session = Depends(get_db)):
    return crud.get_members(db)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_members(db: Session = Depends(get_db)):
    crud.soft_delete_members(db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
