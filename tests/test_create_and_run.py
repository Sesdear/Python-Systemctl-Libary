import subprocess
from unittest.mock import MagicMock, patch, mock_open
import pytest

from pysysctllib import Systemd, Systemctl
from pysysctllib.models import UnitModel, UnitPathType
from pysysctllib.exc import NoSuchService, GenricError


SERVICE_NAME = "test-1.service"


def make_unit_model(path_type=UnitPathType.TEMP_SYSTEM) -> UnitModel:
    model = UnitModel()
    model.filename = SERVICE_NAME
    model.Unit.Description = "Test service"
    model.Unit.After = "network.target"
    model.Service.Type = "simple"
    model.Service.User = "root"
    model.Service.WorkingDirectory = "/tmp"
    model.Service.ExecStart = "/bin/sleep 10"
    model.Service.Restart = "on-failure"
    model.Service.RestartSec = 5
    model.Install.WantedBy = "multi-user.target"
    model.path_type = path_type
    return model


# ---------------------------------------------------------------------------
# Systemd.unit.create
# ---------------------------------------------------------------------------

class TestSystemdUnitCreate:
    def test_create_writes_unit_file(self, tmp_path):
        model = make_unit_model()
        model.path_type = UnitPathType.TEMP_SYSTEM

        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", mock_open()) as mocked_file:
            result = Systemd().unit.create(model)

        assert result is True
        mocked_file.assert_called_once_with(
            UnitPathType.TEMP_SYSTEM.value + SERVICE_NAME, "w"
        )

    def test_create_file_content_contains_exec_start(self):
        model = make_unit_model()
        written = []

        m = mock_open()
        m.return_value.__enter__.return_value.write.side_effect = written.append

        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", m):
            Systemd().unit.create(model)

        content = "".join(written)
        assert "ExecStart=/bin/sleep 10" in content
        assert "Description=Test service" in content
        assert "Type=simple" in content
        assert "WantedBy=multi-user.target" in content

    def test_create_returns_false_when_directory_missing(self):
        model = make_unit_model()

        with patch("os.path.exists", return_value=False):
            result = Systemd().unit.create(model)

        assert result is False

    def test_create_returns_false_on_os_error(self):
        model = make_unit_model()

        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", side_effect=OSError("permission denied")):
            result = Systemd().unit.create(model)

        assert result is False

    def test_create_uses_correct_path_for_user_type(self):
        model = make_unit_model(path_type=UnitPathType.USER)
        expected_path = UnitPathType.USER.value + SERVICE_NAME

        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", mock_open()) as mocked_file:
            Systemd().unit.create(model)

        mocked_file.assert_called_once_with(expected_path, "w")


# ---------------------------------------------------------------------------
# Systemctl.start after create (integration-style with fake subprocess)
# ---------------------------------------------------------------------------

class TestCreateThenStart:
    def test_create_then_start_calls_systemctl_start(self, fake_sudo):
        model = make_unit_model()

        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", mock_open()):
            created = Systemd().unit.create(model)

        assert created is True

        sysctl = Systemctl(SERVICE_NAME)
        result = sysctl.start()

        assert result is True
        assert len(fake_sudo.calls) == 1
        assert fake_sudo.calls[0].args == ["systemctl", "start", SERVICE_NAME]

    def test_create_then_stop(self, fake_sudo):
        model = make_unit_model()

        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", mock_open()):
            Systemd().unit.create(model)

        sysctl = Systemctl(SERVICE_NAME)
        result = sysctl.stop()

        assert result is True
        assert fake_sudo.calls[0].args == ["systemctl", "stop", SERVICE_NAME]

    def test_create_then_enable(self, fake_sudo):
        model = make_unit_model()

        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", mock_open()):
            Systemd().unit.create(model)

        result = Systemctl(SERVICE_NAME).enable()

        assert result is True
        assert fake_sudo.calls[0].args == ["systemctl", "enable", SERVICE_NAME]

    def test_start_raises_no_such_service_when_unit_missing(self, fake_sudo):
        fake_sudo.queue_error(returncode=4)

        with pytest.raises(NoSuchService):
            Systemctl(SERVICE_NAME).start()

    def test_start_raises_generic_error_on_returncode_1(self, fake_sudo):
        fake_sudo.queue_error(returncode=1)

        with pytest.raises(GenricError):
            Systemctl(SERVICE_NAME).start()

    def test_start_reraises_unknown_returncode(self, fake_sudo):
        fake_sudo.queue_error(returncode=99)

        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            Systemctl(SERVICE_NAME).start()

        assert exc_info.value.returncode == 99


# ---------------------------------------------------------------------------
# Systemctl.is_active / is_enabled after create
# ---------------------------------------------------------------------------

class TestIsActiveIsEnabled:
    def test_is_active_returns_true_when_active(self, fake_sudo):
        fake_sudo.queue_result(stdout="active\n")

        result = Systemctl(SERVICE_NAME).is_active()

        assert result is True
        assert fake_sudo.calls[0].args == [
            "systemctl", "show", SERVICE_NAME, "-p", "ActiveState", "--value"
        ]

    def test_is_active_returns_false_when_inactive(self, fake_sudo):
        fake_sudo.queue_result(stdout="inactive\n")

        result = Systemctl(SERVICE_NAME).is_active()

        assert result is False

    def test_is_enabled_returns_true_when_enabled(self, fake_sudo):
        fake_sudo.queue_result(stdout="enabled\n")

        result = Systemctl(SERVICE_NAME).is_enabled()

        assert result is True

    def test_is_enabled_returns_false_when_disabled(self, fake_sudo):
        fake_sudo.queue_result(stdout="disabled\n")

        result = Systemctl(SERVICE_NAME).is_enabled()

        assert result is False

    def test_is_active_raises_no_such_service(self, fake_sudo):
        fake_sudo.queue_error(returncode=4)

        with pytest.raises(NoSuchService):
            Systemctl(SERVICE_NAME).is_active()


# ---------------------------------------------------------------------------
# Systemctl.status
# ---------------------------------------------------------------------------

class TestStatus:
    def test_status_returns_model_with_correct_fields(self, fake_sudo):
        fake_sudo.queue_result(stdout=(
            "ActiveState=active\n"
            "SubState=running\n"
            "MainPID=1234\n"
            "UnitFileState=enabled\n"
            "FragmentPath=/etc/systemd/system/test-1.service\n"
        ))

        status = Systemctl(SERVICE_NAME).status()

        assert status.active_state == "active"
        assert status.sub_state == "running"
        assert status.pid == 1234
        assert status.unit_file_state == "enabled"
        assert status.service_path == "/etc/systemd/system/test-1.service"

    def test_status_raises_no_such_service(self, fake_sudo):
        fake_sudo.queue_error(returncode=4)

        with pytest.raises(NoSuchService):
            Systemctl(SERVICE_NAME).status()


# ---------------------------------------------------------------------------
# Systemctl.reload_daemon
# ---------------------------------------------------------------------------

class TestReloadDaemon:
    def test_reload_daemon_calls_correct_command(self, fake_sudo):
        fake_sudo.queue_result()

        result = Systemctl(SERVICE_NAME).reload_daemon()

        assert result is True
        assert fake_sudo.calls[0].args == ["systemctl", "daemon-reload"]
