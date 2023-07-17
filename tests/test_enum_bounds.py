from rgdps.constants.users import UserPrivileges


def test_user_privilege_bounds() -> None:
    """Tests that the user privileges can fit within a 128 bit unsigned
    integer."""

    for privilege in UserPrivileges:
        assert privilege.value < 1 << 128
        assert privilege.value >= 0
