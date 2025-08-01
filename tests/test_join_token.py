import pytest

from bang_py.network.server import (
    generate_join_token,
    parse_join_token,
    DEFAULT_TOKEN_KEY,
)
from cryptography.fernet import InvalidToken


def test_generate_and_parse_token():
    token = generate_join_token("host", 1234, "code", DEFAULT_TOKEN_KEY)
    host, port, code = parse_join_token(token, DEFAULT_TOKEN_KEY)
    assert host == "host"
    assert port == 1234
    assert code == "code"


def test_token_invalid_key():
    token = generate_join_token("host", 1, "c", DEFAULT_TOKEN_KEY)
    bad_key = b"fh-IQhdbcUCrWTWyQ7WcM5VqCPU-ixXvSawvMkE415Q="
    with pytest.raises(InvalidToken):
        parse_join_token(token, bad_key)
