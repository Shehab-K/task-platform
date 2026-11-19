# Cloud-Native Task Processing Platform

A containerized task-processing API built with FastAPI, PostgreSQL, SQLAlchemy, and LocalStack for SQS.

## Current implementation

- FastAPI endpoints to create, list, retrieve, update, and delete tasks.
- PostgreSQL persistence through SQLAlchemy. Tables are created at API startup; Alembic migrations are not set up yet.
- Task creation sends a message to the `task-queue` SQS queue.
- A separate worker polls the queue, marks tasks `processing`, simulates work for five seconds, and then marks them `completed`.

The API and worker run as separate containers built from the same application source and Dockerfile.

## API

| HTTP method | Path | Description |
| --- | --- | --- |
| `GET` | `/health` | API health check |
| `POST` | `/tasks` | Create a task and enqueue it |
| `GET` | `/tasks` | List tasks |
| `GET` | `/tasks/{task_id}` | Get a task |
| `PUT` | `/tasks/{task_id}` | Update a task |
| `DELETE` | `/tasks/{task_id}` | Delete a task |

Example request to `POST /tasks`:

```json
{
  "title": "Example task",
  "description": "A task to process"
}
```

## Run with Docker Compose

Docker Compose starts four containers:

- **`db`** — PostgreSQL 16, with the `task_db` database.
- **`localstack`** — LocalStack SQS, exposed at `http://localhost:4566`.
- **`api`** — FastAPI application, exposed at `http://localhost:8000`.
- **`worker`** — Background task processor; its output includes task processing logs.

Build the application image and start all four containers from the project directory:

```bash
docker compose up --build -d
```

The Compose configuration waits for PostgreSQL and LocalStack health checks before starting the API and worker. Follow worker output in your terminal with:

```bash
docker compose logs -f worker
```

Open the interactive API docs at http://127.0.0.1:8000/docs and create a task. The worker logs processing; the task status changes from `pending` to `processing` and then `completed`. Check container status with `docker compose ps`, and stop the containers with `docker compose down`.

Compose builds the API and worker containers from the project `Dockerfile`, which installs dependencies from `requirements.txt`. PostgreSQL and LocalStack use the upstream images specified in `docker-compose.yml`.

## Run without Docker

For manual development, Python 3, PostgreSQL, and LocalStack must already be running. The app expects the `task_db` database and uses the default local connection settings in `database.py` and `queue_service.py`. Install dependencies from `requirements.txt`, then run the API and worker in separate terminals:

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

```bash
python worker.py
```
