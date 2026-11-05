def test_health_contract(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "harness-api"}


def test_openapi_exposes_health(client):
    assert "/api/v1/health" in client.get("/openapi.json").json()["paths"]


def test_unknown_route_is_not_success(client):
    assert client.get("/api/v1/missing").status_code == 404
