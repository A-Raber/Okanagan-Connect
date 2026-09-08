### Team Information
Team: L03_Scrum&Coke  
Members:  
- Dan Williams  
- Ashton Raber
- Gabriel Traas  
         
#### Overview of the Project
OkanaganConnect is a program to help people keep their events organized.  Running an event can be very complicated, 
having to track down all the vendors needed can be daunting, and having a one stop solution greatly improves event 
organizers abilities to run an event. This project also tackles another major problem for people hosting events, 
namely making the event known to others. 

### Project Scope
Minimum Viable Project Requirements
- Deliver a campus Event Portal where Hosts publish events, Attendees discover & RSVP, and Vendors connect with Hosts.
- Have 10+ upcoming events listed on the website.  
- Include 4 role based access controls: Host, Attendee, Vendor, Admin.
- 100% of “golden path” e2e tests pass (create → publish → discover → RSVP), meeting stakeholder requirements.
- MVP constrained to CRUD/search/RSVP/moderation.
- MVP completed and demo‑ready by Dec 5, 2025.
- That search and RSVP actions complete within 2 seconds under normal load, meeting user performance expectations.
- Design the platform to scale up to 1,000 concurrent users without requiring a major system redesign.

Optional Stretch Objectives
- Vendors must apply for vendor status.
- Events can be listed as private or public.
- Hosts can add tags to events based on categories.
- Calendar and Map integration.
- Featured Events/ Personalized event suggestions.

Out of Scope Objectives
- Payment processing.
- Mobile development / application development.
- Vendor and Host Quotes.
- Real time chat.

### Tech Stack, Database & Libraries 
- Python for the backend
- FastAPI for interface between front and backend
- SQLite for data storage


---

### Demo Video

[![Demo Video](https://img.youtube.com/vi/yCv7iBkRJnY/0.jpg)](https://youtu.be/yCv7iBkRJnY)


# Project Handover & Final Status Report

### Last Update for TAs

The OkanaganConnect project is nearly complete as of December 5, 2025. The Campus Event Portal is fully implemented, including both Host and Admin roles. Hosts can manage all aspects of their own events, including creating and updating event listings. Admins have full oversight of the platform, with the ability to manage users, review and remove events that violate the terms of service, and create new admin accounts.

Users can create accounts, update account details such as their password in settings, logout, and delete their profile if desired.

The system currently features 10+ upcoming events that can be inspected further by clicking on them, along with basic search and moderation tools. Manual testing was completed using pytest, as GitHub Actions was not enabled for our organization. Overall performance meets user expectations, and all code and stakeholder documentation are available in the main branch in Stakeholder_Communication.

### How to Run the Project

#### 1. Installing Dependencies
- **Python 3.13** (recommended)
- **FastAPI**
- **Uvicorn**
- **SQLModel**
- All dependencies are installed in a virtual environment located at `cosc305VE/`

**Create Virtual Environment (Windows):**
```powershell
python -m venv cosc305VE
```

**Setup Commands (Windows):**
```powershell
cosc305VE\Scripts\Activate
pip install -r requirements.txt
```
#### 2. Project Setup Steps (If you do not see any events listed when on Main Site do this)
- To manually set up or seed the database go to the API Docs and, use:
  - `POST /api/seed Seed Demo` "Try it out" and "Execute"

#### 3. Commands to Run the Project
From the project root, start the backend server:
```powershell
uvicorn backend.main:app --reload
```

#### 4. How to Access the Running App
- **API Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Main Site:** [http://127.0.0.1:8000](http://127.0.0.1:8000)

#### 5. Additional Notes
- No Docker or CI/CD setup
- All code and documentation are in the main branch
- Manual testing only; no automated test suite
- Example test credentials (if needed):
  - Host: `host@example.com` / password: `test`
  - Admin: `admin@example.com` / password: `admin`
- Note: There are no attendee or vendor accounts included because their pages were not completed, but you can still create new accounts with those roles.
