"""Tests for FastAPI endpoints."""
import pytest
import uuid


@pytest.mark.api
def test_create_user(client):
    """Test user registration."""
    email = f"testuser-{uuid.uuid4()}@example.com"
    response = client.post("/api/users", json={
        "name": "Test User",
        "email": email,
        "password": "pass123",
        "role": "attendee"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == email
    assert "id" in data


@pytest.mark.api
def test_login(client):
    """Test user login."""
    email = f"login-{uuid.uuid4()}@example.com"
    # Create user first
    client.post("/api/users", json={
        "name": "Login User",
        "email": email,
        "password": "testpass",
        "role": "attendee"
    })
    
    # Test login
    response = client.post("/api/login", json={
        "email": email,
        "password": "testpass"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email


@pytest.mark.api
def test_list_events(client):
    """Test listing events."""
    response = client.get("/api/events")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.api
def test_create_event(client):
    """Test event creation by host."""
    email = f"host-{uuid.uuid4()}@example.com"
    # Create host user
    host_resp = client.post("/api/users", json={
        "name": "Event Host",
        "email": email,
        "password": "pass",
        "role": "host"
    })
    assert host_resp.status_code == 201
    host_id = host_resp.json()["id"]
    
    # Create event
    response = client.post("/api/events", json={
        "title": "Test Event",
        "location": "Test Location",
        "cost": "Free",
        "host_id": host_id
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Event"


@pytest.mark.api
def test_seed_endpoint(client):
    """Test seed creates demo data."""
    response = client.post("/api/seed")
    assert response.status_code == 200
    data = response.json()
    # Seed returns false if data already exists
    assert "seeded" in data


# ============ RSVP Tests ============

@pytest.mark.api
def test_create_rsvp(client):
    """Test RSVP creation."""
    # Create user
    user_email = f"rsvp-user-{uuid.uuid4()}@example.com"
    user_resp = client.post("/api/users", json={
        "name": "RSVP User",
        "email": user_email,
        "password": "pass",
        "role": "attendee"
    })
    user_id = user_resp.json()["id"]
    
    # Create host and event
    host_email = f"rsvp-host-{uuid.uuid4()}@example.com"
    host_resp = client.post("/api/users", json={
        "name": "RSVP Host",
        "email": host_email,
        "password": "pass",
        "role": "host"
    })
    host_id = host_resp.json()["id"]
    
    event_resp = client.post("/api/events", json={
        "title": "RSVP Test Event",
        "location": "Test Location",
        "host_id": host_id
    })
    event_id = event_resp.json()["id"]
    
    # Create RSVP
    rsvp_resp = client.post("/api/rsvp", json={
        "user_id": user_id,
        "event_id": event_id,
        "status": "yes"
    })
    
    assert rsvp_resp.status_code == 201
    rsvp_data = rsvp_resp.json()
    assert rsvp_data["user_id"] == user_id
    assert rsvp_data["event_id"] == event_id
    assert rsvp_data["status"] == "yes"
    assert "id" in rsvp_data


@pytest.mark.api
def test_duplicate_rsvp(client):
    """Test that duplicate RSVPs are rejected."""
    # Create user
    user_email = f"dup-user-{uuid.uuid4()}@example.com"
    user_resp = client.post("/api/users", json={
        "name": "Duplicate User",
        "email": user_email,
        "password": "pass",
        "role": "attendee"
    })
    user_id = user_resp.json()["id"]
    
    # Create host and event
    host_email = f"dup-host-{uuid.uuid4()}@example.com"
    host_resp = client.post("/api/users", json={
        "name": "Duplicate Host",
        "email": host_email,
        "password": "pass",
        "role": "host"
    })
    host_id = host_resp.json()["id"]
    
    event_resp = client.post("/api/events", json={
        "title": "Duplicate Test Event",
        "location": "Test Location",
        "host_id": host_id
    })
    event_id = event_resp.json()["id"]
    
    # Create first RSVP
    first_rsvp = client.post("/api/rsvp", json={
        "user_id": user_id,
        "event_id": event_id
    })
    assert first_rsvp.status_code == 201
    
    # Try to create duplicate RSVP
    duplicate_rsvp = client.post("/api/rsvp", json={
        "user_id": user_id,
        "event_id": event_id
    })
    assert duplicate_rsvp.status_code == 409
    assert "Already RSVP'd" in duplicate_rsvp.json()["detail"]


@pytest.mark.api
def test_list_user_rsvps(client):
    """Test listing user's RSVPs with event details."""
    # Create user
    user_email = f"list-user-{uuid.uuid4()}@example.com"
    user_resp = client.post("/api/users", json={
        "name": "List User",
        "email": user_email,
        "password": "pass",
        "role": "attendee"
    })
    user_id = user_resp.json()["id"]
    
    # Create host and two events
    host_email = f"list-host-{uuid.uuid4()}@example.com"
    host_resp = client.post("/api/users", json={
        "name": "List Host",
        "email": host_email,
        "password": "pass",
        "role": "host"
    })
    host_id = host_resp.json()["id"]
    
    event1_resp = client.post("/api/events", json={
        "title": "Event One",
        "location": "Location 1",
        "host_id": host_id
    })
    event1_id = event1_resp.json()["id"]
    
    event2_resp = client.post("/api/events", json={
        "title": "Event Two",
        "location": "Location 2",
        "host_id": host_id
    })
    event2_id = event2_resp.json()["id"]
    
    # Create RSVPs for both events
    client.post("/api/rsvp", json={"user_id": user_id, "event_id": event1_id})
    client.post("/api/rsvp", json={"user_id": user_id, "event_id": event2_id})
    
    # List user's RSVPs
    list_resp = client.get(f"/api/rsvp/user/{user_id}")
    assert list_resp.status_code == 200
    rsvps = list_resp.json()
    
    assert len(rsvps) == 2
    assert all("event" in rsvp for rsvp in rsvps)
    assert all("title" in rsvp["event"] for rsvp in rsvps)
    
    # Verify event data is nested
    event_titles = {rsvp["event"]["title"] for rsvp in rsvps}
    assert "Event One" in event_titles
    assert "Event Two" in event_titles


@pytest.mark.api
def test_cancel_rsvp(client):
    """Test RSVP cancellation."""
    # Create user
    user_email = f"cancel-user-{uuid.uuid4()}@example.com"
    user_resp = client.post("/api/users", json={
        "name": "Cancel User",
        "email": user_email,
        "password": "pass",
        "role": "attendee"
    })
    user_id = user_resp.json()["id"]
    
    # Create host and event
    host_email = f"cancel-host-{uuid.uuid4()}@example.com"
    host_resp = client.post("/api/users", json={
        "name": "Cancel Host",
        "email": host_email,
        "password": "pass",
        "role": "host"
    })
    host_id = host_resp.json()["id"]
    
    event_resp = client.post("/api/events", json={
        "title": "Cancel Test Event",
        "location": "Test Location",
        "host_id": host_id
    })
    event_id = event_resp.json()["id"]
    
    # Create RSVP
    rsvp_resp = client.post("/api/rsvp", json={
        "user_id": user_id,
        "event_id": event_id
    })
    rsvp_id = rsvp_resp.json()["id"]
    
    # Cancel RSVP
    delete_resp = client.delete(f"/api/rsvp/{rsvp_id}")
    assert delete_resp.status_code == 200
    assert "cancelled successfully" in delete_resp.json()["message"]
    
    # Verify RSVP is gone
    list_resp = client.get(f"/api/rsvp/user/{user_id}")
    assert len(list_resp.json()) == 0


@pytest.mark.api
def test_event_rsvp_count(client):
    """Test that events include RSVP count."""
    # Create host and event
    host_email = f"count-host-{uuid.uuid4()}@example.com"
    host_resp = client.post("/api/users", json={
        "name": "Count Host",
        "email": host_email,
        "password": "pass",
        "role": "host"
    })
    host_id = host_resp.json()["id"]
    
    event_resp = client.post("/api/events", json={
        "title": "Count Test Event",
        "location": "Test Location",
        "host_id": host_id
    })
    event_id = event_resp.json()["id"]
    
    # Create 3 users and RSVPs
    for i in range(3):
        user_email = f"count-user-{i}-{uuid.uuid4()}@example.com"
        user_resp = client.post("/api/users", json={
            "name": f"Count User {i}",
            "email": user_email,
            "password": "pass",
            "role": "attendee"
        })
        user_id = user_resp.json()["id"]
        client.post("/api/rsvp", json={"user_id": user_id, "event_id": event_id})
    
    # Get events and check RSVP count
    events_resp = client.get("/api/events")
    events = events_resp.json()
    
    # Find our event
    test_event = next((e for e in events if e["id"] == event_id), None)
    assert test_event is not None
    assert "rsvp_count" in test_event
    assert test_event["rsvp_count"] == 3


@pytest.mark.api
def test_rsvp_invalid_user(client):
    """Test RSVP with invalid user ID."""
    # Create host and event
    host_email = f"invalid-host-{uuid.uuid4()}@example.com"
    host_resp = client.post("/api/users", json={
        "name": "Invalid Host",
        "email": host_email,
        "password": "pass",
        "role": "host"
    })
    host_id = host_resp.json()["id"]
    
    event_resp = client.post("/api/events", json={
        "title": "Invalid Test Event",
        "location": "Test Location",
        "host_id": host_id
    })
    event_id = event_resp.json()["id"]
    
    # Try to create RSVP with non-existent user
    rsvp_resp = client.post("/api/rsvp", json={
        "user_id": 99999,
        "event_id": event_id
    })
    assert rsvp_resp.status_code == 404
    assert "User not found" in rsvp_resp.json()["detail"]


@pytest.mark.api
def test_rsvp_invalid_event(client):
    """Test RSVP with invalid event ID."""
    # Create user
    user_email = f"invalid-event-user-{uuid.uuid4()}@example.com"
    user_resp = client.post("/api/users", json={
        "name": "Invalid Event User",
        "email": user_email,
        "password": "pass",
        "role": "attendee"
    })
    user_id = user_resp.json()["id"]
    
    # Try to create RSVP with non-existent event
    rsvp_resp = client.post("/api/rsvp", json={
        "user_id": user_id,
        "event_id": 99999
    })
    assert rsvp_resp.status_code == 404
    assert "Event not found" in rsvp_resp.json()["detail"]

