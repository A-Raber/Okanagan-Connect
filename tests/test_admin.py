"""Tests for admin functionality."""
import pytest
import uuid
from unittest.mock import Mock, patch
from backend.DB.models import User, Event, RSVP


@pytest.mark.api
def test_create_admin_user(client):
    """Test creating an admin user."""
    email = f"admin-{uuid.uuid4()}@example.com"
    response = client.post("/api/users", json={
        "name": "Admin User",
        "email": email,
        "password": "adminpass",
        "role": "admin"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == email
    assert data["role"] == "admin"
    assert "id" in data


@pytest.mark.api
def test_admin_login(client):
    """Test admin user can login."""
    email = f"admin-login-{uuid.uuid4()}@example.com"
    # Create admin user
    client.post("/api/users", json={
        "name": "Admin Login",
        "email": email,
        "password": "adminpass",
        "role": "admin"
    })
    
    # Test login
    response = client.post("/api/login", json={
        "email": email,
        "password": "adminpass"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email
    assert data["role"] == "admin"


@pytest.mark.api
def test_admin_can_delete_any_event(client):
    """Test admin can delete events created by any host."""
    # Create host and event
    host_email = f"delete-host-{uuid.uuid4()}@example.com"
    host_resp = client.post("/api/users", json={
        "name": "Delete Host",
        "email": host_email,
        "password": "pass",
        "role": "host"
    })
    host_id = host_resp.json()["id"]
    
    event_resp = client.post("/api/events", json={
        "title": "Event to Delete",
        "location": "Test Location",
        "host_id": host_id,
        "is_public": True
    })
    event_id = event_resp.json()["id"]
    
    # Admin deletes the event
    delete_resp = client.delete(f"/api/events/{event_id}")
    assert delete_resp.status_code == 200
    
    # Verify event is deleted
    events_resp = client.get("/api/events")
    events = events_resp.json()
    assert not any(e["id"] == event_id for e in events)


@pytest.mark.api
def test_list_all_users(client):
    """Test listing all users (admin functionality)."""
    # Create multiple users with different roles
    users_to_create = [
        {"name": "User 1", "email": f"user1-{uuid.uuid4()}@example.com", "password": "pass", "role": "attendee"},
        {"name": "User 2", "email": f"user2-{uuid.uuid4()}@example.com", "password": "pass", "role": "host"},
        {"name": "User 3", "email": f"user3-{uuid.uuid4()}@example.com", "password": "pass", "role": "admin"},
    ]
    
    for user_data in users_to_create:
        client.post("/api/users", json=user_data)
    
    # List all users
    response = client.get("/api/user")
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    assert len(users) >= 3  # At least the 3 we just created
    
    # Verify different roles are returned
    roles = {user["role"] for user in users}
    assert "attendee" in roles
    assert "host" in roles
    assert "admin" in roles


@pytest.mark.api
def test_delete_user(client):
    """Test deleting a user (admin functionality)."""
    # Create user
    email = f"delete-user-{uuid.uuid4()}@example.com"
    user_resp = client.post("/api/users", json={
        "name": "User to Delete",
        "email": email,
        "password": "pass",
        "role": "attendee"
    })
    user_id = user_resp.json()["id"]
    
    # Delete user
    delete_resp = client.delete(f"/api/user/{user_id}")
    assert delete_resp.status_code == 200
    assert "deleted successfully" in delete_resp.json()["message"]
    
    # Verify user is deleted - try to login
    login_resp = client.post("/api/login", json={
        "email": email,
        "password": "pass"
    })
    assert login_resp.status_code == 401


@pytest.mark.api
def test_delete_host_with_events(client):
    """Test deleting a host user also deletes their events."""
    # Create host
    host_email = f"cascade-host-{uuid.uuid4()}@example.com"
    host_resp = client.post("/api/users", json={
        "name": "Cascade Host",
        "email": host_email,
        "password": "pass",
        "role": "host"
    })
    host_id = host_resp.json()["id"]
    
    # Create events for this host
    event1_resp = client.post("/api/events", json={
        "title": "Event 1",
        "location": "Location 1",
        "host_id": host_id
    })
    event1_id = event1_resp.json()["id"]
    
    event2_resp = client.post("/api/events", json={
        "title": "Event 2",
        "location": "Location 2",
        "host_id": host_id
    })
    event2_id = event2_resp.json()["id"]
    
    # Delete host
    delete_resp = client.delete(f"/api/user/{host_id}")
    assert delete_resp.status_code == 200
    
    # Verify events are also deleted
    events_resp = client.get("/api/events")
    events = events_resp.json()
    assert not any(e["id"] == event1_id for e in events)
    assert not any(e["id"] == event2_id for e in events)


@pytest.mark.api
def test_filter_live_events_only(client):
    """Test filtering for public/live events only via admin endpoint."""
    # Create host
    host_email = f"filter-host-{uuid.uuid4()}@example.com"
    host_resp = client.post("/api/users", json={
        "name": "Filter Host",
        "email": host_email,
        "password": "pass",
        "role": "host"
    })
    host_id = host_resp.json()["id"]
    
    # Create public event
    public_event = client.post("/api/events", json={
        "title": "Public Event",
        "location": "Public Location",
        "host_id": host_id,
        "is_public": True
    })
    public_id = public_event.json()["id"]
    
    # Create draft event
    draft_event = client.post("/api/events", json={
        "title": "Draft Event",
        "location": "Draft Location",
        "host_id": host_id,
        "is_public": False
    })
    draft_id = draft_event.json()["id"]
    
    # Get admin events (should only return public)
    admin_events_resp = client.get("/api/admin/events")
    assert admin_events_resp.status_code == 200
    admin_events = admin_events_resp.json()
    
    # Verify public event is in admin events
    assert any(e["id"] == public_id for e in admin_events)
    # Verify draft event is NOT in admin events
    assert not any(e["id"] == draft_id for e in admin_events)
    # All returned events should be public
    assert all(e["is_public"] == True for e in admin_events)


@pytest.mark.api
def test_admin_statistics(client):
    """Test getting statistics for admin dashboard."""
    # Create various users
    client.post("/api/users", json={
        "name": "Stats Admin",
        "email": f"stats-admin-{uuid.uuid4()}@example.com",
        "password": "pass",
        "role": "admin"
    })
    
    host_resp = client.post("/api/users", json={
        "name": "Stats Host",
        "email": f"stats-host-{uuid.uuid4()}@example.com",
        "password": "pass",
        "role": "host"
    })
    host_id = host_resp.json()["id"]
    
    client.post("/api/users", json={
        "name": "Stats Attendee",
        "email": f"stats-attendee-{uuid.uuid4()}@example.com",
        "password": "pass",
        "role": "attendee"
    })
    
    # Create a public event
    client.post("/api/events", json={
        "title": "Stats Event",
        "location": "Test Location",
        "host_id": host_id,
        "is_public": True
    })
    
    # Get statistics via admin endpoint
    stats_resp = client.get("/api/admin/statistics")
    assert stats_resp.status_code == 200
    
    stats = stats_resp.json()
    assert "total_events" in stats
    assert "total_users" in stats
    assert "total_admins" in stats
    assert stats["total_admins"] >= 1
    assert stats["total_users"] >= 3
    assert stats["total_events"] >= 1


@pytest.mark.api
def test_seed_creates_admin(client):
    """Test that seed endpoint creates admin user."""
    # Call seed
    seed_resp = client.post("/api/seed")
    assert seed_resp.status_code == 200
    data = seed_resp.json()
    
    # If seed was successful
    if data.get("seeded"):
        # Verify admin credentials are in response
        assert "users" in data
        assert "admin" in data["users"]
        assert "email" in data["users"]["admin"]
        assert "password" in data["users"]["admin"]
        
        # Try to login with admin credentials from response
        admin_login = client.post("/api/login", json={
            "email": data["users"]["admin"]["email"],
            "password": data["users"]["admin"]["password"]
        })
        assert admin_login.status_code == 200
        admin_data = admin_login.json()
        assert admin_data["role"] == "admin"
    else:
        # If already seeded, just verify the endpoint works and returns proper structure
        assert "seeded" in data
        assert data["seeded"] == False
        assert "reason" in data


@pytest.mark.api
def test_seed_creates_live_events(client):
    """Test that seed creates public/live events."""
    # Call seed
    seed_resp = client.post("/api/seed")
    data = seed_resp.json()
    
    if data.get("seeded"):
        # Get all events
        events_resp = client.get("/api/events")
        events = events_resp.json()
        
        # Filter for seeded events
        seeded_event_ids = data.get("event_ids", [])
        seeded_events = [e for e in events if e["id"] in seeded_event_ids]
        
        # Verify all seeded events are public
        for event in seeded_events:
            assert event.get("is_public") == True, f"Seeded event {event['title']} should be public"


@pytest.mark.api
def test_duplicate_admin_email(client):
    """Test that duplicate admin emails are rejected."""
    email = f"duplicate-admin-{uuid.uuid4()}@example.com"
    
    # Create first admin
    first_resp = client.post("/api/users", json={
        "name": "First Admin",
        "email": email,
        "password": "pass",
        "role": "admin"
    })
    assert first_resp.status_code == 201
    
    # Try to create second admin with same email
    second_resp = client.post("/api/users", json={
        "name": "Second Admin",
        "email": email,
        "password": "pass",
        "role": "admin"
    })
    assert second_resp.status_code == 400
    assert "already exists" in second_resp.json()["detail"].lower()


@pytest.mark.api
def test_admin_event_count_accuracy(client):
    """Test that admin dashboard shows accurate event counts."""
    # Create host
    host_email = f"count-host-{uuid.uuid4()}@example.com"
    host_resp = client.post("/api/users", json={
        "name": "Count Host",
        "email": host_email,
        "password": "pass",
        "role": "host"
    })
    host_id = host_resp.json()["id"]
    
    # Get initial event count
    initial_events = client.get("/api/events").json()
    initial_count = len(initial_events)
    
    # Create 3 new events
    for i in range(3):
        client.post("/api/events", json={
            "title": f"Test Event {i}",
            "location": "Test Location",
            "host_id": host_id,
            "is_public": True
        })
    
    # Verify count increased by 3
    final_events = client.get("/api/events").json()
    final_count = len(final_events)
    assert final_count == initial_count + 3


@pytest.mark.api
def test_admin_user_count_accuracy(client):
    """Test that admin dashboard shows accurate user counts."""
    # Get initial user count
    initial_users = client.get("/api/user").json()
    initial_count = len(initial_users)
    
    # Create 3 new users
    for i in range(3):
        client.post("/api/users", json={
            "name": f"Test User {i}",
            "email": f"testuser-{i}-{uuid.uuid4()}@example.com",
            "password": "pass",
            "role": "attendee"
        })
    
    # Verify count increased by 3
    final_users = client.get("/api/user").json()
    final_count = len(final_users)
    assert final_count == initial_count + 3
