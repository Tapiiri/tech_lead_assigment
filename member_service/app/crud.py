from sqlalchemy.orm import Session
from app.models import Member
from app.schemas import MemberCreate


def create_member(db: Session, payload: MemberCreate) -> Member:
    data = payload.model_dump()
    data["avatar_url"] = str(data["avatar_url"])
    member = Member(**data)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def get_members(db: Session):
    return (
        db.query(Member)
        .filter(Member.deleted == False)
        .order_by(Member.followers.desc())
        .all()
    )


def soft_delete_members(db: Session):
    db.query(Member).update({Member.deleted: True})
    db.commit()
