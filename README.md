# Cloud-Native Task Processing Platform

A distributed, scalable task processing system built with FastAPI, PostgreSQL, and AWS cloud-native services.

## Project Architecture & Roadmap

- [x] **Stage 1: FastAPI Core & REST API** (In-memory CRUD operations with Pydantic validation)
- [ ] **Stage 2: Database Integration** (PostgreSQL & SQLAlchemy ORM with Alembic migrations)
- [ ] **Stage 3: Asynchronous Task Processing** (Background workers with Amazon SQS)
- [ ] **Stage 4: Cloud Infrastructure & Kubernetes** (Docker, Terraform, AWS EKS deployment)

---

## Stage 1: API Specifications

| HTTP Method | Path | Description | Input / Parameters |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Health Check | None |
| `POST` | `/tasks` | Create a new task | JSON Body (`TaskCreate`) |
| `GET` | `/tasks` | Fetch all tasks | None |
| `GET` | `/tasks/{task_id}` | Fetch a task by ID | Path Parameter (`task_id`) |
| `PUT` | `/tasks/{task_id}` | Update an existing task | Path Parameter + JSON Body (`TaskUpdate`) |
| `DELETE` | `/tasks/{task_id}` | Delete a task | Path Parameter (`task_id`) |

---

## Local Setup & Execution

### 1. Clone the repository:

```bash
git clone https://github.com/Shehab-K/task-platform.git
cd task-platform
```

### 2. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies:

```bash
pip install fastapi uvicorn pydantic
```

### 4. Run the API server:

```bash
uvicorn main:app --reload
```

### 5. Access Interactive Documentation:

Open the following URL in your browser:

http://127.0.0.1:8000/docs
