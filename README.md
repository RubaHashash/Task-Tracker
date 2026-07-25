# Task Tracker

A FastAPI + vanilla HTML/CSS/JavaScript Kanban task tracker with in-memory
storage.

## Mid-Course Project

This branch adds:

- Optional task due dates and overdue filtering
- Task search and combined filters

### Run the backend

```bash
python -m venv venv
# Activate the environment
# Windows (PowerShell):
venv\Scripts\Activate.ps1
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The API is now available at `http://localhost:8000` (interactive docs at
`http://localhost:8000/docs`).

### Run the frontend

The frontend is a static file at `app/frontend/index.html`. Serve it with any
static file server, for example:

```bash
python -m http.server 5500 --directory app/frontend
```

Then open `http://localhost:5500` in your browser. The frontend expects the
backend to be running at `http://localhost:8000`.

### Run the tests

```bash
pytest
```
