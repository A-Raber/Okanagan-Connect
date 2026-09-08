from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select, func
from sqlalchemy.exc import IntegrityError
from pathlib import Path
from backend.DB.database import engine, create_db_and_tables
from backend.DB.models import Event, User, RSVP  # ensure models are imported
from datetime import datetime
from contextlib import asynccontextmanager

def _iso(dt: datetime | None):
    return dt.isoformat() if dt else None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ✅ runs once on startup
    create_db_and_tables()
    yield
    # ✅ optional: runs once on shutdown
    print("Server stopped")

app = FastAPI(title="OkanaganConnect API (dev)", lifespan=lifespan)

# allow frontend to fetch from backend during dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/events")
def list_events():
    with Session(engine) as session:
        # Get events with RSVP counts
        rows = session.exec(select(Event)).all()
        
        result = []
        for e in rows:
            # Count RSVPs for this event
            rsvp_count = session.exec(
                select(func.count(RSVP.id)).where(RSVP.event_id == e.id)
            ).one()
            
            result.append({
                "id": e.id,
                "title": e.title,
                "location": e.location or "",
                "description": e.description or "",
                "time": _iso(e.time),
                "cost": e.cost or "",
                "image": e.url or "",
                "is_public": e.is_public,
                "host_id": e.host_id,
                "rsvp_count": rsvp_count
            })
        
        return result
    
@app.get("/api/user")
def list_users():
    with Session(engine) as session:
        rows = session.exec(select(User)).all()
        return [
            {
                "id": e.id,
                "name": e.name,
                "email": e.email or "",
                "password": e.hashed_password or "",
                "role": e.role or ""
            }
            for e in rows
        ]

@app.get("/api/user/{user_id}/can-delete")
def can_delete_user(user_id: int):
    """Check if a user can be deleted (prevents deleting last admin)"""
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # If user is admin, check if they're the last one
        if user.role == "admin":
            admin_count = session.exec(
                select(func.count(User.id)).where(User.role == "admin")
            ).one()
            
            if admin_count <= 1:
                return {
                    "can_delete": False,
                    "reason": "Cannot delete the last admin account"
                }
        
        return {"can_delete": True}
    
@app.delete("/api/user/{user_id}")
def delete_user(user_id: int):
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Prevent deleting last admin
        if user.role == "admin":
            admin_count = session.exec(
                select(func.count(User.id)).where(User.role == "admin")
            ).one()
            
            if admin_count <= 1:
                raise HTTPException(
                    status_code=403,
                    detail="Cannot delete the last admin account"
                )
        
        # Delete all events for that user (Tried to do cascade but has problems)
        events = session.exec(select(Event).where(Event.host_id == user_id)).all()
        for e in events:
            session.delete(e)

        session.delete(user)
        session.commit()
        return {"message": f"User with ID {user_id} deleted successfully"}

@app.put("/api/user/{user_id}/password")
def change_password(user_id: int, payload: dict):
    """Change user password. Requires current_password and new_password."""
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        current_password = payload.get("current_password")
        new_password = payload.get("new_password")
        
        if not current_password or not new_password:
            raise HTTPException(
                status_code=400,
                detail="Both current_password and new_password are required"
            )
        
        # Verify current password (note: passwords stored as plaintext in demo)
        if user.hashed_password != current_password:
            raise HTTPException(
                status_code=401,
                detail="Current password is incorrect"
            )
        
        # Update password
        user.hashed_password = new_password
        session.add(user)
        session.commit()
        
        return {"message": "Password updated successfully"}

