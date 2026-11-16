# Civic-Connect-Management-System
## Government Public Service Management System

Civic Connect is a complaint filing and public service management system, built
as a B.Tech third-year academic project prototype with Python, Flask, MySQL,
HTML, CSS, and JavaScript.

## Features

- Citizen registration and login
- Complaint submission and tracking
- Officer complaint assignment and status updates
- Admin dashboard
- Department, officer, and resource management
- Complaint statistics and reports
- CPU scheduling simulations: FCFS, Priority, and Round Robin
- Banker's safety algorithm
- Deadlock detection
- Synchronization demonstration using a mutex
- IPC demonstration using a producer-consumer queue

## Requirements

- Python 3.10 or newer
- MySQL 8 or newer
- pip
- A browser and a code editor such as VS Code

## Installation

1. Create and activate a virtual environment:

   Windows PowerShell:

   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

   Linux/macOS:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install the packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env`. Update the MySQL username, password,
   database name, and Flask secret key.

4. Create the database and sample departments:

   ```bash
   mysql -u root -p < database/schema.sql
   mysql -u root -p < database/seed.sql
   ```

5. Start the application:

   ```bash
   python app.py
   ```

6. Visit `http://127.0.0.1:5000`.

## Creating the first admin

Register an account using the website. Then, in your local MySQL development
database, promote that account to admin by running the following statement
with the email address you registered:

```sql
USE civic_connect;
UPDATE users SET role = 'admin' WHERE email = 'your-email@example.com';
```

Log out and sign in again so the updated role is loaded into your session.

Use this only in your local development database. Do not expose admin
promotion as a public feature.

## Running tests

From the project root:

```bash
pytest -q
```

## Database tables

- `users`: citizen, officer, and admin accounts
- `departments`: public service departments
- `employees`: officer-to-department mapping
- `complaints`: complaint records and workflow status
- `resources`: department resource quantities

## Notes

- This is an educational prototype, not a production government system.
- Use a strong random secret key and keep `.env` private.
- Before production deployment, add CSRF protection, rate limiting,
  audit logs, stronger input validation, and secure deployment settings.
- The scheduling and resource algorithms are teaching demonstrations.
- The IPC module demonstrates an in-process producer-consumer queue; it is
  not an operating-system process communication implementation.
