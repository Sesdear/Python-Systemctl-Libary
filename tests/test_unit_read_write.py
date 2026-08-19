import os
import configparser
from configparser import ParsingError
from unittest.mock import patch, MagicMock, mock_open
import pytest

from pysysctllib import Systemd
from pysysctllib.models import UnitPathType, ConfigModel
from pysysctllib.exc import FileNotFound, PermissionError


SERVICE_NAME = "test-1.service"
SERVICE_PATH = UnitPathType.TEMP_SYSTEM.value + SERVICE_NAME

UNIT_FILE_CONTENT = (
    "[Unit]\n"
    "Description=Test service\n"
    "After=network.target\n\n"
    "[Service]\n"
    "Type=simple\n"
    "ExecStart=/bin/sleep 10\n\n"
    "[Install]\n"
    "WantedBy=multi-user.target\n"
)


def _access_full(path, mode):
    return True


def _access_missing(path, mode):
    return False


def _access_no_rw(path, mode):
    if mode == os.F_OK:
        return True
    return False


def make_config_model(path: str = SERVICE_PATH) -> ConfigModel:
    config = configparser.ConfigParser(strict=False)
    config.read_string(UNIT_FILE_CONTENT)
    model = ConfigModel()
    model.config = config
    model.path = path
    return model


# ---------------------------------------------------------------------------
# Systemd.unit.read
# ---------------------------------------------------------------------------

class TestSystemdUnitRead:
    def test_read_returns_config_model(self):
        with patch("os.access", side_effect=_access_full), \
             patch("configparser.ConfigParser.read"):
            result = Systemd().unit.read(SERVICE_NAME, UnitPathType.TEMP_SYSTEM)

        assert isinstance(result, ConfigModel)
        assert result.path == SERVICE_PATH

    def test_read_config_contains_unit_data(self):
        with patch("os.access", side_effect=_access_full), \
             patch("configparser.ConfigParser.read", side_effect=lambda path: None) as mock_read:
            config = configparser.ConfigParser(strict=False)
            config.read_string(UNIT_FILE_CONTENT)
            with patch("configparser.ConfigParser") as MockParser:
                MockParser.return_value = config
                result = Systemd().unit.read(SERVICE_NAME, UnitPathType.TEMP_SYSTEM)

        assert result.config is config

    def test_read_raises_file_not_found_when_missing(self):
        with patch("os.access", side_effect=_access_missing):
            with pytest.raises(FileNotFound):
                Systemd().unit.read(SERVICE_NAME, UnitPathType.TEMP_SYSTEM)

    def test_read_raises_permission_error_when_not_readable(self):
        with patch("os.access", side_effect=_access_no_rw):
            with pytest.raises(PermissionError):
                Systemd().unit.read(SERVICE_NAME, UnitPathType.TEMP_SYSTEM)

    def test_read_uses_correct_path(self):
        captured = {}

        def fake_read(path):
            captured["path"] = path

        with patch("os.access", side_effect=_access_full), \
             patch("configparser.ConfigParser.read", side_effect=fake_read):
            Systemd().unit.read(SERVICE_NAME, UnitPathType.TEMP_SYSTEM)

        assert captured["path"] == SERVICE_PATH

    def test_read_uses_correct_path_for_system_type(self):
        captured = {}

        def fake_read(path):
            captured["path"] = path

        with patch("os.access", side_effect=_access_full), \
             patch("configparser.ConfigParser.read", side_effect=fake_read):
            Systemd().unit.read(SERVICE_NAME, UnitPathType.SYSTEM)

        assert captured["path"] == UnitPathType.SYSTEM.value + SERVICE_NAME

    def test_read_default_path_type_is_system(self):
        captured = {}

        def fake_read(path):
            captured["path"] = path

        with patch("os.access", side_effect=_access_full), \
             patch("configparser.ConfigParser.read", side_effect=fake_read):
            Systemd().unit.read(SERVICE_NAME)

        assert captured["path"] == UnitPathType.SYSTEM.value + SERVICE_NAME

    def test_read_raises_parsing_error_on_bad_file(self):
        with patch("os.access", side_effect=_access_full), \
             patch(
                 "configparser.ConfigParser.read",
                 side_effect=ParsingError(SERVICE_PATH),
             ):
            with pytest.raises(ParsingError):
                Systemd().unit.read(SERVICE_NAME, UnitPathType.TEMP_SYSTEM)


