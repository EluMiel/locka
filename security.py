from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass
from typing import Any

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


@dataclass(frozen=True)
class EncryptedPayload:
    """暗号化ファイルに保存するメタ情報つきペイロード"""
    v: int
    kdf: str
    iters: int
    salt_b64: str
    token: str


def _derive_fernet_key(master_password: str, salt: bytes, iters: int) -> bytes:
    """マスターパス＋saltからFernet鍵（base64 32bytes）を作る"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iters,
    )
    raw_key = kdf.derive(master_password.encode("utf-8"))
    return base64.urlsafe_b64encode(raw_key)


def encrypt_items(items: Any, master_password: str) -> bytes:
    """
    items（Pythonのlist/dict）を暗号化して、ファイル保存用bytesを返す
    """
    iters = 390_000
    salt = os.urandom(16)
    key = _derive_fernet_key(master_password, salt=salt, iters=iters)

    f = Fernet(key)
    plain = json.dumps(items, ensure_ascii=False).encode("utf-8")
    token = f.encrypt(plain).decode("utf-8")

    payload = EncryptedPayload(
        v=1,
        kdf="pbkdf2-sha256",
        iters=iters,
        salt_b64=base64.b64encode(salt).decode("ascii"),
        token=token,
    )
    return json.dumps(payload.__dict__, ensure_ascii=False, indent=2).encode("utf-8")


def decrypt_items(blob: bytes, master_password: str) -> Any:
    """
    暗号化ファイル(bytes)を復号して payload(dict) を返す
    """
    try:
        meta: dict[str, Any] = json.loads(blob.decode("utf-8"))

        salt = base64.b64decode(meta["salt_b64"])
        iters = int(meta["iters"])
        token = meta["token"].encode("utf-8")

        key = _derive_fernet_key(master_password, salt=salt, iters=iters)
        f = Fernet(key)

        plain = f.decrypt(token)
        data = json.loads(plain.decode("utf-8"))

        return data

    except InvalidToken:
        raise ValueError("マスターパスワードが異なるか、ファイルが壊れています。")
    except Exception as e:
        raise ValueError(f"復号に失敗しました。: {e}")
