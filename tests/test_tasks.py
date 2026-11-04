from tests.conftest import make_headers

def test_create_and_get_task(client, auth_headers):
    r = client.post("/tasks", json={"title": "Write README"}, headers=auth_headers)
    assert r.status_code == 201
    task_id = r.json()["id"]
    assert client.get(f"/tasks/{task_id}", headers=auth_headers).json()["title"] == "Write README"

def test_filter_by_status(client, auth_headers):
    client.post("/tasks", json={"title": "A", "status": "done"}, headers=auth_headers)
    client.post("/tasks", json={"title": "B"}, headers=auth_headers)
    r = client.get("/tasks?status=done", headers=auth_headers)
    assert [t["title"] for t in r.json()] == ["A"]

def test_pagination(client, auth_headers):
    for i in range(5):
        client.post("/tasks", json={"title": f"T{i}"}, headers=auth_headers)
    assert len(client.get("/tasks?limit=2", headers=auth_headers).json()) == 2

def test_update_task(client, auth_headers):
    tid = client.post("/tasks", json={"title": "A"}, headers=auth_headers).json()["id"]
    r = client.patch(f"/tasks/{tid}", json={"status": "done"}, headers=auth_headers)
    assert r.json()["status"] == "done"
    assert r.json()["title"] == "A"

def test_delete_task(client, auth_headers):
    tid = client.post("/tasks", json={"title": "A"}, headers=auth_headers).json()["id"]
    assert client.delete(f"/tasks/{tid}", headers=auth_headers).status_code == 204
    assert client.get(f"/tasks/{tid}", headers=auth_headers).status_code == 404

def test_cannot_access_other_users_task(client, auth_headers):
    tid = client.post("/tasks", json={"title": "Private"}, headers=auth_headers).json()["id"]
    other = make_headers(client, email="b@test.com")
    assert client.get(f"/tasks/{tid}", headers=other).status_code == 404
    assert client.delete(f"/tasks/{tid}", headers=other).status_code == 404

def test_invalid_status_rejected(client, auth_headers):
    r = client.post("/tasks", json={"title": "A", "status": "banana"}, headers=auth_headers)
    assert r.status_code == 422