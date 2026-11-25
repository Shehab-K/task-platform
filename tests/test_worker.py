from unittest.mock import MagicMock

import models
import worker
from tests.conftest import TestingSessionLocal


def test_process_task_success(monkeypatch):
    monkeypatch.setattr(worker, "SessionLocal", TestingSessionLocal)
    monkeypatch.setattr(worker.time, "sleep", MagicMock())

    db = TestingSessionLocal()
    task = models.Task(title="Generate monthly report", status="pending")
    db.add(task)
    db.commit()
    db.refresh(task)

    succeeded = worker.process_task(task.id)

    db.refresh(task)
    assert succeeded is True
    assert task.status == "completed"
    assert task.error_message is None
    db.close()


def test_process_task_transient_failure_sets_retrying(monkeypatch):
    monkeypatch.setattr(worker, "SessionLocal", TestingSessionLocal)
    monkeypatch.setattr(worker.time, "sleep", MagicMock())
    monkeypatch.setattr(worker, "MAX_RECEIVE_COUNT", 3)

    db = TestingSessionLocal()
    task = models.Task(title="Please fail once", status="pending", retry_count=0)
    db.add(task)
    db.commit()
    db.refresh(task)

    succeeded = worker.process_task(task.id)

    db.refresh(task)
    assert succeeded is False
    assert task.status == "retrying"
    assert task.retry_count == 1
    assert "Simulated processing error" in task.error_message
    db.close()


def test_process_task_max_retries_sets_failed(monkeypatch):
    monkeypatch.setattr(worker, "SessionLocal", TestingSessionLocal)
    monkeypatch.setattr(worker.time, "sleep", MagicMock())
    monkeypatch.setattr(worker, "MAX_RECEIVE_COUNT", 3)

    db = TestingSessionLocal()
    task = models.Task(title="Permanent fail task", status="retrying", retry_count=2)
    db.add(task)
    db.commit()
    db.refresh(task)

    succeeded = worker.process_task(task.id)

    db.refresh(task)
    assert succeeded is False
    assert task.status == "failed"
    assert task.retry_count == 3
    db.close()


def test_process_task_idempotency_skips_completed_task(monkeypatch):
    monkeypatch.setattr(worker, "SessionLocal", TestingSessionLocal)
    mock_sleep = MagicMock()
    monkeypatch.setattr(worker.time, "sleep", mock_sleep)

    db = TestingSessionLocal()
    task = models.Task(
        title="Fail keyword but already done", status="completed", retry_count=0
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    succeeded = worker.process_task(task.id)

    db.refresh(task)
    assert succeeded is True
    assert task.status == "completed"
    assert task.retry_count == 0
    mock_sleep.assert_not_called()
    db.close()


def test_process_task_missing_id_returns_true(monkeypatch):
    monkeypatch.setattr(worker, "SessionLocal", TestingSessionLocal)
    monkeypatch.setattr(worker.time, "sleep", MagicMock())

    succeeded = worker.process_task(999)

    assert succeeded is True