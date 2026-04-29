import pytest
from app.core.vault import Vault, VaultLockedError


@pytest.mark.asyncio
async def test_first_time_unlock(test_session_factory):
    v = Vault(test_session_factory)
    ok, is_first = await v.unlock("abcdefgh")
    assert ok
    assert is_first
    assert v.is_unlocked
    assert v.session_id is not None


@pytest.mark.asyncio
async def test_unlock_wrong_password(vault):
    vault.lock()
    assert not vault.is_unlocked
    ok, is_first = await vault.unlock("wrong-password")
    assert not ok
    assert not is_first
    assert not vault.is_unlocked


@pytest.mark.asyncio
async def test_lock(vault):
    assert vault.is_unlocked
    vault.lock()
    assert not vault.is_unlocked
    assert vault.session_id is None


@pytest.mark.asyncio
async def test_lock_then_unlock_again(vault):
    vault.lock()
    ok, is_first = await vault.unlock("abcdefgh")
    assert ok
    assert not is_first
    assert vault.is_unlocked


@pytest.mark.asyncio
async def test_save_and_get_credential(vault):
    await vault.save_credential("mock", {
        "display_name": "my-account",
        "credentials": {"token": "abc"},
        "enabled_games": ["game1"],
        "is_enabled": True,
    })
    creds = vault.get_credentials("mock")
    assert len(creds) == 1
    assert creds[0]["display_name"] == "my-account"
    assert creds[0]["credentials"] == {"token": "abc"}
    assert creds[0]["enabled_games"] == ["game1"]


@pytest.mark.asyncio
async def test_save_credential_assigns_id_and_plugin_id(vault):
    cid = await vault.save_credential("mock", {
        "display_name": "acc1",
        "credentials": {"t": "1"},
    })
    assert cid > 0
    creds = vault.get_credentials("mock")
    assert creds[0]["id"] == cid
    assert creds[0]["plugin_id"] == "mock"


@pytest.mark.asyncio
async def test_list_summaries_no_sensitive_data(vault):
    await vault.save_credential("mock", {
        "display_name": "acc1",
        "credentials": {"token": "secret"},
        "enabled_games": ["game1"],
        "is_enabled": True,
    })
    summaries = vault.list_summaries()
    assert len(summaries) == 1
    s = summaries[0]
    assert s["display_name"] == "acc1"
    assert "credentials" not in s
    assert "token" not in str(s)


@pytest.mark.asyncio
async def test_get_all_credentials(vault):
    await vault.save_credential("plugin-a", {
        "display_name": "a1",
        "credentials": {"t": "1"},
    })
    await vault.save_credential("plugin-b", {
        "display_name": "b1",
        "credentials": {"t": "2"},
    })
    all_creds = vault.get_all_credentials()
    assert "plugin-a" in all_creds
    assert "plugin-b" in all_creds
    assert len(all_creds["plugin-a"]) == 1
    assert len(all_creds["plugin-b"]) == 1


@pytest.mark.asyncio
async def test_delete_credential(vault):
    cid = await vault.save_credential("mock", {
        "display_name": "to-delete",
        "credentials": {"x": "1"},
    })
    assert len(vault.get_credentials("mock")) == 1

    await vault.delete_credential(cid)
    assert len(vault.get_credentials("mock")) == 0


@pytest.mark.asyncio
async def test_delete_nonexistent_does_not_raise(vault):
    await vault.delete_credential(99999)


@pytest.mark.asyncio
async def test_change_password(vault):
    await vault.save_credential("mock", {
        "display_name": "acc",
        "credentials": {"token": "s"},
    })
    success = await vault.change_password("abcdefgh", "new-password-123")
    assert success
    assert vault.is_unlocked

    creds = vault.get_credentials("mock")
    assert creds[0]["credentials"] == {"token": "s"}

    vault.lock()
    ok, _ = await vault.unlock("new-password-123")
    assert ok


@pytest.mark.asyncio
async def test_change_password_wrong_old(vault):
    success = await vault.change_password("wrong-old", "new-pass")
    assert not success


@pytest.mark.asyncio
async def test_vault_locked_error_on_get_credentials(test_session_factory):
    v = Vault(test_session_factory)
    with pytest.raises(VaultLockedError):
        v.get_credentials("any")


@pytest.mark.asyncio
async def test_vault_locked_error_on_save(test_session_factory):
    v = Vault(test_session_factory)
    with pytest.raises(VaultLockedError):
        await v.save_credential("any", {"display_name": "x"})


@pytest.mark.asyncio
async def test_vault_locked_error_on_summaries(test_session_factory):
    v = Vault(test_session_factory)
    with pytest.raises(VaultLockedError):
        v.list_summaries()


@pytest.mark.asyncio
async def test_credential_survives_relock(vault):
    cid = await vault.save_credential("mock", {
        "display_name": "persist",
        "credentials": {"token": "abc"},
    })
    vault.lock()
    ok, _ = await vault.unlock("abcdefgh")
    assert ok
    creds = vault.get_credentials("mock")
    assert len(creds) == 1
    assert creds[0]["id"] == cid
    assert creds[0]["credentials"] == {"token": "abc"}


@pytest.mark.asyncio
async def test_update_existing_credential(vault):
    cid = await vault.save_credential("mock", {
        "display_name": "old-name",
        "credentials": {"token": "old"},
    })
    await vault.save_credential("mock", {
        "id": cid,
        "display_name": "new-name",
        "credentials": {"token": "new"},
    })
    creds = vault.get_credentials("mock")
    assert len(creds) == 1
    assert creds[0]["display_name"] == "new-name"
    assert creds[0]["credentials"] == {"token": "new"}
