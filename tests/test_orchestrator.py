import pytest
from app.core.orchestrator import Orchestrator


@pytest.mark.asyncio
async def test_sign_credential_writes_log(test_session_factory, yaml_store, mock_plugin_registry):
    yaml_store.save("mock", {
        "display_name": "test-user",
        "credentials": {"token": "abc"},
    })

    oc = Orchestrator(mock_plugin_registry, test_session_factory)
    creds = yaml_store.list_all(plugin_id="mock")

    logs = await oc.sign_credential("mock", creds[0]["id"])
    assert len(logs) >= 1
    assert logs[0]["plugin_id"] == "mock"
    assert logs[0]["game_id"] == "game1"
    assert logs[0]["status"] == "success"
    assert logs[0]["reward"] == "100 coins"
    assert logs[0]["message"] == "OK"


@pytest.mark.asyncio
async def test_sign_all_writes_multiple_logs(test_session_factory, yaml_store, mock_plugin_registry):
    yaml_store.save("mock", {
        "display_name": "user1",
        "credentials": {"token": "a"},
    })
    yaml_store.save("mock", {
        "display_name": "user2",
        "credentials": {"token": "b"},
    })

    oc = Orchestrator(mock_plugin_registry, test_session_factory)
    logs = await oc.sign_all()
    assert len(logs) >= 2


@pytest.mark.asyncio
async def test_sign_unknown_plugin_raises(test_session_factory, yaml_store, mock_plugin_registry):
    yaml_store.save("mock", {
        "display_name": "u",
        "credentials": {"token": "x"},
    })
    creds = yaml_store.list_all(plugin_id="mock")

    oc = Orchestrator(mock_plugin_registry, test_session_factory)
    with pytest.raises(ValueError, match="Unknown plugin"):
        await oc.sign_credential("nonexistent", creds[0]["id"])
