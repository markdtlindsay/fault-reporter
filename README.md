# Fault Reporter

Fault Reporter is a lightweight web application built with Flask that allows users to submit and manage building maintenance issues. The system supports role-based actions for standard users and administrators and demonstrates core principles of Agile software development.

## Features

- User login and session tracking using Flask-Login
- Submission of building faults with title, description, location, and status
- Admin-only functionality to delete faults and create new users
- Support for marking faults as closed (with automatic close date)
- Fault and user data stored in a relational SQLite database
- All forms (Add Fault, Add User) presented in responsive Bootstrap modals
- UK-style date formatting using Jinja filters
- Clean, Bootstrap-based interface for usability and visual clarity

## Technologies

- Python 3.10
- Flask
- Flask-Login
- SQLite (accessed via `sqlite3`)
- HTML, CSS (Jinja2 templating + Bootstrap 5)

## Getting Started

These steps assume you have Python 3.10+ installed.

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/fault-reporter.git
cd fault-reporter
```

### 2. Create and activate a virtual environment (Windows)

```bash
python -m venv venv
venv\Scripts\activate
```

> On macOS/Linux, use:  
> `source venv/bin/activate`

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Database Setup

The application can create the SQLite database (`app.db`) automatically on first run using the `schema.sql` file and preloaded data.

Alternatively, a prebuilt `app.db` file is included in the repository for convenience.

### Option 1: Auto-create on first run (recommended)

If `app.db` does not exist, the application will:
- Execute `schema.sql` to define the database structure
- Insert 10 users and 10 fault records

This requires no manual action — the app will be ready to use once started.

### Option 2: Use the prebuilt `app.db`

The repository includes a working database with test data. You can run the app immediately without triggering auto-creation.

To reset or recreate the database manually:
1. Delete the existing `app.db`
2. Run the app and it will rebuild using `schema.sql` (Option 1)

### 5. Run the application

```bash
flask run
```

Visit [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

## Project Structure

### Folders

- `diagrams/`: Entity Relationship Diagram
- `screenshots/`: Annotated screenshots of the application
- `templates/`: Jinja2 HTML templates
- `tests/`: Basic automated tests using `pytest`

### Files

- `.gitignore`: Specifies intentionally untracked files (e.g., `venv/`, `app.db`)
- `app.py`: Main Flask application logic
- `Procfile`: Specifies start command for deployment on Render
- `requirements.txt`: Lists required Python packages
- `schema.sql`: SQL script to initialise the database

## ERD

The Entity Relationship Diagram is located at `/diagrams/FaultReporterERD.png`.

It shows the structure and relationships between the two main tables:

- `users`: stores user credentials, names, and roles
- `faults`: stores fault reports, including submitter, optional closer, and closure date

The diagram reflects:
- A mandatory many-to-one relationship between `faults.submitted_by` and `users.id`
- An optional many-to-one relationship between `faults.closed_by` and `users.id`
- Timestamps for `date_created` and `date_closed`

![ERD](diagrams/FaultReporterERD.png)

## Screenshots

Key screenshots are located in the `/screenshots/` folder, including:

- **Login form** – `01_login.png`
- **Fault list for regular user showing open and closed faults** – `02_home_user.png`
- **Modal for submitting a fault** – `03_submit_modal.png`
- **Admin view showing delete buttons and “Add New User” button** – `04_admin_buttons.png`
- **Modal for adding a user** – `05_add_user_modal.png`

## Testing

Basic route-level tests are included in `tests/test_routes.py`, using `pytest`.

To run the tests:

```bash
pip install -r requirements.txt
pytest
```

These tests verify that key routes behave correctly (e.g. homepage redirects unauthenticated users, login page loads as expected).

## Deployment

This application is deployed online via [Render](https://render.com) using the free tier:

**Live App**: [https://fault-reporter.onrender.com](https://fault-reporter.onrender.com)

**Note**:  
Render’s free plan automatically suspends the application after 15 minutes of inactivity.  
The first request may take 30–60 seconds to load while the service "wakes up."  
Please be patient, the app will load shortly.

## Notes

This application was created for a Level 5 Software Engineering and Agile module. It demonstrates:

- CRUD operations across users and faults
- Flask routing and database integration
- Secure authentication and role-based access
- Use of version control (Git/GitHub)
- Bootstrap 5 for responsive design
- Jinja templating and date formatting