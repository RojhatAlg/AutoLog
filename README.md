# 🔧 Auto Parts Tracker

A self-hosted **vehicle maintenance tracking system** built with Flask and SQLite. It logs service history (oil changes, brake work, filters, inspections) per vehicle and automatically calculates when the next maintenance task is due, based on either vehicle-specific intervals or a reference catalog of manufacturer defaults.

> Server-rendered Flask application — no build step, no JS framework, runs anywhere Python runs.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Technologies Used](#2-technologies-used)
3. [Technical Skills Demonstrated](#3-technical-skills-demonstrated)
4. [Software Engineering Concepts](#4-software-engineering-concepts)
5. [Architecture](#5-architecture)
6. [Folder Structure](#6-folder-structure)
7. [Challenges Solved](#7-challenges-solved)
8. [Learning Outcomes](#8-learning-outcomes)
9. [Recruiter Summary](#9-recruiter-summary)
10. [Future Improvements](#10-future-improvements)
11. [Getting Started](#11-getting-started)

---

## 1. Project Overview

### What it does

Auto Parts Tracker lets a user register one or more vehicles, log maintenance events against them (date, mileage, task performed, optional photo of the receipt/part), and view a computed **"Upcoming Maintenance"** report that projects when each tracked task (oil service, brake pads, filters, inspections, etc.) is next due — either by mileage or by calendar date.

### Problem it solves

Vehicle owners typically track maintenance in scattered receipts, spreadsheets, or memory, making it easy to miss manufacturer-recommended service intervals (which vary by make/model and by task — e.g. oil every 10,000 km vs. brake fluid every 2 years). This app centralizes that history and turns static interval data into an actionable, per-task due list.

### Main features

- **Vehicle registry** — register a car against a reference catalog (make/model) that supplies default maintenance intervals, with an optional custom nickname/plate label.
- **Event logging (CRUD)** — record maintenance events with date, mileage, one or more predefined task types, free-text notes, and a photo upload.
- **Photo attachments** — upload, replace, and automatically clean up (delete from disk) photos tied to an event when it's edited or removed.
- **Automatic due-date engine** — computes the next due mileage/date per maintenance task from the vehicle's own event history, falling back to catalog defaults when a task has never been logged.
- **Multi-vehicle support** — switch between registered vehicles; the active vehicle is tracked server-side via session state.
- **Responsive UI** — card-based, mobile-friendly layout with a date picker and image lightbox.

---

## 2. Technologies Used

| Category | Technology |
|---|---|
| Language | Python 3.12 |
| Web Framework | [Flask](https://flask.palletsprojects.com/) (application factory + Blueprints) |
| Templating | Jinja2 (Flask's built-in engine) |
| Database | SQLite (via Python's built-in `sqlite3` module — no ORM) |
| WSGI Utilities | Werkzeug (`secure_filename` for upload sanitization) |
| Configuration | `python-dotenv` + class-based config (`Config` / `DevelopmentConfig` / `ProductionConfig`) |
| Frontend | Hand-written HTML5, CSS3 (custom properties, flexbox/grid, media queries), vanilla JavaScript |
| Frontend libraries (CDN) | [Flatpickr](https://flatpickr.js.org/) (date picker) |
| Tooling | Git, `venv` for dependency isolation |

No ORM, no frontend framework, no external database server, no third-party auth or cloud SDKs are used — the stack is intentionally minimal and dependency-light (`requirements.txt` has three entries).

---

## 3. Technical Skills Demonstrated

- **Web application development with Flask** — application factory pattern (`create_app()`), modular routing via **Blueprints** (`cars_bp`, `events_bp`) instead of a single monolithic routes file.
- **Layered / service-oriented design** — routes (HTTP layer) never touch SQL directly; they call a service layer (`car_service`, `event_service`, `maintenance_service`), which calls a dedicated data-access module (`database.py`).
- **Relational database design with raw SQL** — schema for `cars`, `events`, and a separate `vehicles` reference/catalog table, including a one-to-many relationship (`cars.id → events.car_id`).
- **SQL injection prevention** — every query uses parameterized placeholders (`?`) rather than string interpolation.
- **CRUD operations** — full create/read/update/delete flows for both vehicles and maintenance events.
- **File upload handling & sanitization** — `werkzeug.secure_filename`, MIME-scoped `accept="image/*"` on the client, and disk cleanup of orphaned files on edit/delete.
- **Server-side session/state management** — Flask's signed session cookie tracks the "currently selected vehicle" across requests without a database-backed session store.
- **Environment-based configuration** — secrets (`SECRET_KEY`) loaded from environment variables with a `.env.example` template and a documented, deliberately excluded `.env`; separate `Development`/`Production` config classes.
- **Database schema migrations without a framework** — hand-rolled, sequential, **idempotent** migration scripts (`001_initial_schema.py` → `003_add_brake_disc_intervals.py`) that inspect `PRAGMA table_info` before altering tables, so re-running a migration is safe.
- **Domain/business logic separated from persistence** — `maintenance_service.compute_due_list()` is the core algorithm of the app: it merges per-vehicle overrides with catalog defaults, groups tasks by unit (`km` vs `years`), and projects the next due point from historical event data.
- **Date arithmetic edge-case handling** — `utils.add_years()` explicitly handles the Feb 29 leap-day overflow case (`ValueError` fallback) when projecting year-based due dates.
- **Data normalization on input** — free-text task selections and manual notes are merged into a single normalized, comma-separated `description` field on write, then parsed back into structured checkboxes + free text on the edit form (round-trip parsing).
- **Responsive, accessible-by-default UI** — CSS custom properties as a lightweight design-token system, `@media` breakpoints for mobile layout, semantic HTML forms.
- **Client-side progressive enhancement** — a small amount of vanilla JS (image lightbox overlay, Flatpickr initialization) layered on top of fully functional server-rendered forms.
- **Basic error handling** — explicit 404 responses for missing vehicles/events, defensive `try/except OSError` around filesystem cleanup so a missing photo file never crashes a request.
- **Version control hygiene** — `.gitignore` correctly excludes virtual environments, bytecode caches, instance-level SQLite databases, and secrets from source control.

---

## 4. Software Engineering Concepts

- **Separation of Concerns** — the codebase is split into three clear responsibilities: `routes/` (HTTP request/response and form parsing), `services/` (business rules), and `database.py` (connection/query execution). A route handler never constructs SQL, and a service function never touches `request` or `session`.
- **Single Responsibility Principle** — each service module owns exactly one aggregate: `car_service` for vehicles, `event_service` for maintenance events, `maintenance_service` for the due-date projection algorithm.
- **DRY (Don't Repeat Yourself)** — `MAINTENANCE_TASKS` is a single source of truth mapping human-readable task names to their database column and unit; it drives both the due-list computation and the edit-form's checkbox reconciliation logic, so task definitions never need to be duplicated.
- **Idempotency** — every migration script checks existing schema state (`PRAGMA table_info`) before mutating it, so migrations can be safely re-run without erroring or corrupting data.
- **Fail-fast validation at the boundary** — required form fields (`date`, `mileage`, `vehicle_id`) are marked `required` in HTML and read directly via `request.form[...]`, which raises immediately on a genuinely missing field rather than silently proceeding with bad state.
- **Configuration over hard-coding** — database paths, upload folders, and secrets are resolved once in `config.py` from environment/base-path logic rather than being hard-coded across the codebase.
- **Convention-based fallback logic** — `compute_due_list()` demonstrates a small but real business rule hierarchy: vehicle-specific interval → catalog default → skip task if neither exists.
- **Defensive resource cleanup** — uploaded photos are deleted from disk when an event is edited (with a new photo) or removed entirely, preventing orphaned files from accumulating — an explicit lifecycle-management decision rather than an oversight.

---

## 5. Architecture

The application follows a **layered (n-tier) architecture** inside a single Flask process, with an MVC-like split enforced by convention:

```
┌─────────────────────────────────────────────┐
│                  Browser (Client)            │
│   HTML forms, vanilla JS, Flatpickr (CDN)    │
└───────────────────┬───────────────────────────┘
                     │ HTTP (form posts / redirects)
┌───────────────────▼───────────────────────────┐
│         Presentation Layer (routes/)          │
│   cars_bp, events_bp — Flask Blueprints        │
│   Parses requests, renders Jinja2 templates    │
└───────────────────┬───────────────────────────┘
                     │ function calls (no HTTP)
┌───────────────────▼───────────────────────────┐
│          Service / Domain Layer (services/)    │
│   car_service · event_service                 │
│   maintenance_service (due-date engine)        │
└───────────────────┬───────────────────────────┘
                     │ function calls
┌───────────────────▼───────────────────────────┐
│         Data Access Layer (database.py)        │
│   sqlite3 connections, parameterized queries   │
└───────────────────┬───────────────────────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
  instance/database.db     instance/vehicles.db
  (cars, events —          (make/model catalog +
   user/transactional data)  default intervals —
                              reference/lookup data)
```

This is a **client-server, server-rendered (multi-page) web application** — not a REST/JSON API consumed by a separate frontend. Every user action is a standard HTML form submission or link navigation, and the server responds with a fully rendered HTML page (or a redirect), which keeps the client trivially simple and the app deployable without a JS build pipeline.

**Two-database split** is a deliberate design choice: `database.db` holds mutable, user-owned data (registered cars, logged events), while `vehicles.db` holds a mostly-static reference catalog (manufacturer defaults per make/model). This separates transactional data from lookup/master data, so the catalog can be reseeded (`scripts/seed_vehicles.py`) independently of user data.

---

## 6. Folder Structure

```
auto_parts_tracker/
├── app/
│   ├── __init__.py          # Application factory (create_app) — wires config + blueprints
│   ├── config.py             # Config / DevelopmentConfig / ProductionConfig
│   ├── database.py           # sqlite3 connection helpers (get_db, get_vehicles_db)
│   ├── utils.py               # Small framework-agnostic helpers (date math)
│   ├── routes/                # Presentation layer — Flask Blueprints
│   │   ├── cars.py            # Vehicle registration/selection/deletion endpoints
│   │   └── events.py          # Maintenance event CRUD + upcoming-maintenance view
│   └── services/               # Business/domain logic layer
│       ├── car_service.py     # Vehicle & catalog persistence operations
│       ├── event_service.py   # Maintenance event persistence operations
│       └── maintenance_service.py  # Due-date projection engine + task catalog
├── migrations/                 # Hand-rolled, idempotent, sequential schema migrations
├── scripts/
│   └── seed_vehicles.py        # Reseeds the vehicle reference catalog
├── static/
│   ├── css/                     # Per-page stylesheets (design tokens, responsive rules)
│   └── uploads/                 # User-uploaded maintenance photos
├── templates/                    # Jinja2 templates (one per page/view)
├── instance/                      # Local SQLite databases (gitignored)
├── .env.example                   # Documents required environment variables
├── requirements.txt
└── run.py                          # Development entrypoint
```

---

## 7. Challenges Solved

- **Modeling "next due" without a rigid schema.** Maintenance tasks differ in unit (mileage vs. time) and in whether a vehicle overrides the manufacturer default. `maintenance_service.compute_due_list()` solves this with a single data-driven loop over `MAINTENANCE_TASKS`, rather than hard-coding a branch per task — adding a new trackable task is a one-line addition to the dictionary, not a new function.
- **Reconstructing structured state from a denormalized field.** Events store their tasks as a single comma-separated `description` string (to keep the schema simple and support free-text notes alongside fixed tasks). The edit view has to reverse this on load — splitting the string, matching each fragment case-insensitively against the known task catalog, and routing unmatched fragments into a "manual notes" field — without losing user-entered text that doesn't match any known task.
- **Evolving a schema without a migration framework.** Three sequential migrations add columns to `cars` over time (`oil_service_interval`/`inspection_interval`, then brake disc intervals). Each is written to be safely re-runnable by checking `PRAGMA table_info` first, avoiding the common pitfall of a migration script that crashes (or silently fails) on a second run.
- **Leap-year-safe date projection.** Adding N years to a service date via `datetime.replace(year=...)` throws on a Feb 29 anniversary in a non-leap year; `add_years()` explicitly catches this and falls back to Feb 28, so the due-date engine never crashes on a real-world date.
- **Avoiding orphaned uploads.** Because photos live on disk (not in the database), deleting or replacing an event's photo requires explicit filesystem cleanup — handled defensively so a missing/already-deleted file never turns into a 500 error.

---

## 8. Learning Outcomes

Building (or extending) a project like this exercises:

- How to structure a Flask application beyond a single `app.py` — factory pattern, Blueprints, and a layered folder structure that scales past a toy project.
- Writing safe, parameterized SQL by hand, and understanding *why* an ORM exists by feeling the boilerplate it would remove.
- Designing a schema migration strategy from first principles, including idempotency, before reaching for a tool like Alembic or Flask-Migrate.
- Handling file uploads end-to-end: validation, storage, referencing from a database row, and lifecycle cleanup.
- Translating a real-world business rule (manufacturer service intervals) into a small, data-driven algorithm instead of a wall of conditionals.
- Recognizing where server-rendered, form-based architecture is a legitimate and simpler alternative to a REST API + SPA for a small, form-heavy CRUD application.

---

## 9. Recruiter Summary

This repository demonstrates the ability to independently design and ship a **complete, working full-stack web application** using Python and Flask — from database schema through business logic to a polished, responsive UI — without leaning on scaffolding tools, an ORM, or a frontend framework to do the hard parts for you.

Specifically, it shows competency in: **backend web development (Flask, Blueprints, application factory)**, **relational database design and raw SQL** with injection-safe query practices, **layered architecture and separation of concerns**, **CRUD API/route design**, **file upload handling and security-conscious sanitization**, **environment-based configuration management**, **hand-written schema migrations**, **algorithmic business-logic implementation** (the due-date projection engine), and **responsive frontend styling** with plain CSS/JS. The codebase is small enough to review in full, which makes it a good signal of code organization habits and attention to edge cases (idempotent migrations, leap-year dates, orphaned file cleanup) rather than a showcase of framework breadth.

---

## 10. Future Improvements

Honest next steps if this project continued toward production-grade maturity:

- **Automated testing** — no unit/integration tests currently exist; the service layer (`maintenance_service.compute_due_list`, `utils.add_years`) is well-isolated and would be straightforward to cover with `pytest`.
- **Authentication & authorization** — the app currently has no user accounts; all vehicles are globally visible. Multi-user support would need login, and per-user scoping of cars/events.
- **ORM adoption** (e.g. SQLAlchemy) — would remove repetitive connection/cursor boilerplate and add a formal migration tool (Alembic/Flask-Migrate) in place of the hand-rolled scripts.
- **CI/CD pipeline** — no GitHub Actions/CI currently runs; linting, tests, and a build check would catch regressions before merge.
- **Containerization** — a `Dockerfile` and `docker-compose.yml` would make local setup and deployment environment-independent (currently relies on a local Python virtual environment).
- **JSON/REST API layer** — the current app is form/HTML-only; exposing the same operations as a JSON API would enable a future mobile client or SPA frontend.
- **Structured logging** — currently there is no application logging; request/error logging with correlation would aid production debugging.
- **Input validation hardening** — form values are parsed with minimal validation (e.g., mileage parsing assumes a `.`-separated thousands format); a validation library (e.g. WTForms) would centralize and harden this.

---

## 11. Getting Started

```bash
# 1. Clone and enter the project
git clone <repo-url>
cd auto_parts_tracker

# 2. Create and activate a virtual environment
python -m venv env
env\Scripts\activate      # Windows
# source env/bin/activate # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure secrets
copy .env.example .env    # Windows
# cp .env.example .env    # macOS/Linux
# then edit .env and set a real SECRET_KEY

# 5. Initialize the database
python migrations/001_initial_schema.py
python migrations/002_add_intervals.py
python migrations/003_add_brake_disc_intervals.py
python scripts/seed_vehicles.py

# 6. Run the app
python run.py
# → http://127.0.0.1:5000
```
