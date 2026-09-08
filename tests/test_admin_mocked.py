"""Mocked tests for admin functionality."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from backend.DB.models import User, Event, RSVP
from datetime import datetime


@pytest.mark.api
@patch('backend.main.Session')
def test_create_admin_user_mocked(mock_session_class):
    """Test creating an admin user with mocked database."""
    from backend.main import app
    from fastapi.testclient import TestClient
    
    # Setup mock session
    mock_session = MagicMock()
    mock_session_class.return_value.__enter__.return_value = mock_session
    
    # Mock that email doesn't exist
    mock_session.exec.return_value.first.return_value = None
    
    # Mock the created user
    mock_user = User(id=1, name="Admin User", email="admin@test.com", role="admin", hashed_password="pass")
    mock_session.refresh.side_effect = lambda obj: setattr(obj, 'id', 1)
    
    client = TestClient(app)
    response = client.post("/api/users", json={
        "name": "Admin User",
        "email": "admin@test.com",
        "password": "adminpass",
        "role": "admin"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "admin@test.com"
    assert data["role"] == "admin"
    assert "id" in data
    
    # Verify session methods were called
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()


@pytest.mark.api
@patch('backend.main.Session')
def test_admin_login_mocked(mock_session_class):
    """Test admin user login with mocked database."""
    from backend.main import app
    from fastapi.testclient import TestClient
    
    # Setup mock session
    mock_session = MagicMock()
    mock_session_class.return_value.__enter__.return_value = mock_session
    
    # Mock user in database
    mock_user = User(id=1, name="Admin User", email="admin@test.com", role="admin", hashed_password="adminpass")
    mock_session.exec.return_value.first.return_value = mock_user
    
    client = TestClient(app)
    response = client.post("/api/login", json={
        "email": "admin@test.com",
        "password": "adminpass"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin@test.com"
    assert data["role"] == "admin"


@pytest.mark.api
@patch('backend.main.Session')
def test_delete_user_mocked(mock_session_class):
    """Test deleting a user with mocked database."""
    from backend.main import app
    from fastapi.testclient import TestClient
    
    # Setup mock session
    mock_session = MagicMock()
    mock_session_class.return_value.__enter__.return_value = mock_session
    
    # Mock user exists
    mock_user = User(id=1, name="User to Delete", email="delete@test.com", role="attendee", hashed_password="pass")
    mock_session.get.return_value = mock_user
    mock_session.exec.return_value.all.return_value = []  # No events for this user
    
    client = TestClient(app)
    response = client.delete("/api/user/1")
    
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]
    
    # Verify delete was called
    mock_session.delete.assert_called_once_with(mock_user)
    mock_session.commit.assert_called_once()


@pytest.mark.api
@patch('backend.main.Session')
def test_delete_event_mocked(mock_session_class):
    """Test deleting an event with mocked database."""
    from backend.main import app
    from fastapi.testclient import TestClient
    
    # Setup mock session
    mock_session = MagicMock()
    mock_session_class.return_value.__enter__.return_value = mock_session
    
    # Mock event exists
    mock_event = Event(id=1, title="Test Event", location="Test Location", host_id=1, is_public=True)
    mock_session.get.return_value = mock_event
    
    client = TestClient(app)
    response = client.delete("/api/events/1")
    
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]
    
    # Verify delete was called
    mock_session.delete.assert_called_once_with(mock_event)
    mock_session.commit.assert_called_once()


@pytest.mark.api
@patch('backend.main.Session')
def test_admin_statistics_mocked(mock_session_class):
    """Test getting admin statistics with mocked database."""
    from backend.main import app
    from fastapi.testclient import TestClient
    
    # Setup mock session
    mock_session = MagicMock()
    mock_session_class.return_value.__enter__.return_value = mock_session
    
    # Mock statistics queries
    mock_session.exec.return_value.one.side_effect = [10, 25, 3]  # events, users, admins
    
    client = TestClient(app)
    response = client.get("/api/admin/statistics")
    
    assert response.status_code == 200
    stats = response.json()
    assert stats["total_events"] == 10
    assert stats["total_users"] == 25
    assert stats["total_admins"] == 3


@pytest.mark.api
@patch('backend.main.Session')
def test_admin_events_mocked(mock_session_class):
    """Test getting admin events with mocked database."""
    from backend.main import app
    from fastapi.testclient import TestClient
    
    # Setup mock session
    mock_session = MagicMock()
    mock_session_class.return_value.__enter__.return_value = mock_session
    
    # Mock public events
    mock_event1 = Event(
        id=1, 
        title="Public Event 1", 
        location="Location 1", 
        description="Description 1",
        time=datetime(2026, 3, 15, 19, 0),
        cost="Free",
        url="",
        host_id=1, 
        is_public=True
    )
    mock_event2 = Event(
        id=2, 
        title="Public Event 2", 
        location="Location 2",
        description="Description 2",
        time=datetime(2026, 3, 20, 20, 0),
        cost="$10",
        url="",
        host_id=1, 
        is_public=True
    )
    
    # First exec call returns events, subsequent calls return RSVP counts
    mock_session.exec.return_value.all.return_value = [mock_event1, mock_event2]
    mock_session.exec.return_value.one.side_effect = [5, 3]  # RSVP counts for each event
    
    client = TestClient(app)
    response = client.get("/api/admin/events")
    
    assert response.status_code == 200
    events = response.json()
    assert len(events) == 2
    assert all(e["is_public"] == True for e in events)
    assert events[0]["rsvp_count"] == 5
    assert events[1]["rsvp_count"] == 3


@pytest.mark.api
@patch('backend.main.Session')
def test_list_all_users_mocked(mock_session_class):
    """Test listing all users with mocked database."""
    from backend.main import app
    from fastapi.testclient import TestClient
    
    # Setup mock session
    mock_session = MagicMock()
    mock_session_class.return_value.__enter__.return_value = mock_session
    
    # Mock users
    mock_users = [
        User(id=1, name="Admin User", email="admin@test.com", role="admin", hashed_password="pass"),
        User(id=2, name="Host User", email="host@test.com", role="host", hashed_password="pass"),
        User(id=3, name="Attendee User", email="attendee@test.com", role="attendee", hashed_password="pass"),
    ]
    mock_session.exec.return_value.all.return_value = mock_users
    
    client = TestClient(app)
    response = client.get("/api/user")
    
    assert response.status_code == 200
    users = response.json()
    assert len(users) == 3
    
    roles = {user["role"] for user in users}
    assert "admin" in roles
    assert "host" in roles
    assert "attendee" in roles


@pytest.mark.api
@patch('backend.main.Session')
def test_delete_host_with_events_mocked(mock_session_class):
    """Test deleting a host user also deletes their events."""
    from backend.main import app
    from fastapi.testclient import TestClient
    
    # Setup mock session
    mock_session = MagicMock()
    mock_session_class.return_value.__enter__.return_value = mock_session
    
    # Mock host user
    mock_user = User(id=1, name="Host User", email="host@test.com", role="host", hashed_password="pass")
    mock_session.get.return_value = mock_user
    
    # Mock events for this host
    mock_events = [
        Event(id=1, title="Event 1", location="Location 1", host_id=1, is_public=True),
        Event(id=2, title="Event 2", location="Location 2", host_id=1, is_public=True),
    ]
    mock_session.exec.return_value.all.return_value = mock_events
    
    client = TestClient(app)
    response = client.delete("/api/user/1")
    
    assert response.status_code == 200
    
    # Verify all events were deleted
    assert mock_session.delete.call_count == 3  # 2 events + 1 user
    mock_session.commit.assert_called_once()


@pytest.mark.api
@patch('backend.main.Session')
def test_duplicate_admin_email_mocked(mock_session_class):
    """Test that duplicate admin emails are rejected."""
    from backend.main import app
    from fastapi.testclient import TestClient
    
    # Setup mock session
    mock_session = MagicMock()
    mock_session_class.return_value.__enter__.return_value = mock_session
    
    # Mock that email already exists
    existing_user = User(id=1, name="Existing Admin", email="admin@test.com", role="admin", hashed_password="pass")
    mock_session.exec.return_value.first.return_value = existing_user
    
    client = TestClient(app)
    response = client.post("/api/users", json={
        "name": "Second Admin",
        "email": "admin@test.com",
        "password": "pass",
        "role": "admin"
    })
    
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


@pytest.mark.api
@patch('backend.main.Session')
def test_create_event_validates_host_role_mocked(mock_session_class):
    """Test that only host/admin can create events."""
    from backend.main import app
    from fastapi.testclient import TestClient
    
    # Setup mock session
    mock_session = MagicMock()
    mock_session_class.return_value.__enter__.return_value = mock_session
    
    # Mock attendee user (not allowed to create events)
    mock_user = User(id=1, name="Attendee", email="attendee@test.com", role="attendee", hashed_password="pass")
    mock_session.get.return_value = mock_user
    
    client = TestClient(app)
    response = client.post("/api/events", json={
        "title": "Test Event",
        "location": "Test Location",
        "host_id": 1,
        "is_public": True
    })
    
    assert response.status_code == 403
    assert "must be a host or admin" in response.json()["detail"].lower()


@pytest.mark.api
@patch('backend.main.Session')
def test_admin_can_create_events_mocked(mock_session_class):
    """Test that admin users can create events."""
    from backend.main import app
    from fastapi.testclient import TestClient
    
    # Setup mock session
    mock_session = MagicMock()
    mock_session_class.return_value.__enter__.return_value = mock_session
    
    # Mock admin user
    mock_admin = User(id=1, name="Admin", email="admin@test.com", role="admin", hashed_password="pass")
    mock_session.get.return_value = mock_admin
    
    # Mock the created event
    def set_event_id(event):
        event.id = 1
    
    mock_session.refresh.side_effect = set_event_id
    
    client = TestClient(app)
    response = client.post("/api/events", json={
        "title": "Admin Event",
        "location": "Admin Location",
        "host_id": 1,
        "is_public": True
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Admin Event"
    assert data["host_id"] == 1


@pytest.mark.api
def test_admin_statistics_endpoint_structure():
    """Test admin statistics endpoint returns correct structure without database."""
    from backend.main import app
    from fastapi.testclient import TestClient
    
    with patch('backend.main.Session') as mock_session_class:
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        mock_session.exec.return_value.one.side_effect = [0, 0, 0]
        
        client = TestClient(app)
        response = client.get("/api/admin/statistics")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_events" in data
        assert "total_users" in data
        assert "total_admins" in data
        assert isinstance(data["total_events"], int)
        assert isinstance(data["total_users"], int)
        assert isinstance(data["total_admins"], int)
