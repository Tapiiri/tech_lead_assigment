from pydantic import BaseModel
from datetime import datetime

class FeedbackCreate(BaseModel):
    feedback: str

class FeedbackRead(BaseModel):
    id: int
    feedback: str
    created_at: datetime

    class Config:
        orm_mode = True