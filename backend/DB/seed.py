from datetime import datetime
from sqlmodel import Session
from backend.DB.database import engine, create_db_and_tables
from backend.DB.models import User, Event

# ...existing code...


def create_host(session: Session, name: str, email: str, role: str = "host", hashed_password: str | None = None) -> User:
	
	# Create and return a User with role (default 'host').
	
	user = User(name=name, email=email, hashed_password=hashed_password, role=role)
	session.add(user)
	session.commit()
	session.refresh(user)
	return user

"""
def create_event(session: Session, title: str, host_id: int | None = None, description: str | None = None,
                 location: str | None = None, time=None, cost: str | None = None) -> Event:
	
	# Create and return an Event. `time` may be a datetime or ISO string.
	
	if isinstance(time, str):
		try:
			time = datetime.fromisoformat(time)
		except Exception:
			time = None

	ev = Event(title=title, description=description, location=location, location_detail=location,
	           time=time, cost=cost, host_id=host_id)
	session.add(ev)
	session.commit()
	session.refresh(ev)
	return ev
	"""
"""
if __name__ == "__main__":
	# convenience demo: create DB/tables and add one or more hosts + events
	create_db_and_tables()
	with Session(engine) as session:
		# create a host
		host = create_host(session, name="Demo Host", email="host@example.com")
		print("Created host:", host.id, host.email)

		# create first event for that host
		event1 = create_event(
			session,
			title="UBCO Games Club Meeting",
			host_id=host.id,
			time="2026-03-08T19:00:00",
			location="UBCO Fipke 103",
			cost="Free",
			description="Weekly meetup for board and tabletop gamers. Bring your favourite games, meet new players, and enjoy light snacks provided by the club."
		)
		print("Created event:", event1.id, event1.title)

		# create second event (add more as needed)
		event2 = create_event(
			session,
			title="Street Eats Festival",
			host_id=host.id,
			time="2026-03-09T17:00:00",
			location="Waterfront Promenade",
			cost="$5 entry",
			description="Taste bites from 20+ food trucks, sip craft sodas, and enjoy busker performances all evening. Family friendly."
		)
		print("Created event:", event2.id, event2.title)
"""