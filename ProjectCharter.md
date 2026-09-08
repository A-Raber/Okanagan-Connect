# Project Charter

## Identification
Project Name: OkanaganConnect
Charter Version 1.0 - September, 15, 2025
Sponsor Name: Patricia Lasserre
Project Managers: Gabriel Traas, Dan Williams, Ashton Raber

## Overview of the Project
OkanaganConnect is a program to help people keep their events organized.  Running an event can be very complicated, having to track down all the vendors needed can be daunting, and having a one stop solution greatly improves event organizers abilities to run an event. This project also tackles another major problem for people hosting events, namely making the event known to others. 

## Project Objective
The objective of the OkanaganConnect project is to deliver a fully functional Event Portal by December 5, 2025 that enables hosts, vendors, and attendees to organize and participate in events through a centralized platform. The platform will launch with at least 10 upcoming events listed, demonstrating adoption and usability, and will ensure that all core event workflows, including publishing, discovering, and RSVPing, function reliably with 100% successful end-to-end testing before release. To meet user expectations, search and RSVP actions will be completed within two seconds under normal load, and the system will be designed to scale to 1,000 concurrent users without requiring a major redesign, ensuring long-term sustainability and stakeholder confidence.

## Business Needs or Opportunities
Event information and vendor coordination in the Okanagan is currently fragmented across posters, group chats, and emails. This makes it difficult for attendees to discover events and for hosts to organize them efficiently. OkanaganConnect addresses these challenges by providing:

Centralized discovery: A single, searchable directory, improving attendance and event awareness.
Organizer efficiency: Simple publishing tools and RSVP counts reduce planning overhead and errors. 
Vendor visibility: A way for service providers to connect with hosts, supporting more efficient event planning and benefiting local businesses.
Community & safety: Optional group meetups and introductions that reduce social friction, with moderation features to maintain quality and trust.

## Scope 
### Minimum Viable Project Requirements
Deliver a campus Event Portal where Hosts publish events, Attendees discover & RSVP, and Vendors connect with Hosts.
Have 10+ upcoming events listed on the website.  
Include 4 role based access controls: Host, Attendee, Vendor, Admin.
All typical user workflows are tested including account creation, event creation, event discovery, event attendance, and vendor connection.
That search and RSVP actions complete within 2 seconds under normal load, meeting user performance expectations.
Design the platform to scale up to 1,000 concurrent users without requiring a major system redesign.
Vendors must apply for vendor status.
Events can be listed as private or public.
Hosts can add tags to events based on categories.
Calendar and Map integration.
Featured Events/ Personalized event suggestions.

### Out of Scope Objectives
Payment processing
Mobile development / application development.
Vendor and Host Quotes.
Real time chat.

## Key Stakeholder Summary
### Stakeholder identification:
Project Sponsor: Provides overall direction for the project (TA / Professor).
Event Attendees: The majority of the users of the platform, and the ones that will RSVP for events.
Event Hosts: Primary users creating and managing events on the platform.
Vendors: Users seeking to advertise or sell their services to Event Hosts.
Admins: Ensures the website stays running and conducts maintenance.
Development Team: Designers, developers and testers responsible for building and validating the portal.
### Stakeholder Needs:
Project Sponsor
Wants the project delivered on time.
Wants the project delivered within budget.
Wants the project delivered will all requested features, and as many additional ones as possible.
Wants risk to be managed and mitigated wherever possible.
Wants frequent progress reports or documentation.

Event Attendees
Require a bug/frustration free product.
Wants to easily sign up for events.
Wants to be aware of events they may want to attend.
Wants secure handling of login/private information.

Event Hosts
Wants a simple to set up and easy to update manager.
Wants to be able to easily fill in required vendors.
Wants secure handling of login, private information and event access.

Vendors
Wants to sell services to as many hosts as possible.
Wants the visibility/marketing opportunities.
Wants ability to grow a platform or reputation on the website.



Admins
Need reliable monitoring tools to ensure the platform is consistently operational.
Want clear processes for identifying and resolving issues quickly.
Need secure access controls to perform administrative tasks safely.
Desire scalability and flexibility in the system to support future growth.
Want documentation and logs to assist with troubleshooting and system audits.

