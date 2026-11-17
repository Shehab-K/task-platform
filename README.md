# Cloud-Native Task Processing Platform

A task-processing API built with FastAPI, PostgreSQL, SQLAlchemy, and an SQS-compatible queue. The current local setup uses LocalStack for SQS.

## Current implementation

- FastAPI endpoints to create, list, retrieve, update, and delete tasks.
- PostgreSQL persistence through SQLAlchemy. Tables are created at API startup; Alembic migrations are not set up yet.
- Task creation sends a message to the `task-queue` SQS queue.
- A separate worker polls the queue, marks tasks `processing`, simulates work for five seconds, and then marks them `completed`.

The worker and API must run as separate processes. The worker does not start automatically with the API.

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

## Local setup

### Prerequisites

- Python 3
- PostgreSQL running locally, with a `task_db` database and credentials matching the connection URL in `database.py`
- LocalStack running locally with its SQS service available at `http://localhost:4566`

The current connection details are configured directly in `database.py` and `queue_service.py`. The queue is created automatically when the API or worker connects to it.

### Install dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn sqlalchemy psycopg2-binary boto3
```

### Run the API and worker

In the first terminal, start the API:

```bash
source venv/bin/activate
uvicorn main:app --reload
```

In a second terminal, start the worker:

```bash
source venv/bin/activate
python worker.py
```

Create a task using the interactive API docs at http://127.0.0.1:8000/docs. The worker logs task processing in its terminal. You can also check the task status with `GET /tasks/{task_id}`; it changes from `pending` to `processing` and then `completed`.
