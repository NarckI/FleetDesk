# FleetDesk
### An Integrated Driver, Vehicle, and Rent Management System
#### Developed for Megamiths Taxi Rental Services

> FleetDesk is a fully offline, web-based fleet management system built exclusively for **Megamiths**. It is designed to be the company's central platform for managing drivers, vehicles, rental contracts, daily payments, vehicle repairs, and automated expiration monitoring — replacing manual and paper-based processes with a reliable, organized digital system.

![Python](https://img.shields.io/badge/Python-Django-green?style=flat-square&logo=python)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue?style=flat-square&logo=postgresql)
![Bootstrap](https://img.shields.io/badge/UI-Bootstrap%205-purple?style=flat-square&logo=bootstrap)
![Offline](https://img.shields.io/badge/Mode-Fully%20Offline-gray?style=flat-square)
![Access](https://img.shields.io/badge/Access-Admin%20Only-red?style=flat-square)

---

## 📌 Table of Contents

- [About the System](#about-the-system)
- [Who This Is For](#who-this-is-for)
- [System Modules](#system-modules)
- [Business Rules](#business-rules)
- [Technology Stack](#technology-stack)
- [Database Design](#database-design)
- [Installation & Setup Guide](#installation--setup-guide)
- [Daily Automation](#daily-automation)
- [Pages & Routes](#pages--routes)
- [Project Structure](#project-structure)
- [Known Limitations & Future Improvements](#known-limitations--future-improvements)
- [Development Team](#development-team)
- [Academic Context](#academic-context)
- [Disclaimer](#disclaimer)

---

## About the System

**FleetDesk** is a custom-built fleet management system developed specifically for **Megamiths**, a taxi rental company. The system was built as part of an academic information systems project by second-year BSIS students at Cebu Technological University (CTU) Main Campus, in direct response to the operational needs of the company.

The system addresses the following real business needs of Megamiths:

- Maintaining an organized and verifiable record of drivers and their credentials
- Tracking all vehicles in the fleet including registration and compliance documents
- Managing rental contracts between the company and its drivers
- Automating daily payment generation and monitoring collections
- Logging vehicle repairs with full accountability to the responsible driver
- Receiving timely alerts before licenses, permits, and contracts expire

FleetDesk is deployed and intended for active, day-to-day use by the Megamiths administrator.

---

## Who This Is For

This system is built for and handed over to **Megamiths** for operational use. It is accessed exclusively by the designated **system administrator** of the company.

If you are the Megamiths administrator reading this:

- Follow the [Installation & Setup Guide](#installation--setup-guide) to get the system running on your computer
- Run the [Daily Automation](#daily-automation) command every day (or set it up to run automatically at midnight)
- Use the [Pages & Routes](#pages--routes) section as a quick reference for navigating the system
- Contact the development team for any technical issues during the initial deployment period

---

## System Modules

### 🗂️ Dashboard
- Central overview of all company operations at a glance
- Summary of active contracts, payment status, vehicle availability, and pending alerts
- Designed to give the admin an immediate picture of the business every time they log in

### 👤 Drivers
- Register and manage all driver profiles in the company
- Store complete demographic information for each driver
- Record driver's license number and expiry date to ensure all drivers are legally qualified to operate company vehicles
- Track the date each driver was added to the system for record-keeping
- Drivers currently under an active contract are automatically locked out of the contract driver selector to prevent duplicate assignments

### 🚗 Vehicles
- Maintain a complete registry of all Megamiths fleet vehicles
- Store the following per vehicle:
  - Plate number, Official Receipt (OR), Certificate of Public Convenience (CPC) expiry
  - Vehicle type, brand, model, and manufacturing year
  - Current mileage and last maintenance date
  - Availability status: **Available**, **In-Use**, or **Maintenance**
- Flag any vehicle for repair directly from this section
- Flagging a vehicle for repair automatically updates its status to **Maintenance** across the system
- Vehicles that are In-Use or under Maintenance are excluded from the contract vehicle selector

### 📄 Contracts
- Create and manage rental contracts between Megamiths and its drivers
- Each contract records:
  - The assigned driver and vehicle
  - Contract status: **Active** or **Inactive**
  - Daily rental rate
  - Contract start date and end date
- Supports full editing and deletion of contract records
- Contract data is referenced across the system — particularly in the Repairs module to identify which driver was operating a vehicle at the time of a breakdown
- **Terminated contracts are locked** and cannot be modified to protect record integrity
- Contracts that have passed their end date are automatically expired by the daily automation task

### 💳 Payments
- View a real-time financial summary showing:
  - **Total Payments** collected to date
  - **Total Pending** payments outstanding
  - **Overdue** payments past their due date
- Payments are **automatically generated every day** for each active contract based on the agreed daily rate — no manual entry needed
- Supports both **full payment** and **partial payment**:
  - Partial payments display the updated running balance after each transaction
  - Partial payments accumulate until the full amount is settled, at which point the record is automatically marked **Paid**
- Admin can manually mark any payment as **Paid** when cash is collected
- Overdue payments are automatically flagged by the daily automation task

### 🔧 Repairs
- Repair records are automatically created when a vehicle is flagged for repair from the Vehicles section
- The system pulls driver identity from the active contract to establish accountability for the breakdown
- Admin fills in the following repair details:
  - Repair status: **Pending** or **Completed**
  - Repair type (selected from pre-loaded checkboxes — no manual typing required)
  - Repair cost, shop name, and date of completion
  - Additional notes for detailed documentation
- **Printable repair receipts** can be generated for all completed repairs
- Marking a repair as Completed automatically restores the vehicle's status to **Available** or **In-Use**
- All status changes are immediately reflected across the relevant sections of the system

### 🔔 Notifications
- Fully automated alert system requiring no manual setup from the admin
- Three alert categories:
  - **Payment Alerts** — notifies the admin of overdue and upcoming payment dues
  - **Expiration Alerts** — alerts the admin **14 days** and **7 days** before the expiry of driver licenses, OR, CR, and CPC documents
  - **Total Alerts** — shows the combined count of all active alerts that need attention
- All notifications are generated automatically by the daily automation command

---

## Business Rules

The following rules govern how the system behaves to protect data accuracy and business integrity:

| Rule | System Behavior |
|---|---|
| Terminated contracts | Locked from editing once marked terminated |
| Vehicle selector | In-Use and Maintenance vehicles are excluded |
| Driver selector | Drivers with active contracts are excluded |
| Flagging a vehicle for repair | Automatically sets status to **Maintenance** |
| Completing a repair | Automatically restores status to **Available** or **In-Use** |
| Payment generation | Auto-generated daily for every active contract |
| Partial payments | Accumulate until the full balance is cleared |
| Expiry notifications | Triggered at 14 days and 7 days before expiry |
| Contract auto-expiry | Contracts past their end date are automatically expired |
| Status interconnectivity | All status changes are reflected system-wide in real time |

---

## Technology Stack

| Layer | Technology |
|---|---|
| Backend Framework | Python / Django |
| Frontend UI | Bootstrap 5 |
| Database | PostgreSQL |
| Deployment Mode | Fully Offline (Local Network) |
| UI/UX Prototyping | Figma |
| ERD Design | Mermaid / draw.io |
| Version Control | Git / GitHub |

---

## Database Design

The system uses a relational database with the following core entities:

- **Driver** — demographics, license number, license expiry, date added
- **Vehicle** — plate number, OR, CR, CPC expiry, type, brand, model, year, mileage, last maintenance, status
- **Contract** — driver-vehicle assignment, daily rate, start/end date, status
- **Payment** — amount due, amount paid, running balance, payment date, status
- **Repair** — vehicle reference, driver (via contract), repair types, cost, shop name, date finished, status, notes
- **Notification** — alert type, reference record, trigger date, status

> Full ERD and data dictionary are available in the `/docs` folder.

---

## Installation & Setup Guide

> This guide is intended for the **Megamiths system administrator** or the assigned technical person setting up FleetDesk on the company computer.

### Prerequisites
Before starting, make sure the following are installed on the computer:
- [Python 3.x](https://www.python.org/downloads/)
- [PostgreSQL](https://www.postgresql.org/download/)
- [Git](https://git-scm.com/)

---

### Step 1 — Get the project files
```bash
git clone https://github.com/your-username/fleetdesk.git
cd fleetdesk
```

### Step 2 — Install required Python packages
```bash
pip install -r requirements.txt
```

### Step 3 — Set up the PostgreSQL database
Open your PostgreSQL terminal and run:
```sql
CREATE DATABASE fleetdesk;
CREATE USER fleetdesk_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE fleetdesk TO fleetdesk_user;
```

### Step 4 — Configure database connection
Edit `config/settings.py` or set the following environment variables:
```bash
export DB_NAME=fleetdesk
export DB_USER=fleetdesk_user
export DB_PASSWORD=yourpassword
export DB_HOST=localhost
export DB_PORT=5432
```

### Step 5 — Run database migrations
```bash
python manage.py migrate
```

### Step 6 — Create the admin account
```bash
python manage.py setup_admin
# Default login — Username: admin | Password: admin123
```
> ⚠️ **Important:** Change the default password immediately after first login.

### Step 7 — Collect static files
```bash
python manage.py collectstatic
```

### Step 8 — Start the system
```bash
python manage.py runserver
```
Then open your browser and go to:
```
http://localhost:8000
```

---

## Daily Automation

> **This step is critical for the system to function correctly.** The daily automation task handles payment generation, overdue flagging, contract expiry, and notification alerts automatically.

### Option A — Run manually every day
```bash
cd /path/to/fleetdesk
python manage.py run_daily_tasks
```

### Option B — Set up automatic daily execution (recommended)
Schedule it to run at midnight using cron:
```bash
# Open crontab
crontab -e

# Add this line
0 0 * * * cd /path/to/fleetdesk && python manage.py run_daily_tasks
```

### What this command does every day:

| Task | Description |
|---|---|
| Contract expiry | Automatically expires contracts past their end date |
| Overdue payments | Flags all unpaid payments past their due date |
| Daily payment logs | Generates one payment record per active contract |
| Expiry notifications | Creates alerts at 14 days and 7 days before license, OR, CR, and CPC expiry |

---

## Pages & Routes

| URL | Page |
|---|---|
| `/` | Dashboard |
| `/login/` | Login |
| `/drivers/` | Driver Management |
| `/vehicles/` | Vehicle Management |
| `/contracts/` | Contract Management |
| `/payments/` | Payment & Collections |
| `/repairs/` | Repair Logs |
| `/notifications/` | Notifications |
| `/admin/` | Django Admin Panel |

---

## Project Structure

```
fleetdesk/
├── config/
│   └── settings.py             # Project settings and database configuration
├── drivers/                    # Driver management module
├── vehicles/                   # Vehicle management module
├── contracts/                  # Contract management module
├── payments/                   # Payment tracking module
├── repairs/                    # Repair logging module
├── notifications/              # Notification center module
├── management/
│   └── commands/
│       ├── run_daily_tasks.py  # Daily automation command
│       └── setup_admin.py      # Admin account setup command
├── templates/                  # HTML templates (Bootstrap 5)
├── static/                     # CSS, JS, and image assets
├── docs/
│   ├── ERD.png                 # Entity-relationship diagram
│   └── data_dictionary.pdf     # Data dictionary
├── manage.py
└── requirements.txt
```

---

## Known Limitations & Future Improvements

The following limitations were identified during development. These are recommended for the next phase of the system:

| Current Limitation | Recommended Improvement |
|---|---|
| Admin-only access | Implement role-based access control (RBAC) — Super Admin and Staff/Viewer roles |
| No payment schedule preview | Auto-display the full payment timeline when a contract is created |
| No audit trail | Add an activity log to track all changes with timestamps for accountability |
| No report export | Add PDF and Excel export for payment collections, contract summaries, and repair records |
| Repair cost not linked to payments | Add a "Charge to Driver" option to add repair costs as a payable item in the driver's account |

---

## Development Team

| Name | Role | Module Focus |
|---|---|---|
| Demecillo | Team Leader / Backend Developer | Contracts & Payments |
| Almacen | Database Designer | Vehicles & Drivers |
| Torres | Frontend Developer | UI/UX & Notifications |
| Binondo | Documentation & QA | Repairs & Testing |

For technical concerns during deployment, please contact the development team through Cebu Technological University — BSIS Department.

---

## Academic Context

This system was developed as a capstone course requirement under the Bachelor of Science in Information Systems program.

| | |
|---|---|
| **Institution** | Cebu Technological University (CTU) Main Campus |
| **Program** | Bachelor of Science in Information Systems (BSIS) |
| **Year Level** | 2nd Year |
| **Subject** | [Subject Code & Name] |
| **Instructor** | [Instructor's Name] |
| **School Year** | A.Y. 2024–2025 |
| **Client Company** | Megamiths Taxi Rental Services |

---

## Disclaimer

FleetDesk was developed as an academic project by BSIS students of Cebu Technological University for **Megamiths Taxi Rental Services**. The system is intended for the company's operational use and serves as the basis for the **Certificate of Utilization** issued to verify actual deployment and use by the client. The development team does not assume liability for any business decisions made based on the system's output. All development was conducted in good faith to address the genuine operational needs of the company.

---

<p align="center">
  Developed by BSIS 2nd Year Students &nbsp;•&nbsp; Cebu Technological University Main Campus &nbsp;•&nbsp; A.Y. 2024–2025<br/>
  <b>Client:</b> Megamiths Taxi Rental Services
</p>
