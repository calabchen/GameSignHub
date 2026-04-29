import pytest
from app.core.orchestrator import Orchestrator


@pytest.mark.asyncio
async def test_sign_credential_writes_log(test_session_factory, vault, mock_plugin_registry):
    await vault.save_credential("mock", {
        "display_name": "test-user",
        "credentials": {"token": "abc"},
    })

    oc = Orchestrator(mock_plugin_registry, vault, test_session_factory)
    cred = vault.get_credentials("mock")[0]

    logs = await oc.sign_credential("mock", cred["id"])
    assert len(logs) >= 1
    assert logs[0].plugin_id == "mock"
    assert logs[0].game_id == "game1"
    assert logs[0].status == "success"
    assert logs[0].reward == "100 coins"
    assert logs[0].message == "OK"


@pytest.mark.asyncio
async def test_sign_credential_persisted_to_db(test_session_factory, vault, mock_plugin_registry):
    await vault.save_credential("mock", {
        "display_name": "test-user",
        "credentials": {"token": "abc"},
    })
    cred = vault.get_credentials("mock")[0]

    oc = Orchestrator(mock_plugin_registry, vault, test_session_factory)
    await oc.sign_credential("mock", cred["id"])

    rows, total = await oc.get_logs(page=1, page_size=50)
    assert total >= 1
    assert rows[0].game_id == "game1"
    assert rows[0].status == "success"


@pytest.mark.asyncio
async def test_sign_all_writes_multiple_logs(test_session_factory, vault, mock_plugin_registry):
    await vault.save_credential("mock", {
        "display_name": "user1",
        "credentials": {"token": "a"},
    })
    await vault.save_credential("mock", {
        "display_name": "user2",
        "credentials": {"token": "b"},
    })

    oc = Orchestrator(mock_plugin_registry, vault, test_session_factory)
    logs = await oc.sign_all()
    assert len(logs) >= 2


@pytest.mark.asyncio
async def test_get_logs_pagination(test_session_factory, vault, mock_plugin_registry):
    await vault.save_credential("mock", {
        "display_name": "u",
        "credentials": {"token": "x"},
    })
    cred = vault.get_credentials("mock")[0]

    oc = Orchestrator(mock_plugin_registry, vault, test_session_factory)
    for _ in range(3):
        await oc.sign_credential("mock", cred["id"])

    rows, total = await oc.get_logs(page=1, page_size=2)
    assert len(rows) == 2
    assert total == 3

    rows, total = await oc.get_logs(page=2, page_size=2)
    assert len(rows) == 1


@pytest.mark.asyncio
async def test_get_today_summary(test_session_factory, vault, mock_plugin_registry):
    await vault.save_credential("mock", {
        "display_name": "u",
        "credentials": {"token": "x"},
    })
    cred = vault.get_credentials("mock")[0]

    oc = Orchestrator(mock_plugin_registry, vault, test_session_factory)
    await oc.sign_credential("mock", cred["id"])

    summary = await oc.get_today_summary()
    assert summary["total"] >= 1
    assert summary["success"] >= 1


@pytest.mark.asyncio
async def test_clear_logs(test_session_factory, vault, mock_plugin_registry):
    await vault.save_credential("mock", {
        "display_name": "u",
        "credentials": {"token": "x"},
    })
    cred = vault.get_credentials("mock")[0]

    oc = Orchestrator(mock_plugin_registry, vault, test_session_factory)
    await oc.sign_credential("mock", cred["id"])

    _, total_before = await oc.get_logs()
    assert total_before >= 1

    deleted = await oc.clear_logs()
    assert deleted == total_before

    _, total_after = await oc.get_logs()
    assert total_after == 0


@pytest.mark.asyncio
async def test_sign_unknown_plugin_raises(test_session_factory, vault, mock_plugin_registry):
    await vault.save_credential("mock", {
        "display_name": "u",
        "credentials": {"token": "x"},
    })
    cred = vault.get_credentials("mock")[0]

    oc = Orchestrator(mock_plugin_registry, vault, test_session_factory)
    with pytest.raises(ValueError, match="Unknown plugin"):
        await oc.sign_credential("nonexistent", cred["id"])


@pytest.mark.asyncio
async def test_sign_vault_locked_raises(test_session_factory, vault, mock_plugin_registry):
    await vault.save_credential("mock", {
        "display_name": "u",
        "credentials": {"token": "x"},
    })
    cred = vault.get_credentials("mock")[0]

    vault.lock()
    oc = Orchestrator(mock_plugin_registry, vault, test_session_factory)
    with pytest.raises(Exception):
        await oc.sign_credential("mock", cred["id"])


@pytest.mark.asyncio
async def test_get_logs_filter_by_status(test_session_factory, vault, mock_plugin_registry):
    await vault.save_credential("mock", {
        "display_name": "u",
        "credentials": {"token": "x"},
    })
    cred = vault.get_credentials("mock")[0]

    oc = Orchestrator(mock_plugin_registry, vault, test_session_factory)
    await oc.sign_credential("mock", cred["id"])

    rows, total = await oc.get_logs(status="success")
    assert total >= 1
    assert all(r.status == "success" for r in rows)

    rows, total = await oc.get_logs(status="failed")
    assert total == 0
