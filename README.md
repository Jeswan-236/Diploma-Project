# Diploma Project — Skill Stalker

## Overview

This repository contains a learning portal for Skill Stalker with a Flask backend and frontend demo pages. The backend manages authentication via Supabase and JWTs, while the frontend provides a student dashboard, AI helper widget, and study resources.

## Structure

- `backend/` — Flask application and environment configuration
- `frontend/` — static HTML, CSS, and JavaScript demo pages

## Requirements

- Python 3.11+ (recommended)
- Node/npm is not required for the static frontend, but a browser is needed to open HTML pages

## Setup

1. Create a Python virtual environment in the root directory:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
2. Install backend dependencies:
   ```powershell
   pip install -r backend\requirements.txt
   ```
3. Copy the environment template:
   ```powershell
   copy .\backend\.env.example .\backend\.env
   ```
4. Edit `backend\.env` and add your Supabase credentials:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `SECRET_KEY`
   - `DATABASE_URL` (optional if using direct Postgres access)

## Run backend

From the repository root with the virtual environment active:

```powershell
cd backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Then open any frontend HTML page in a browser, or connect to the backend API at `http://127.0.0.1:8000`.

## Notes

- `backend/.env` is ignored by version control and should contain secrets.
- `backend/.env.example` is provided as a template.
- The frontend pages are static; integration with the backend requires adding API calls and token handling.

## Recommended improvements

- Add frontend login/register flows that consume `/api/auth/login` and `/api/auth/register`
- Harden CORS settings in `backend/main.py`
- Remove the hardcoded fallback secret key and fail loudly if `SECRET_KEY` is missing
- Add a proper `README` page and deployment instructions for Supabase
