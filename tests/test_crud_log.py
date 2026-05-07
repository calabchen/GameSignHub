import pytest
from app.core.crud_log import get_logs
from app.core.orchestrator import Orchestrator


@pytest.mark.asyncio
async def test_sign_credential_persisted_to_db(test_session_factory, yaml_store, mock_plugin_registry):
    yaml_store.save("mock", {
        "display_name": "test-user",
        "credentials": {"token": "abc"},
    })
    creds = yaml_store.list_all(plugin_id="mock")

    oc = Orchestrator(mock_plugin_registry, test_session_factory)
    await oc.sign_credential("mock", creds[0]["id"])

    rows, total = await get_logs(test_session_factory, page=1, page_size=50)
    assert total >= 1
    assert rows[0]["game_id"] == "game1"
    assert rows[0]["status"] == "success"


@pytest.mark.asyncio
async def test_get_logs_pagination(test_session_factory, yaml_store, mock_plugin_registry):
    yaml_store.save("mock", {
        "display_name": "u",
        "credentials": {"token": "x"},
    })
    creds = yaml_store.list_all(plugin_id="mock")

    oc = Orchestrator(mock_plugin_registry, test_session_factory)
    for _ in range(3):
        await oc.sign_credential("mock", creds[0]["id"])

    rows, total = await get_logs(test_session_factory, page=1, page_size=2)
    assert len(rows) == 2
    assert total == 3

    rows, total = await get_logs(test_session_factory, page=2, page_size=2)
    assert len(rows) == 1


@pytest.mark.asyncio
async def test_get_logs_filter_by_status(test_session_factory, yaml_store, mock_plugin_registry):
    yaml_store.save("mock", {
        "display_name": "u",
        "credentials": {"token": "x"},
    })
    creds = yaml_store.list_all(plugin_id="mock")

    oc = Orchestrator(mock_plugin_registry, test_session_factory)
    await oc.sign_credential("mock", creds[0]["id"])

    rows, total = await get_logs(test_session_factory, status="success")
    assert total >= 1
    assert all(r["status"] == "success" for r in rows)

    rows, total = await get_logs(test_session_factory, status="failed")
    assert total == 0
