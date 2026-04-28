"""AES-256-GCM 加解密工具."""

import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class EncryptionService:
    """对称加密服务.

    使用 AES-256-GCM 认证加密模式：
    - 密钥: 256-bit (32 bytes)
    - nonce: 随机 12 bytes
    - AAD: 可选附加认证数据 (防密文替换)
    """

    def __init__(self, key: bytes) -> None:
        if len(key) != 32:
            raise ValueError("Encryption key must be 32 bytes (256-bit)")
        self._aesgcm = AESGCM(key)

    def encrypt(self, plaintext: bytes, aad: bytes = b"") -> bytes:
        """加密.

        Returns:
            nonce (12 bytes) + ciphertext.
        """
        nonce = os.urandom(12)
        ciphertext = self._aesgcm.encrypt(nonce, plaintext, aad)
        return nonce + ciphertext

    def decrypt(self, ciphertext: bytes, aad: bytes = b"") -> bytes:
        """解密.

        Args:
            ciphertext: nonce (12 bytes) + encrypted data.

        Raises:
            InvalidTag: 密文被篡改或密钥错误。
        """
        nonce = ciphertext[:12]
        data = ciphertext[12:]
        return self._aesgcm.decrypt(nonce, data, aad)
