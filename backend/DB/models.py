from typing import Optional, List
from datetime import datetime, UTC
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import UniqueConstraint
from enum import Enum

class Role(str, Enum):
    attendee = "attendee"
    host = "host"
    vendor = "vendor"
    admin = "admin"

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, nullable=False, max_length=255)
    name: Optional[str] = None
    hashed_password: Optional[str] = None
    role: Role = Field(default=Role.attendee)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    rsvps: List["RSVP"] = Relationship(back_populates="user")
    events: List["Event"] = Relationship(back_populates="host")  # if user is host

class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    time: Optional[datetime] = None
    cost: Optional[str] = None
    url: Optional[str] = None
    is_public: bool = Field(default=True)
    host_id: Optional[int] = Field(default=None, foreign_key="user.id")

    host: Optional[User] = Relationship(back_populates="events")
    rsvps: List["RSVP"] = Relationship(back_populates="event")

class RSVP(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("user_id", "event_id", name="unique_user_event_rsvp"),)
    
    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: int = Field(foreign_key="event.id")
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    status: str = Field(default="yes")  # yes/no/maybe

    event: Optional[Event] = Relationship(back_populates="rsvps")
    user: Optional[User] = Relationship(back_populates="rsvps")

class VendorApplicationStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class VendorApplication(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    business_name: str
    contact_email: Optional[str] = None
    submitted_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    status: VendorApplicationStatus = Field(default=VendorApplicationStatus.pending)
    submitted_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    notes: Optional[str] = None

    submitted_by: Optional[User] = Relationship()