Development Team
Want clear, prioritized requirements to guide design and implementation.
Need ongoing communication with the sponsor and stakeholders to clarify goals.
Require access to appropriate tools, frameworks, and environments for development and testing.
Want timely feedback during testing and review cycles.
Desire recognition of effort and support for continuous improvement.


## Project Milestones
Project Charter is Completed
Stakeholder identification.
User needs identified.
Objectives agreed upon.
Degree of Scope decided.
Charter approved.

Project Design Phase Complete
Wireframe is made and agreed upon.
Graphical design conventions (colour, font, etc. agreed upon).
Database application and hosting platform agreed upon.
Risk identification begins.

Prototype Creation Phase
Basic Prototype (paper, slideshow, etc) created as a demonstration for users and developers.
Basic UI made and ready to implement.
Risk identification/mitigation is ongoing.

Core Functionality Delivered
Minimum Viable Project objectives complete.
Feasible optional objectives identified, but not yet implemented .
Risk identification/mitigation is ongoing.

Testing and Finalisation Phase Complete
Testing and bug fixing performed.
Feasible optional objectives implemented and bug fixing performed.
Risk mitigation is complete.

Product is launched
Project is made available to users (submitted to class).
Maintenance would begin if required by the project sponsor.
Last team meeting is held to discuss project closing and document lessons learned.

## Major Deliverables
Project Charter: Approved document defining objectives, scope, stakeholders, and constraints. Delivered after the team formation milestone.
Work Plan / WBS: An organized breakdown of tasks, schedule, and resources to meet objectives.
Technical Spec: Data model, role/permission matrix, key API endpoints, acceptance criteria
Documentation: User guide for each role, moderation policy, AI use disclosure, developer README
MVP Application: Deployed web app with core in-scope features, seeded data, and tested user workflows for all common tasks on the site including event creation, event signup, vendor connection.
Final Report & Presentation: Summarizing objectives, process, results, risks, and lessons learned.
Finished Application: Final application, with any stretch objectives that were achieved. Delivered alongside the final presentation.

## Assumptions
Team Availability: Team members will contribute approximately 5 hours per week outside scheduled labs and will attend group meetings as planned.
Seed Content: Sufficient demo events and vendor/host data will be available to populate the Event Portal for demonstrations.
Infrastructure: Basic hosting (e.g., local Docker or school-provided VM) and email capability will be available for deployment.
Stakeholder Support: Instructor/TA will provide timely feedback on milestones and act as an effective project sponsor with the authority to approve or reject changes.
Tool Usage: Use of AI-assisted tools for scaffolding and copywriting is permitted, provided all outputs undergo human review in compliance with course policy.
Traffic Levels: The platform will only need to support moderate traffic (classroom and demo scale); no horizontal scaling is required.
Instructor/TA acts as an effective sponsor with authority to approve/reject changes.
Database Reliability: The database will support simultaneous use by multiple users without data corruption or input conflicts.
Project Environment Stability: Required development tools, frameworks, and school-provided infrastructure will remain stable and available throughout the project timeline.

## Constraints
Time Constraint: The MVP must be fully developed, tested, and demo-ready by December 5, 2025.
Resource Constraint: The project will be delivered by a small team, limiting the number of features that can be included. Additional features will only be considered if extra resources become available.
Technical Constraint: Development must be completed on a web-based platform, leveraging existing frameworks and technologies approved for campus use.
Knowledge Constraint: The project team has limited expertise in advanced integrations (e.g., calendar APIs, personalization algorithms), which may restrict stretch objectives.
Testing Constraint: Testing will be limited to internal stakeholders and a small pilot group, which may not fully reflect all real-world usage scenarios.
Budget Constraint: The project is assumed to operate with minimal budget and relies primarily on existing personnel and tools. Paid contractors or premium services are not expected to be available.


Disclosure: We used AI (ChatGPT) to brainstorm ideas, organize the brief, and polish wording. All decisions, structure, and final content were created, reviewed, and approved by us.
