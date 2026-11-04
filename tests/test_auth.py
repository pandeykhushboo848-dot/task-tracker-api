def test_register_success(client):
    r = client.post("/auth/register", json={"email": "x@test.com", "password": "password123"})
    assert r.status_code == 201
    assert "hashed_password" not in r.json()

def test_register_duplicate_email(client):
    body = {"email": "x@test.com", "password": "password123"}
    client.post("/auth/register", json=body)
    assert client.post("/auth/register", json=body).status_code == 409

def test_register_short_password(client):
    r = client.post("/auth/register", json={"email": "x@test.com", "password": "123"})
    assert r.status_code == 422

def test_login_wrong_password(client):
    client.post("/auth/register", json={"email": "x@test.com", "password": "password123"})
    r = client.post("/auth/login", data={"username": "x@test.com", "password": "wrongpass1"})
    assert r.status_code == 401

def test_tasks_require_token(client):
    assert client.get("/tasks").status_code == 401