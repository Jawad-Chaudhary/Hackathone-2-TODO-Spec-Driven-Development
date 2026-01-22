## Running the Project with Docker

This project provides a full-stack application with a Python (FastAPI) backend, a TypeScript (Next.js) frontend, and a PostgreSQL database. The recommended way to run the project is using Docker Compose, which orchestrates all services and their dependencies.

### Project-Specific Docker Requirements

- **Backend**: Python 3.11 (from `python:3.11-slim`), uses `uv` for dependency management, and runs with `uvicorn`.
- **Frontend**: Node.js 22.13.1 (from `node:22.13.1-slim`), builds and serves a Next.js app.
- **Database**: PostgreSQL (official `postgres:latest` image).

### Required Environment Variables

- **Backend**: Copy `./backend/.env.example` to `./backend/.env` and fill in the required values (e.g., `DATABASE_URL`, secrets, etc.).
- **Frontend**: If needed, copy `./frontend/.env.local.example` to `./frontend/.env.local` and adjust as necessary.
- **Database**: Credentials are set in `compose.yaml` (user: `user`, password: `password`, db: `database`). Ensure your backend `.env` matches these values.

### Build and Run Instructions

1. **Prepare Environment Files**
   - Backend: `cp ./backend/.env.example ./backend/.env` and edit as needed.
   - Frontend (optional): `cp ./frontend/.env.local.example ./frontend/.env.local` and edit as needed.

2. **Start All Services**
   - From the project root, run:
     ```sh
     docker compose up --build
     ```
   - This will build and start the backend, frontend, and database containers.

### Service Ports

- **Backend (FastAPI)**: [http://localhost:8000](http://localhost:8000)
- **Frontend (Next.js)**: [http://localhost:3000](http://localhost:3000)
- **PostgreSQL**: [localhost:5432](localhost:5432)

### Special Configuration Notes

- The backend expects the database connection string in the `.env` file to match the credentials set in `compose.yaml`.
- The frontend expects the backend to be available at `http://localhost:8000`.
- Both backend and frontend containers run as non-root users for improved security.
- The backend uses `uv` for Python dependency management; no manual `pip` or `venv` setup is needed.
- Persistent PostgreSQL data is stored in the `pgdata` Docker volume.

---

_If you make changes to environment files or dependencies, re-run `docker compose up --build` to ensure all services are up to date._
