import pytest


@pytest.mark.asyncio
async def test_create_credential(test_app, vault):
    resp = await test_app.post("/api/credentials", json={
        "plugin_id": "mock",
        "display_name": "test-account",
        "credentials": {"token": "my-token"},
        "enabled_games": ["game1"],
        "is_enabled": True,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["display_name"] == "test-account"
    assert data["plugin_id"] == "mock"
    assert data["id"] > 0
    assert "credentials" not in data

    creds = vault.get_credentials("mock")
    assert len(creds) == 1
    assert creds[0]["credentials"] == {"token": "my-token"}


@pytest.mark.asyncio
async def test_list_credentials(test_app, vault):
    await vault.save_credential("mock", {
        "display_name": "acc1",
        "credentials": {},
    })
    await vault.save_credential("mock", {
        "display_name": "acc2",
        "credentials": {},
    })
    resp = await test_app.get("/api/credentials")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    names = [c["display_name"] for c in data]
    assert "acc1" in names
    assert "acc2" in names


@pytest.mark.asyncio
async def test_update_credential(test_app, vault):
    cid = await vault.save_credential("mock", {
        "display_name": "old",
        "credentials": {"token": "old"},
        "enabled_games": [],
    })
    resp = await test_app.put(f"/api/credentials/{cid}", json={
        "display_name": "updated",
        "credentials": {"token": "new"},
        "is_enabled": False,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["display_name"] == "updated"
    assert not data["is_enabled"]

    creds = vault.get_credentials("mock")
    assert creds[0]["display_name"] == "updated"
    assert creds[0]["credentials"] == {"token": "new"}


@pytest.mark.asyncio
async def test_update_nonexistent_credential(test_app):
    resp = await test_app.put("/api/credentials/99999", json={
        "display_name": "x",
    })
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_credential(test_app, vault):
    cid = await vault.save_credential("mock", {
        "display_name": "del-me",
        "credentials": {},
    })
    resp = await test_app.delete(f"/api/credentials/{cid}")
    assert resp.status_code == 200
    assert resp.json() == {"message": "deleted"}
    assert len(vault.get_credentials("mock")) == 0


@pytest.mark.asyncio
async def test_validate_credential(test_app, vault):
    await vault.save_credential("mock", {
        "display_name": "acc",
        "credentials": {"token": "x"},
    })
    creds = vault.get_credentials("mock")
    cid = creds[0]["id"]

    resp = await test_app.post(f"/api/credentials/{cid}/validate")
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is True


@pytest.mark.asyncio
async def test_validate_nonexistent_credential(test_app):
    resp = await test_app.post("/api/credentials/99999/validate")
    assert resp.status_code == 404
