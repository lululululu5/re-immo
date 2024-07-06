from datetime import datetime, timezone
from typing import Optional
import enum

import sqlalchemy as sa
import sqlalchemy.orm as so

from app import db


class UserTypes(enum.Enum):
    general = "general"
    partner = "partner"
    admin = "admin"

class User(db.Model):
    __tablename__ = "users"
    
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), index=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(128), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    user_type: so.Mapped[UserTypes] = so.mapped_column(sa.Enum(UserTypes, validate_strings=True), default=UserTypes.general)
    # building = so.WriteOnlyMapped["Building"] = so.relationship(back_populates="owner")
    
    def __repr__(self) -> str:
        return f"<User: {self.name} Email: {self.email} >"
    
    

# class Building(db.Model):
#     __tablename__ = "buildings"
    
#     id: so.Mapped[int] = so.mapped_column(primary_key=True)
#     user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
#     address: so.Mapped[str] = so.mapped_column(sa.String(128), index=True)
    
    
    
    
#     owner: so.Mapped[User] = so.relationship(back_populates="building")
    
#     def __repr__(self) -> str:
#         return f"Building {self.address}"
    

    
    