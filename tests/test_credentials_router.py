import pytest


@pytest.mark.asyncio
async def test_create_credential(test_app, yaml_store):
    resp = await test_app.post("/api/credentials", json={
        "plugin_id": "mock",
        "user_id": "test-user",
        "token": "my-token",
        "enabled_games": ["game1"],
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
async def test_list_credentials(test_app, yaml_store):
    yaml_store.save("mock", {"user_id": "u1", "token": "a", "enabled_games": []})
    yaml_store.save("mock", {"user_id": "u2", "token": "b", "enabled_games": []})
    resp = await test_app.get("/api/credentials")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    uids = [c["user_id"] for c in data]
    assert "u1" in uids
    assert "u2" in uids


@pytest.mark.asyncio
async def test_update_credential(test_app, yaml_store):
    cid = yaml_store.save("mock", {"user_id": "old", "token": "old", "enabled_games": []})
    resp = await test_app.put(f"/api/credentials/{cid}", json={
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
async def test_update_nonexistent_credential(test_app):
    resp = await test_app.put("/api/credentials/99999", json={"user_id": "x"})
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_credential(test_app, yaml_store):
    cid = yaml_store.save("mock", {"user_id": "del-me", "token": "x", "enabled_games": []})
    resp = await test_app.delete(f"/api/credentials/{cid}")
    assert resp.status_code == 200
    assert resp.json() == {"message": "deleted"}
    assert yaml_store.get("mock", cid) is None


@pytest.mark.asyncio
async def test_validate_credential(test_app, yaml_store):
    yaml_store.save("mock", {"user_id": "acc", "token": "x", "enabled_games": []})
    creds = yaml_store.list_by_plugin("mock")
    cid = creds[0]["id"]

    resp = await test_app.post(f"/api/credentials/{cid}/validate")
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is True


@pytest.mark.asyncio
async def test_validate_nonexistent_credential(test_app):
    resp = await test_app.post("/api/credentials/99999/validate")
    assert resp.status_code == 404
