"""Credential Vault — 凭据的加密存储与内存缓存.

安全模型:
  用户密码 → bcrypt 验证 → Argon2id 派生密钥 → AES-256-GCM 加密凭据
  解密后的凭据仅存于内存 (_cache)，锁定或退出时销毁。
"""

import json
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.auth import (
    derive_encryption_key,
    generate_session_id,
    hash_password,
    verify_password,
)
from app.models.config import Config
from app.models.credential import Credential
from app.utils.encryption import EncryptionService

logger = logging.getLogger("app.vault")


class Vault:
    """凭据保险库.

    状态机:
      LOCKED ──[unlock(pwd)]──> UNLOCKED
                    ↑                      │
                    └──────[lock()]────────┘
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory
        self._decrypt_key: bytes | None = None
        self._cache: dict[str, list[dict]] = {}  # plugin_id → list of decrypted credentials
        self._session_id: str | None = None

    # --------------- Public API ---------------

    async def unlock(self, password: str) -> tuple[bool, bool]:
        """解锁保险库.

        Args:
            password: 用户输入的密码。

        Returns:
            (success, is_first_time)
        """
        is_first_time = await self._is_first_time()

        if is_first_time:
            await self._initialize(password)
        else:
            if not await self._check_password(password):
                return False, False

        # 派生加密密钥
        self._decrypt_key = derive_encryption_key(password)

        # 解密所有凭据到内存缓存
        await self._load_all_credentials()

        # 生成会话 ID
        self._session_id = generate_session_id()

        logger.info("Vault unlocked, session=%s", self._session_id)
        return True, is_first_time

    def lock(self) -> None:
        """锁定保险库：销毁密钥和内存缓存."""
        self._decrypt_key = None
        self._cache.clear()
        self._session_id = None
        logger.info("Vault locked")

    @property
    def is_unlocked(self) -> bool:
        return self._decrypt_key is not None

    @property
    def session_id(self) -> str | None:
        return self._session_id

    async def is_password_set(self) -> bool:
        return not await self._is_first_time()

    async def ensure_default_password(self) -> bool:
        """首次启动时设置默认密码 12345678."""
        if await self._is_first_time():
            await self._initialize("12345678")
            logger.info("已设置默认密码 12345678")
            return True
        return False

    async def change_password(self, old_password: str, new_password: str) -> bool:
        """修改密码，重新加密所有凭据."""
        if not self.is_unlocked:
            raise VaultLockedError()

        # 验证旧密码
        if not await self._check_password(old_password):
            return False

        # 用新密码派生密钥
        new_key = derive_encryption_key(new_password)

        # 重新加密所有凭据
        old_enc = EncryptionService(self._decrypt_key)
        new_enc = EncryptionService(new_key)

        async with self._session_factory() as session:
            stmt = select(Credential)
            r = await session.execute(stmt)
            rows = r.scalars().all()

            for row in rows:
                plaintext = old_enc.decrypt(row.encrypted_data)
                row.encrypted_data = new_enc.encrypt(plaintext)

            # 更新密码哈希
            hash_row = await session.get(Config, "password_hash")
            if hash_row:
                hash_row.value = hash_password(new_password)

            await session.commit()

        # 更新内存密钥
        self._decrypt_key = new_key
        logger.info("密码已修改")
        return True

    def get_credentials(self, plugin_id: str) -> list[dict]:
        """获取某个插件的所有解密凭据（内存缓存）."""
        if not self.is_unlocked:
            raise VaultLockedError()
        return self._cache.get(plugin_id, [])

    def get_all_credentials(self) -> dict[str, list[dict]]:
        """获取所有解密凭据."""
        if not self.is_unlocked:
            raise VaultLockedError()
        return self._cache.copy()

    def list_summaries(self) -> list[dict]:
        """凭据摘要列表（无敏感字段，供前端展示）."""
        if not self.is_unlocked:
            raise VaultLockedError()
        result = []
        for plugin_id, creds in self._cache.items():
            for cred in creds:
                result.append({
                    "id": cred["id"],
                    "plugin_id": plugin_id,
                    "display_name": cred.get("display_name", ""),
                    "enabled_games": cred.get("enabled_games", []),
                    "is_enabled": cred.get("is_enabled", True),
                })
        return result

    async def save_credential(self, plugin_id: str, credential_data: dict) -> int:
        """加密并保存凭据到数据库.

        Args:
            plugin_id: 插件标识。
            credential_data: 明文凭据字典。需包含: display_name, credentials, enabled_games。

        Returns:
            新建记录的 ID。
        """
        if not self.is_unlocked:
            raise VaultLockedError()

        cred_id = credential_data.get("id")
        plaintext = json.dumps(credential_data, ensure_ascii=False).encode()

        assert self._decrypt_key is not None
        enc = EncryptionService(self._decrypt_key)
        ciphertext = enc.encrypt(plaintext)

        async with self._session_factory() as session:
            if cred_id:
                stmt = select(Credential).where(Credential.id == cred_id)
                r = await session.execute(stmt)
                row = r.scalar_one_or_none()
                if row is None:
                    raise ValueError(f"Credential {cred_id} not found")
                row.display_name = credential_data.get("display_name", "")
                row.enabled_games = credential_data.get("enabled_games", [])
                row.is_enabled = credential_data.get("is_enabled", True)
                row.encrypted_data = ciphertext
            else:
                row = Credential(
                    plugin_id=plugin_id,
                    display_name=credential_data.get("display_name", ""),
                    encrypted_data=ciphertext,
                    enabled_games=credential_data.get("enabled_games", []),
                    is_enabled=credential_data.get("is_enabled", True),
                )
                session.add(row)

            await session.commit()
            await session.refresh(row)
            new_id = row.id

        # 更新内存缓存
        credential_data["id"] = new_id
        credential_data["plugin_id"] = plugin_id
        self._cache.setdefault(plugin_id, []).append(credential_data)

        return new_id

    async def delete_credential(self, credential_id: int) -> None:
        """删除凭据."""
        async with self._session_factory() as session:
            stmt = select(Credential).where(Credential.id == credential_id)
            r = await session.execute(stmt)
            row = r.scalar_one_or_none()
            if row:
                await session.delete(row)
                await session.commit()

        # 从缓存移除
        for plugin_id, creds in self._cache.items():
            self._cache[plugin_id] = [c for c in creds if c["id"] != credential_id]

    # --------------- Internal ---------------

    async def _is_first_time(self) -> bool:
        async with self._session_factory() as session:
            stmt = select(Config).where(Config.key == "password_hash")
            r = await session.execute(stmt)
            row = r.scalar_one_or_none()
            return row is None or not row.value

    async def _initialize(self, password: str) -> None:
        """首次设置密码."""
        hashed = hash_password(password)
        async with self._session_factory() as session:
            row = Config(key="password_hash", value=hashed)
            session.add(row)
            await session.commit()
        logger.info("Password initialized")

    async def _check_password(self, password: str) -> bool:
        async with self._session_factory() as session:
            stmt = select(Config).where(Config.key == "password_hash")
            r = await session.execute(stmt)
            row = r.scalar_one_or_none()
            if row is None or not row.value:
                return False
            return verify_password(password, row.value)

    async def _load_all_credentials(self) -> None:
        """从数据库加载并解密所有凭据到内存缓存."""
        self._cache.clear()
        assert self._decrypt_key is not None
        enc = EncryptionService(self._decrypt_key)

        async with self._session_factory() as session:
            stmt = select(Credential).where(Credential.is_enabled).order_by(Credential.sort_order)
            r = await session.execute(stmt)
            rows = r.scalars().all()

        for row in rows:
            try:
                plaintext = enc.decrypt(row.encrypted_data)
                data = json.loads(plaintext)
                data["id"] = row.id
                data["plugin_id"] = row.plugin_id
                data["display_name"] = row.display_name
                data["enabled_games"] = row.enabled_games
                data["is_enabled"] = row.is_enabled
                self._cache.setdefault(row.plugin_id, []).append(data)
            except Exception as e:
                logger.warning(
                    "Failed to decrypt credential %d (%s): %s",
                    row.id, row.display_name, e,
                )


class VaultLockedError(Exception):
    """凭据库已锁定."""
    pass