@app.delete("/api/events/{event_id}")
def delete_event(event_id: int):
    with Session(engine) as session:
        event = session.get(Event, event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        session.delete(event)
        session.commit()
        return {"message": f"Event with ID {event_id} deleted successfully"}

# New endpoint to create a user
@app.post("/api/users", status_code=201)
def create_user(payload: dict):
    """
    Accepts JSON { name, email, role, password } and creates a User record.
    Returns created user's id and email.
    """
    name = payload.get("name")
    email = payload.get("email")
    role = payload.get("role", "attendee")
    password = payload.get("password")  # for demo only — hash in production!

    if not email or not password or not name:
        raise HTTPException(status_code=400, detail="name, email and password are required")

    # basic email uniqueness check
    with Session(engine) as session:
        existing = session.exec(select(User).where(User.email == email)).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already exists")

        user = User(name=name, email=email, role=role, hashed_password=password)
        session.add(user)
        session.commit()
        session.refresh(user)
        return {"id": user.id, "email": user.email, "name": user.name, "role": user.role}

@app.post("/api/login")
def login_user(payload: dict):
    """
    Accepts JSON { email, password } and returns success if credentials match.
    """
    email = payload.get("email")
    password = payload.get("password")

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()

        if not user or user.hashed_password != password:
            # For demo only — in production, use hashed passwords!
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Optional: return some user info (omit password)
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }

