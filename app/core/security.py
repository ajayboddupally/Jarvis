import hashlib
import hmac
import secrets


API_KEY_PREFIX = "jv_live_"


def generate_api_key() -> str:
    return API_KEY_PREFIX + secrets.token_urlsafe(32)


def digest_api_key(api_key: str, pepper: str) -> str:
    return hmac.new(pepper.encode("utf-8"), api_key.encode("utf-8"), hashlib.sha256).hexdigest()


def verify_api_key(api_key: str, expected_digest: str, pepper: str) -> bool:
    actual = digest_api_key(api_key, pepper)
    return hmac.compare_digest(actual, expected_digest)
