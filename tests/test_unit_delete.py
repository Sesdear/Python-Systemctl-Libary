import os
from unittest.mock import patch
import pytest

from pysysctllib import Systemd
from pysysctllib.models import UnitPathType
from pysysctllib.exc import FileNotFound, PermissionError


SERVICE_NAME = "test-1.service"


def _access_full(path, mode):
    return True


def _access_missing(path, mode):
    return False


def _access_no_write(path, mode):
    if mode == os.F_OK:
        return True
    return False


# ---------------------------------------------------------------------------
# Systemd.unit.delete
# ---------------------------------------------------------------------------

class TestSystemdUnitDelete:
    def test_delete_removes_file_and_returns_true(self):
        with patch("os.access", side_effect=_access_full), \
             patch("os.remove") as mock_remove:
            result = Systemd().unit.delete(SERVICE_NAME, UnitPathType.TEMP_SYSTEM)

        assert result is True
        mock_remove.assert_called_once_with(UnitPathType.TEMP_SYSTEM.value + SERVICE_NAME)

    def test_delete_raises_file_not_found_when_missing(self):
        with patch("os.access", side_effect=_access_missing):
            with pytest.raises(FileNotFound):
                Systemd().unit.delete(SERVICE_NAME, UnitPathType.TEMP_SYSTEM)

    def test_delete_raises_permission_error_when_not_writable(self):
        with patch("os.access", side_effect=_access_no_write):
            with pytest.raises(PermissionError):
                Systemd().unit.delete(SERVICE_NAME, UnitPathType.TEMP_SYSTEM)

    def test_delete_uses_correct_path_for_system_type(self):
        with patch("os.access", side_effect=_access_full), \
             patch("os.remove") as mock_remove:
            Systemd().unit.delete(SERVICE_NAME, UnitPathType.SYSTEM)

        mock_remove.assert_called_once_with(UnitPathType.SYSTEM.value + SERVICE_NAME)

    def test_delete_uses_correct_path_for_user_type(self):
        with patch("os.access", side_effect=_access_full), \
             patch("os.remove") as mock_remove:
            Systemd().unit.delete(SERVICE_NAME, UnitPathType.USER)

        mock_remove.assert_called_once_with(UnitPathType.USER.value + SERVICE_NAME)

    def test_delete_raises_file_not_found_on_os_remove_error(self):
        with patch("os.access", side_effect=_access_full), \
             patch("os.remove", side_effect=FileNotFoundError):
            with pytest.raises(FileNotFound):
                Systemd().unit.delete(SERVICE_NAME, UnitPathType.TEMP_SYSTEM)

    def test_delete_raises_permission_error_on_os_remove_permission_error(self):
        with patch("os.access", side_effect=_access_full), \
             patch("os.remove", side_effect=PermissionError):
            with pytest.raises(PermissionError):
                Systemd().unit.delete(SERVICE_NAME, UnitPathType.TEMP_SYSTEM)

    def test_delete_default_path_type_is_system(self):
        with patch("os.access", side_effect=_access_full), \
             patch("os.remove") as mock_remove:
            result = Systemd().unit.delete(SERVICE_NAME)

        assert result is True
        mock_remove.assert_called_once_with(UnitPathType.SYSTEM.value + SERVICE_NAME)
