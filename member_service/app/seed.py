from sqlalchemy.orm import Session
from app.crud import create_member
from app.models import Member
from app.schemas import MemberCreate

def seed_members(db: Session):
    """
    Insert a couple of sample members if none exist.
    """
    # Only seed if there are no non-deleted members
    existing = db.query(Member).filter(Member.deleted == False).count()
    if existing > 0:
        return

    samples = [
        MemberCreate(
            first_name="John",
            last_name="Doe",
            login="john123",
            avatar_url="https://example.com/avatar.jpg",
            followers=120,
            following=35,
            title="Senior Developer",
            email="john@example.com"
        ),
        MemberCreate(
            first_name="Jane",
            last_name="Smith",
            login="jane456",
            avatar_url="https://example.com/avatar2.jpg",
            followers=80,
            following=20,
            title="Developer",
            email="jane@example.com"
        )
    ]

    for member_data in samples:
        create_member(db, member_data)