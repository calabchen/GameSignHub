import pytest


@pytest.mark.asyncio
async def test_create_account(test_app, yaml_store):
    resp = await test_app.post("/api/accounts", json={
        "plugin_id": "mock",
        "user_id": "test-user",
        "token": "my-token",
        "is_enabled": True,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["user_id"] == "test-user"
    assert data["plugin_id"] == "mock"
    assert data["id"] > 0

    full = yaml_store.get("mock", data["id"])
    assert full["token"] == "my-token"


@pytest.mark.asyncio
async def test_list_accounts(test_app, yaml_store):
    yaml_store.save("mock", {"user_id": "u1", "token": "a"})
    yaml_store.save("mock", {"user_id": "u2", "token": "b"})
    resp = await test_app.get("/api/accounts")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    uids = [c["user_id"] for c in data]
    assert "u1" in uids
    assert "u2" in uids


@pytest.mark.asyncio
async def test_list_accounts_by_plugin(test_app, yaml_store):
    yaml_store.save("mock", {"user_id": "u1", "token": "a"})
    resp = await test_app.get("/api/accounts?plugin=mock")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1


@pytest.mark.asyncio
async def test_get_account(test_app, yaml_store):
    cid = yaml_store.save("mock", {"user_id": "u1", "token": "a"})
    resp = await test_app.get(f"/api/accounts/{cid}", params={"plugin": "mock"})
    assert resp.status_code == 200
    assert resp.json()["user_id"] == "u1"


@pytest.mark.asyncio
async def test_get_account_not_found(test_app):
    resp = await test_app.get("/api/accounts/99999", params={"plugin": "mock"})
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_account_no_plugin(test_app):
    resp = await test_app.get("/api/accounts/1")
    assert resp.status_code == 422  # missing plugin query param


@pytest.mark.asyncio
async def test_update_account(test_app, yaml_store):
    cid = yaml_store.save("mock", {"user_id": "old", "token": "old"})
    resp = await test_app.patch(f"/api/accounts/{cid}", params={"plugin": "mock"}, json={
        "user_id": "updated",
        "token": "new",
        "is_enabled": False,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["user_id"] == "updated"
    assert not data["is_enabled"]

    full = yaml_store.get("mock", cid)
    assert full["user_id"] == "updated"
    assert full["token"] == "new"


@pytest.mark.asyncio
async def test_update_nonexistent_account(test_app):
    resp = await test_app.patch("/api/accounts/99999", params={"plugin": "mock"}, json={"user_id": "x"})
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_account(test_app, yaml_store):
    cid = yaml_store.save("mock", {"user_id": "del-me", "token": "x"})
    resp = await test_app.delete(f"/api/accounts/{cid}", params={"plugin": "mock"})
    assert resp.status_code == 200
    assert yaml_store.get("mock", cid) is None


@pytest.mark.asyncio
async def test_validate_account(test_app, yaml_store):
    cid = yaml_store.save("mock", {"user_id": "acc", "token": "x"})
    resp = await test_app.post(f"/api/accounts/{cid}/validate", params={"plugin": "mock"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is True


@pytest.mark.asyncio
async def test_validate_nonexistent_account(test_app):
    resp = await test_app.post("/api/accounts/99999/validate", params={"plugin": "mock"})
    assert resp.status_code == 404