@app.post("/api/events", status_code=201)
def create_event(payload: dict):
    """
    Accepts JSON { title, description?, location?, time?, cost?, url?, is_public?, host_id }
    and creates an Event record. Returns created event with id.
    """
    title = payload.get("title")
    description = payload.get("description")
    location = payload.get("location")
    time = payload.get("time")
    cost = payload.get("cost")
    url = payload.get("url")
    is_public = payload.get("is_public", True)
    host_id = payload.get("host_id")

    if not title:
        raise HTTPException(status_code=400, detail="title is required")
    
    if not host_id:
        raise HTTPException(status_code=400, detail="host_id is required")

    # Parse time if provided as ISO string
    event_time = None
    if time:
        try:
            event_time = datetime.fromisoformat(time.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            raise HTTPException(status_code=400, detail="Invalid datetime format. Use ISO format (e.g., 2026-03-08T19:00:00)")

    with Session(engine) as session:
        # Verify host exists
        host = session.get(User, host_id)
        if not host:
            raise HTTPException(status_code=404, detail="Host user not found")
        
        # Check if host has appropriate role (optional validation)
        if host.role not in ["host", "admin"]:
            raise HTTPException(status_code=403, detail="User must be a host or admin to create events")

        event = Event(
            title=title,
            description=description,
            location=location,
            time=event_time,
            cost=cost,
            url=url,
            is_public=is_public,
            host_id=host_id
        )
        session.add(event)
        session.commit()
        session.refresh(event)
        
        return {
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "location": event.location,
            "time": _iso(event.time),
            "cost": event.cost,
            "image": event.url,
            "is_public": event.is_public,
            "host_id": event.host_id
        }

@app.put("/api/events/{event_id}")
def update_event(event_id: int, payload: dict):
    """
    Updates an existing event. Only the host who created it (or admin) should be able to update.
    Accepts partial updates - only provided fields will be updated.
    """
    with Session(engine) as session:
        event = session.get(Event, event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        # Update only provided fields
        if "title" in payload:
            event.title = payload["title"]
        if "description" in payload:
            event.description = payload["description"]
        if "location" in payload:
            event.location = payload["location"]
        if "cost" in payload:
            event.cost = payload["cost"]
        if "url" in payload:
            event.url = payload["url"]
        if "is_public" in payload:
            event.is_public = payload["is_public"]
        if "time" in payload:
            try:
                event.time = datetime.fromisoformat(payload["time"].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                raise HTTPException(status_code=400, detail="Invalid datetime format")
        
        session.add(event)
        session.commit()
        session.refresh(event)
        
        return {
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "location": event.location,
            "time": _iso(event.time),
            "cost": event.cost,
            "image": event.url,
            "is_public": event.is_public,
            "host_id": event.host_id
        }

# ============ RSVP Endpoints ============

@app.post("/api/rsvp", status_code=201)
def create_rsvp(payload: dict):
    """
    Create an RSVP for a user and event.
    Accepts JSON { user_id, event_id, status? }
    Returns created RSVP with id.
    """
    user_id = payload.get("user_id")
    event_id = payload.get("event_id")
    status = payload.get("status", "yes")
    
    if not user_id or not event_id:
        raise HTTPException(status_code=400, detail="user_id and event_id are required")
    
    with Session(engine) as session:
        # Verify user exists
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Verify event exists
        event = session.get(Event, event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        # Create RSVP
        rsvp = RSVP(user_id=user_id, event_id=event_id, status=status)
        session.add(rsvp)
        
        try:
            session.commit()
            session.refresh(rsvp)
        except IntegrityError:
            # Unique constraint violation - user already RSVP'd
            raise HTTPException(status_code=409, detail="Already RSVP'd to this event")
        
        return {
            "id": rsvp.id,
            "user_id": rsvp.user_id,
            "event_id": rsvp.event_id,
            "status": rsvp.status,
            "created_at": _iso(rsvp.created_at)
        }

@app.get("/api/rsvp/user/{user_id}")
def list_user_rsvps(user_id: int):
    """
    Get all RSVPs for a specific user with nested event data.
    Returns list of RSVPs with event details.
    """
    with Session(engine) as session:
        # Verify user exists
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get RSVPs with event data using relationship
        rsvps = session.exec(select(RSVP).where(RSVP.user_id == user_id)).all()
        
        result = []
        for rsvp in rsvps:
            # Use the relationship to get event data
            event = rsvp.event
            result.append({
                "id": rsvp.id,
                "user_id": rsvp.user_id,
                "event_id": rsvp.event_id,
                "status": rsvp.status,
                "created_at": _iso(rsvp.created_at),
                "event": {
                    "id": event.id,
                    "title": event.title,
                    "description": event.description or "",
                    "location": event.location or "",
                    "time": _iso(event.time),
                    "cost": event.cost or "",
                    "image": event.url or "",
                    "is_public": event.is_public,
                    "host_id": event.host_id
                } if event else None
            })
        
        return result

@app.delete("/api/rsvp/{rsvp_id}")
def cancel_rsvp(rsvp_id: int):
    """
    Cancel (delete) an RSVP by ID.
    """
    with Session(engine) as session:
        rsvp = session.get(RSVP, rsvp_id)
        if not rsvp:
            raise HTTPException(status_code=404, detail="RSVP not found")
        
        session.delete(rsvp)
        session.commit()
        
        return {"message": f"RSVP with ID {rsvp_id} cancelled successfully"}

# ============ End RSVP Endpoints ============

# ============ Admin Endpoints ============

@app.get("/api/admin/statistics")
def get_admin_statistics():
    """
    Get statistics for admin dashboard.
    Returns total events, total users, and total admins.
    """
    with Session(engine) as session:
        total_events = session.exec(select(func.count(Event.id))).one()
        total_users = session.exec(select(func.count(User.id))).one()
        total_admins = session.exec(
            select(func.count(User.id)).where(User.role == "admin")
        ).one()
        
        return {
            "total_events": total_events,
            "total_users": total_users,
            "total_admins": total_admins
        }

@app.get("/api/admin/events")
def get_admin_events():
    """
    Get all live (public) events for admin management.
    Returns events with RSVP counts, filtered to only public events.
    """
    with Session(engine) as session:
        # Get only public events
        events = session.exec(select(Event).where(Event.is_public == True)).all()
        
        result = []
        for e in events:
            # Count RSVPs for this event
            rsvp_count = session.exec(
                select(func.count(RSVP.id)).where(RSVP.event_id == e.id)
            ).one()
            
            result.append({
                "id": e.id,
                "title": e.title,
                "location": e.location or "",
                "description": e.description or "",
                "time": _iso(e.time),
                "cost": e.cost or "",
                "image": e.url or "",
                "is_public": e.is_public,
                "host_id": e.host_id,
                "rsvp_count": rsvp_count
            })
        
        return result

# ============ End Admin Endpoints ============

# Dev helper: seed a demo event if none exist
@app.post("/api/seed")
def seed_demo():
    with Session(engine) as session:
        first = session.exec(select(Event)).first()
        if first:
            return {"seeded": False, "reason": "events already exist"}
        
        # Create demo users: host and admin
        host = User(name="Demo Host", email="host@example.com", role="host", hashed_password="test")
        admin = User(name="Admin User", email="admin@example.com", role="admin", hashed_password="admin")
        session.add(host)
        session.add(admin)
        session.commit()
        session.refresh(host)
        session.refresh(admin)

        events = [
            Event(
                title="UBCO Games Club Meeting",
                description="Weekly meetup for board and tabletop gamers. Bring your favourite games, meet new players, and enjoy light snacks provided by the club.",
                location="UBCO Fipke 103",
                time=datetime.fromisoformat("2026-03-08T19:00:00"),
                cost="Free",
                host_id=host.id,
                is_public=True,
                url="https://images.unsplash.com/photo-1526498460520-4c246339dccb?auto=format&fit=crop&w=600&q=80"
            ),
            Event(
                title="AC/DC Tribute Night",
                description="Crank up the volume for a high-energy tribute to AC/DC. Local legends perform Highway to Hell, Thunderstruck, and more arena classics. Fans are encouraged to rock their favourite band tees.",
                location="Alex's Bar — Downtown Kelowna",
                time=datetime.fromisoformat("2026-04-03T20:00:00"),
                cost="$30",
                host_id=host.id,
                is_public=True,
                url="https://images.unsplash.com/photo-1507874457470-272b3c8d8ee2?auto=format&fit=crop&w=600&q=80"
            ),
            Event(
                title="Downtown Farmers Market",
                description="Shop fresh produce, artisan goods, and food trucks along the waterfront. Live acoustic sets throughout the morning and kid-friendly activities.",
                location="Waterfront Plaza — Downtown Kelowna",
                time=datetime.fromisoformat("2026-03-09T17:00:00"),
                cost="Free",
                host_id=host.id,
                is_public=True,
                url="https://images.unsplash.com/photo-1489515217757-5fd1be406fef?auto=format&fit=crop&w=900&q=80"
            ),
            Event(
                title="UBCO Engineering Capstone Showcase",
                description="Discover innovative senior projects from UBCO engineering students. Teams present their capstone designs, prototypes, and research findings. Network with future engineers and learn about cutting-edge campus technology.",
                location="UBCO Engineering Building",
                time=datetime.fromisoformat("2026-04-15T14:00:00"),
                cost="Free",
                host_id=host.id,
                is_public=True,
                url="https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=600&q=80"
            ),
            Event(
                title="Study Jam: Finals Week Prep",
                description="Beat the finals stress with group study sessions, free coffee, and tutoring support. Drop in anytime during the 6-hour block. Math, science, and writing tutors available.",
                location="UBCO Library Learning Commons",
                time=datetime.fromisoformat("2026-04-20T10:00:00"),
                cost="Free",
                host_id=host.id,
                is_public=True,
                url="https://images.unsplash.com/photo-1523050854058-8df90110c9f1?auto=format&fit=crop&w=600&q=80"
            ),
            Event(
                title="Okanagan Science Trivia Night",
                description="Test your knowledge of biology, chemistry, physics, and local ecology. Teams of 4 compete for prizes. Hosted by UBCO Science Students Association with themed rounds and bonus questions.",
                location="The Cambie Pub — Downtown Kelowna",
                time=datetime.fromisoformat("2026-03-12T19:30:00"),
                cost="$5 per person",
                host_id=host.id,
                is_public=True,
                url="https://images.unsplash.com/photo-1606326608606-aa0b62935f2b?auto=format&fit=crop&w=600&q=80"
            ),
            Event(
                title="Campus Mental Health Workshop",
                description="Learn evidence-based strategies for managing academic stress, building resilience, and supporting peers. Led by UBCO counseling services with interactive activities and resource handouts.",
                location="UBCO Arts Building Room 203",
                time=datetime.fromisoformat("2026-03-25T16:00:00"),
                cost="Free",
                host_id=host.id,
                is_public=True,
                url="https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?auto=format&fit=crop&w=600&q=80"
            ),
            Event(
                title="UBCO Outdoor Adventure Club Hike",
                description="Spring hike to Knox Mountain Summit with panoramic views of Kelowna and Okanagan Lake. All fitness levels welcome. Meet at campus before carpooling. Bring water, snacks, and sturdy footwear.",
                location="Knox Mountain Park Trailhead",
                time=datetime.fromisoformat("2026-03-29T09:00:00"),
                cost="Free",
                host_id=host.id,
                is_public=True,
                url="https://images.unsplash.com/photo-1551632811-561732d1e306?auto=format&fit=crop&w=600&q=80"
            ),
            Event(
                title="International Food Festival",
                description="Celebrate campus diversity with cuisine from 20+ countries. Student cultural clubs prepare traditional dishes. Live performances, language tables, and cultural displays throughout the afternoon.",
                location="UBCO Quad",
                time=datetime.fromisoformat("2026-04-10T12:00:00"),
                cost="$10 (all-you-can-taste)",
                host_id=host.id,
                is_public=True,
                url="https://images.unsplash.com/photo-1555939594-58d7cb561ad1?auto=format&fit=crop&w=600&q=80"
            ),
            Event(
                title="Coding Bootcamp: Intro to Python",
                description="Beginner-friendly workshop covering Python basics, data structures, and simple programs. Bring your laptop. No prior experience required. Led by Computer Science students and faculty.",
                location="UBCO Innovation Precinct",
                time=datetime.fromisoformat("2026-03-18T18:00:00"),
                cost="Free",
                host_id=host.id,
                is_public=True,
                url="https://images.unsplash.com/photo-1515879218367-8466d910aaa4?auto=format&fit=crop&w=600&q=80"
            ),
            Event(
                title="Career Fair: Tech & Innovation",
                description="Connect with 40+ employers seeking UBCO talent. Bring resumes for on-site interviews. Companies include local startups, national tech firms, and research labs. Business casual attire recommended.",
                location="UBCO Gymnasium",
                time=datetime.fromisoformat("2026-04-08T10:00:00"),
                cost="Free",
                host_id=host.id,
                is_public=True,
                url="https://images.unsplash.com/photo-1521737711867-e3b97375f902?auto=format&fit=crop&w=600&q=80"
            ),
            Event(
                title="Open Mic Night at The Well",
                description="Showcase your talent or support student performers. Musicians, poets, comedians, and storytellers welcome. Sign up starts at 7pm. Hosted by UBCO Arts Council with themed rounds.",
                location="The Well — UBCO Campus",
                time=datetime.fromisoformat("2026-03-27T19:00:00"),
                cost="Free",
                host_id=host.id,
                is_public=True,
                url="https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?auto=format&fit=crop&w=600&q=80"
            ),
            Event(
                title="Sustainability Summit 2026",
                description="Campus-wide conversation on climate action, waste reduction, and sustainable living. Keynote speakers, student research posters, and interactive workshops. Learn how to reduce your carbon footprint.",
                location="UBCO Administration Building Atrium",
                time=datetime.fromisoformat("2026-04-22T13:00:00"),
                cost="Free",
                host_id=host.id,
                is_public=True,
                url="https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?auto=format&fit=crop&w=600&q=80"
            )
        ]
        for e in events:
            session.add(e)

        session.commit()

        return {
            "seeded": True, 
            "event_ids": [e.id for e in events],
            "users": {
                "host": {"email": "host@example.com", "password": "test"},
                "admin": {"email": "admin@example.com", "password": "admin"}
            }
        }

# Serve frontend files at root (so GET / returns your frontend/index.html)
# path: project_root/backend/.. -> frontend folder
frontend_path = Path(__file__).resolve().parents[1] / "frontend"
if not frontend_path.exists():
    # safeguard: don't crash if path missing
    print("Warning: frontend folder not found at", frontend_path)
else:
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")
