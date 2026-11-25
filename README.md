# Cloud-Native Task Processing Platform

A containerized task-processing API built with FastAPI, PostgreSQL, SQLAlchemy, and LocalStack for SQS.

## Current implementation

- FastAPI endpoints to create, list, retrieve, update, and delete tasks.
- PostgreSQL persistence through SQLAlchemy. Tables are created at API startup; Alembic migrations are not set up yet.
- Task creation sends a message to the `task-queue` SQS queue.
- A separate worker polls the queue, marks tasks `processing`, simulates work, and then marks them `completed`.
- Failed tasks record an error and retry count. They are retried by SQS and moved to the `task-dlq` dead-letter queue after three receives by default.
- Task responses include `retry_count` and `error_message`.

The API and worker run as separate containers built from the same application source and Dockerfile.

## API

| HTTP method | Path | Description |
| --- | --- | --- |
| `GET` | `/health` | API health check |
| `POST` | `/tasks` | Create a task and enqueue it |
| `GET` | `/tasks` | List tasks |
| `GET` | `/tasks/dlq` | Inspect the dead-letter queue message count and messages |
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

## Retries and dead-letter queue

The worker records failed attempts and leaves unsuccessful messages on the main queue for SQS to retry. After the configured receive limit, SQS routes the message to `task-dlq`. The default maximum receive count is `3`, and the default visibility timeout is `10` seconds. The API endpoint `GET /tasks/dlq` reports the approximate message count and currently available DLQ messages; inspecting them does not delete them.

For testing the failure path, a task title containing `fail` triggers a simulated processing error. This is a development/test behavior, not application-specific failure handling.

Queue settings can be configured with `SQS_ENDPOINT_URL`, `AWS_REGION`, `QUEUE_NAME`, `DLQ_NAME`, `MAX_RECEIVE_COUNT`, and `VISIBILITY_TIMEOUT`. The database connection can be set with `DATABASE_URL`. Defaults are defined in `database.py` and `queue_service.py`; Docker Compose supplies the database and SQS endpoint for container networking.

## Tests and CI

Install the project dependencies, including pytest, and run the test suite from the repository root:

```bash
pip install -r requirements.txt
pytest -v
```

Tests use a local SQLite database and mock SQS interactions, so the test suite does not require running PostgreSQL or LocalStack. API tests cover task creation, listing, missing-task responses, and DLQ inspection. Worker tests cover successful processing, retryable and exhausted failures, duplicate completed messages, and missing task IDs.

GitHub Actions runs `pytest -v` on pushes and pull requests targeting `main`, using Python 3.12.

## Run without Docker

For manual development, Python 3, PostgreSQL, and LocalStack must already be running. The app expects the `task_db` database and uses the default local connection settings in `database.py` and `queue_service.py`. Install dependencies from `requirements.txt`, then run the API and worker in separate terminals:

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

```bash
python worker.py
```
