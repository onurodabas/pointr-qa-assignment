# Pointr CMS REST API

REST API implementation for managing Site → Building → Level hierarchy, with BDD tests.

## Project Overview

This project implements a CMS REST API for Pointr that manages:
- **Sites** (e.g., a hospital campus)
- **Buildings** (within a site)
- **Levels** (floors within a building)

Tests are written using BDD (Behavior Driven Development) with Behave framework. Each feature file describes the API behavior in a human-readable format.

## Project Structure

```
q1_rest_api_bdd/
├── app.py                          # Flask REST API
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── .gitignore
├── .github/
│   └── workflows/
│       └── bdd-tests.yml           # CI/CD pipeline
└── features/
    ├── environment.py              # Test setup/teardown
    ├── site.feature                # Site API scenarios
    ├── building.feature            # Building API scenarios
    ├── level.feature               # Level API scenarios
    └── steps/
        ├── site_steps.py
        ├── building_steps.py
        └── level_steps.py
```

## How to Run

### Prerequisites

- Python 3.11 or newer
- pip

### Setup

```bash
# (Optional) Create a virtual environment
python3 -m venv venv
source venv/bin/activate     # Linux/Mac
# venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt
```

### Running the Tests

```bash
# Run all tests
behave

# Run a specific feature
behave features/site.feature
behave features/building.feature
behave features/level.feature

# Run a specific scenario by name
behave -n "Create site with valid data"

# Verbose output
behave -v
behave --no-capture
```

The `environment.py` file automatically starts the Flask API before the tests run and stops it when they finish, so you don't need to start the server manually.

### Running the API Manually (Optional)

```bash
python app.py
```

The API will be available at `http://localhost:5000`.

## API Endpoints

| Method | URL                       | Description                       |
|--------|---------------------------|-----------------------------------|
| POST   | /api/sites                | Create a site                     |
| GET    | /api/sites/{id}           | Get a site by ID                  |
| DELETE | /api/sites/{id}           | Delete a site                     |
| POST   | /api/buildings            | Create a building                 |
| GET    | /api/buildings/{id}       | Get a building by ID              |
| DELETE | /api/buildings/{id}       | Delete a building                 |
| POST   | /api/levels               | Import single or multiple levels  |

### Example Requests

**Create a site:**
```bash
curl -X POST http://localhost:5000/api/sites \
  -H "Content-Type: application/json" \
  -d '{"name": "Main Hospital", "description": "Central campus"}'
```

**Create a building (requires existing site_id):**
```bash
curl -X POST http://localhost:5000/api/buildings \
  -H "Content-Type: application/json" \
  -d '{"name": "Block A", "site_id": "<site-uuid>", "floors": 5}'
```

**Import multiple levels:**
```bash
curl -X POST http://localhost:5000/api/levels \
  -H "Content-Type: application/json" \
  -d '[
    {"name": "Ground", "building_id": "<building-uuid>", "floor_number": 0},
    {"name": "First", "building_id": "<building-uuid>", "floor_number": 1}
  ]'
```

## Test Coverage

The project covers 22 scenarios across 3 features:

**Site (8 scenarios):** create with valid/minimal data, validation errors (no name, empty body), retrieve existing/non-existent, delete existing/non-existent.

**Building (8 scenarios):** create with valid data, default floors, validation errors (no name, no site_id, invalid site_id), retrieve, delete.

**Level (6 scenarios):** import single, import multiple, default floor_number, missing name (partial success), invalid building_id (partial success), mixed valid/invalid import.

## Design Decisions

**In-memory storage.** The API uses Python dictionaries instead of a database. This keeps the project focused on the API and testing layer. In production, I would replace this with PostgreSQL via SQLAlchemy.

**UUIDs for IDs.** UUIDs avoid collisions and don't expose internal counters. An auto-increment integer would be simpler but reveals creation order and total count.

**Optional fields with defaults.** `description` defaults to empty string, `floors` defaults to 1, `floor_number` defaults to 0. The API always returns these fields, so clients get a consistent response shape.

**Partial success for level import.** When importing multiple levels, valid ones are created even if some fail validation. The response separates `created` and `errors` lists. This is important for bulk operations where rejecting the entire batch over one bad row is wasteful.

**Referential integrity check.** Creating a building requires a valid `site_id`; creating a level requires a valid `building_id`. The API returns 404 if the referenced resource doesn't exist.

## CI/CD

GitHub Actions workflow (`.github/workflows/bdd-tests.yml`) runs on every push and pull request. It installs dependencies, runs the BDD tests, and uploads logs on failure.

## What I'd Improve in Production

- Replace in-memory storage with PostgreSQL + SQLAlchemy
- Add request validation with Pydantic / marshmallow
- Add OpenAPI/Swagger documentation
- Add authentication (JWT or API keys)
- Add rate limiting
- Structured logging with correlation IDs
- Containerize with Docker, deploy with Gunicorn behind Nginx
- Add integration tests against a real database instance

