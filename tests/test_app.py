import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_signup_for_activity():
    email = "newstudent@mergington.edu"
    activity = "Chess Club"
    # Удаляем если вдруг остался
    client.delete(f"/activities/{activity}/unregister?email={email}")
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    assert f"Signed up {email} for {activity}" in response.json()["message"]
    # Проверяем, что теперь участник есть
    activities = client.get("/activities").json()
    assert email in activities[activity]["participants"]


def test_signup_duplicate():
    email = "emma@mergington.edu"
    activity = "Programming Class"
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_unregister_participant():
    email = "emma@mergington.edu"
    activity = "Programming Class"
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 200
    assert f"Unregistered {email} from {activity}" in response.json()["message"]
    # Проверяем, что участник удалён
    activities = client.get("/activities").json()
    assert email not in activities[activity]["participants"]
    # Восстанавливаем для других тестов
    client.post(f"/activities/{activity}/signup?email={email}")


def test_unregister_nonexistent():
    email = "notfound@mergington.edu"
    activity = "Chess Club"
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 404
    assert "Participant not found" in response.json()["detail"]


def test_signup_nonexistent_activity():
    email = "someone@mergington.edu"
    activity = "Nonexistent"
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_unregister_nonexistent_activity():
    email = "someone@mergington.edu"
    activity = "Nonexistent"
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]
