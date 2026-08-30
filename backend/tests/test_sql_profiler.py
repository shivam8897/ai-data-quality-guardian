import pytest

from profiler.sql_profiler import profile_table


@pytest.mark.parametrize("bad_name", [
    'orders"; DROP TABLE users; --',
    "orders; DROP TABLE users;",
    "1invalid_start",
    "with space",
    "",
])
def test_profile_table_rejects_invalid_identifiers(bad_name):
    with pytest.raises(ValueError):
        profile_table("postgresql://user:pass@localhost/db", bad_name)


def test_profile_table_accepts_valid_identifier_before_connecting():
    # An unreachable host should fail on the connection/query, not on validation —
    # confirms a well-formed table name passes the identifier check.
    with pytest.raises(Exception) as exc_info:
        profile_table("postgresql://user:pass@localhost:1/db", "valid_table")
    assert not isinstance(exc_info.value, ValueError)