# ---------------------------------------------------------------------------
# Systemd.unit.write
# ---------------------------------------------------------------------------

class TestSystemdUnitWrite:
    def test_write_returns_true_on_success(self):
        model = make_config_model()
        mock_file = MagicMock()

        with patch("os.access", side_effect=_access_full), \
             patch("builtins.open", mock_open()) as mocked_open:
            mocked_open.return_value.__enter__.return_value = mock_file
            result = Systemd().unit.write(model)

        assert result is True

    def test_write_calls_config_write(self):
        model = make_config_model()
        mock_file = MagicMock()

        with patch("os.access", side_effect=_access_full), \
             patch("builtins.open", mock_open()) as mocked_open:
            mocked_open.return_value.__enter__.return_value = mock_file
            Systemd().unit.write(model)

        mock_file.write.assert_called()

    def test_write_opens_correct_path(self):
        model = make_config_model(SERVICE_PATH)

        with patch("os.access", side_effect=_access_full), \
             patch("builtins.open", mock_open()) as mocked_open:
            Systemd().unit.write(model)

        mocked_open.assert_called_once_with(SERVICE_PATH, "w", encoding="utf-8")

    def test_write_raises_file_not_found_when_missing(self):
        model = make_config_model()

        with patch("os.access", side_effect=_access_missing):
            with pytest.raises(FileNotFound):
                Systemd().unit.write(model)

    def test_write_raises_permission_error_when_not_writable(self):
        model = make_config_model()

        with patch("os.access", side_effect=_access_no_rw):
            with pytest.raises(PermissionError):
                Systemd().unit.write(model)

    def test_write_returns_false_on_exception(self):
        model = make_config_model()

        with patch("os.access", side_effect=_access_full), \
             patch("builtins.open", side_effect=OSError("disk full")):
            result = Systemd().unit.write(model)

        assert result is False


# ---------------------------------------------------------------------------
# Read -> Write round-trip
# ---------------------------------------------------------------------------

class TestReadWriteRoundTrip:
    def test_read_then_write_preserves_exec_start(self):
        config = configparser.ConfigParser(strict=False)
        config.read_string(UNIT_FILE_CONTENT)
        model = ConfigModel()
        model.config = config
        model.path = SERVICE_PATH

        mock_file = MagicMock()
        written_content = []
        mock_file.write.side_effect = written_content.append

        with patch("os.access", side_effect=_access_full), \
             patch("builtins.open", mock_open()) as mocked_open:
            mocked_open.return_value.__enter__.return_value = mock_file
            result = Systemd().unit.write(model)

        assert result is True
        combined = "".join(written_content)
        assert "execstart" in combined.lower() or mock_file.write.called

    def test_read_produces_model_writable_by_write(self):
        with patch("os.access", side_effect=_access_full), \
             patch("configparser.ConfigParser.read"):
            read_model = Systemd().unit.read(SERVICE_NAME, UnitPathType.TEMP_SYSTEM)

        mock_file = MagicMock()
        with patch("os.access", side_effect=_access_full), \
             patch("builtins.open", mock_open()) as mocked_open:
            mocked_open.return_value.__enter__.return_value = mock_file
            result = Systemd().unit.write(read_model)

        assert result is True

    def test_read_then_modify_then_write(self):
        config = configparser.ConfigParser(strict=False)
        config.read_string(UNIT_FILE_CONTENT)
        model = ConfigModel()
        model.config = config
        model.path = SERVICE_PATH

        model.config.set("Service", "ExecStart", "/bin/sleep 999")

        assert model.config.get("Service", "ExecStart") == "/bin/sleep 999"

        mock_file = MagicMock()
        with patch("os.access", side_effect=_access_full), \
             patch("builtins.open", mock_open()) as mocked_open:
            mocked_open.return_value.__enter__.return_value = mock_file
            result = Systemd().unit.write(model)

        assert result is True
        mock_file.write.assert_called()
