from app.core.security import digest_api_key, generate_api_key, verify_api_key


def test_api_key_round_trip():
    pepper = "x" * 32
    key = generate_api_key()
    digest = digest_api_key(key, pepper)

    assert key.startswith("jv_live_")
    assert verify_api_key(key, digest, pepper)
    assert not verify_api_key("jv_live_wrong", digest, pepper)
