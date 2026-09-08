"""Tests for SQLModel database models."""
import pytest
from sqlmodel import Session
from backend.DB.models import User, Event, RSVP, VendorApplication, Role
from backend.DB.database import engine


@pytest.mark.unit
def test_user_creation_defaults():
    """Test user with default values."""
    with Session(engine) as session:
        user = User(name="Test User", email="testuser@example.com", hashed_password="pass123")
        session.add(user)
        session.commit()
        session.refresh(user)
        
        assert user.id is not None
        assert user.role == Role.attendee
        assert user.created_at is not None
        
        # Cleanup
        session.delete(user)
        session.commit()


@pytest.mark.unit
def test_event_creation():
    """Test creating event with required fields."""
    with Session(engine) as session:
        # Create host first
        host = User(name="Host", email="eventhost@example.com", hashed_password="pass", role=Role.host)
        session.add(host)
        session.commit()
        session.refresh(host)
        
        # Create event
        event = Event(title="Test Event", host_id=host.id)
        session.add(event)
        session.commit()
        session.refresh(event)
        
        assert event.id is not None
        assert event.title == "Test Event"
        assert event.is_public == True
        
        # Cleanup
        session.delete(event)
        session.delete(host)
        session.commit()


@pytest.mark.unit  
def test_rsvp_creation():
    """Test creating RSVP."""
    with Session(engine) as session:
        # Create host and event
        host = User(name="Host", email="rsvphost@example.com", hashed_password="pass", role=Role.host)
        session.add(host)
        session.commit()
        
        event = Event(title="RSVP Event", host_id=host.id)
        session.add(event)
        session.commit()
        
        # Create attendee
        attendee = User(name="Attendee", email="attendee@example.com", hashed_password="pass")
        session.add(attendee)
        session.commit()
        
        # Create RSVP
        rsvp = RSVP(event_id=event.id, user_id=attendee.id, status="yes")
        session.add(rsvp)
        session.commit()
        session.refresh(rsvp)
        
        assert rsvp.id is not None
        assert rsvp.status == "yes"
        
        # Cleanup
        session.delete(rsvp)
        session.delete(attendee)
        session.delete(event)
        session.delete(host)
        session.commit()
