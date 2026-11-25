import json
from unittest.mock import MagicMock

import main


def test_create_task_success(client, monkeypatch):
    mock_send = MagicMock()
    monkeypatch.setattr(main, "send_task_to_queue", mock_send)

    # send a real HTTP POST instead of using swagger ui execute button
    response = client.post(
        "/tasks",
        json={"title": "Write unit tests", "description": "First pytest test"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Write unit tests"
    assert data["status"] == "pending"
    assert data["retry_count"] == 0
    assert data["error_message"] is None
    mock_send.assert_called_once_with(1)


def test_get_tasks_returns_created_items(client, monkeypatch):
    monkeypatch.setattr(main, "send_task_to_queue", MagicMock())

    client.post("/tasks", json={"title": "Task A"})
    client.post("/tasks", json={"title": "Task B"})

    response = client.get("/tasks")

    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 2
    assert tasks[0]["title"] == "Task A"
    assert tasks[1]["title"] == "Task B"


def test_get_nonexistent_task_returns_404(client):
    response = client.get("/tasks/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "task not found"


def test_get_dlq_messages(client, monkeypatch):
    
    mock_sqs = MagicMock()
    fake_dlq_url = "http://localhost:4566/000000000000/task-dlq"

    mock_sqs.create_queue.return_value = {"QueueUrl": fake_dlq_url}
    mock_sqs.get_queue_attributes.return_value = {
        "Attributes": {"ApproximateNumberOfMessages": "1"}
    }
    mock_sqs.receive_message.return_value = {
        "Messages": [
            {
                "MessageId": "msg-123",
                "Body": json.dumps({"task_id": 7}),
            }
        ]
    }
    monkeypatch.setattr(main, "sqs_client", mock_sqs)

    
    response = client.get("/tasks/dlq")

    
    assert response.status_code == 200
    data = response.json()
    assert data["queue"] == main.DLQ_NAME
    assert data["approximate_message_count"] == 1
    assert data["messages"] == [
        {"message_id": "msg-123", "body": {"task_id": 7}}
    ]
    mock_sqs.get_queue_attributes.assert_called_once_with(
        QueueUrl=fake_dlq_url,
        AttributeNames=["ApproximateNumberOfMessages"],
    )
    mock_sqs.receive_message.assert_called_once_with(
        QueueUrl=fake_dlq_url,
        MaxNumberOfMessages=10,
        WaitTimeSeconds=1,
        VisibilityTimeout=0,
    )