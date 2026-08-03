import subprocess

import pytest

from pysysctllib.exc import PermissionError
from pysysctllib.modules.systemctl.unit.is_active import is_active
from pysysctllib.modules.systemctl.unit.is_enabled import is_enabled
from pysysctllib.modules.systemctl.unit.is_masked import is_masked
from pysysctllib.modules.systemctl.unit.list_dependencies import list_dependencies
from pysysctllib.modules.systemctl.unit.main_pid import main_pid
from pysysctllib.modules.systemctl.unit.properties import show
from pysysctllib.modules.systemctl.unit.status import status
from pysysctllib.modules.systemctl.unit.unit_file_state import unit_file_state


SERVICE = "demo.service"


@pytest.mark.parametrize(
    "function,stdout,expected,command",
    [
        (
            is_enabled,
            "enabled\n",
            True,
            ["systemctl", "is-enabled", SERVICE],
        ),
        (
            is_enabled,
            "disabled\n",
            False,
            ["systemctl", "is-enabled", SERVICE],
        ),
        (
            is_active,
            "active\n",
            True,
            ["systemctl", "show", SERVICE, "-p", "ActiveState", "--value"],
        ),
        (
            is_active,
            "inactive\n",
            False,
            ["systemctl", "show", SERVICE, "-p", "ActiveState", "--value"],
        ),
        (
            is_masked,
            "masked\n",
            True,
            ["systemctl", "is-masked", SERVICE, "-p", ""],
        ),
        (
            is_masked,
            "unmasked\n",
            False,
            ["systemctl", "is-masked", SERVICE, "-p", ""],
        ),
    ],
)
def test_boolean_query_modules_parse_systemctl_output(
    fake_sudo,
    function,
    stdout,
    expected,
    command,
):
    fake_sudo.queue_result(stdout=stdout)

    assert function(SERVICE) is expected

    assert len(fake_sudo.calls) == 1
    call = fake_sudo.calls[0]
    assert call.args == command
    assert call.kwargs == {
        "check": True,
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "text": True,
    }


@pytest.mark.parametrize("function", [is_enabled, is_active, is_masked])
def test_boolean_query_modules_map_known_systemctl_return_codes(fake_sudo, function):
    fake_sudo.queue_error(returncode=126)

    with pytest.raises(PermissionError):
        function(SERVICE)


def test_list_dependencies_filters_root_unit_and_blank_lines(fake_sudo):
    fake_sudo.queue_result(
        stdout="""
        demo.service
        network.target

        postgresql.service
        """,
    )

    assert list_dependencies(SERVICE) == ["network.target", "postgresql.service"]

    assert len(fake_sudo.calls) == 1
    call = fake_sudo.calls[0]
    assert call.args == [
        "systemctl",
        "list-dependencies",
        SERVICE,
        "--plain",
        "--no-pager",
        "--output",
        "json",
    ]
    assert call.kwargs == {
        "check": True,
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "text": True,
    }


def test_properties_show_returns_key_value_mapping(fake_sudo):
    fake_sudo.queue_result(
        stdout="Description=Demo Service\nMainPID=4242\nFragmentPath=/etc/systemd/demo.service\n",
    )

    assert show(SERVICE) == {
        "Description": "Demo Service",
        "MainPID": "4242",
        "FragmentPath": "/etc/systemd/demo.service",
    }

    assert len(fake_sudo.calls) == 1
    call = fake_sudo.calls[0]
    assert call.args == ["systemctl", "show", SERVICE]
    assert call.kwargs["stdout"] is subprocess.PIPE
    assert call.kwargs["stderr"] is subprocess.PIPE
    assert call.kwargs["text"] is True


def test_unit_file_state_returns_value(fake_sudo):
    fake_sudo.queue_result(stdout="UnitFileState=enabled\n")

    assert unit_file_state(SERVICE) == "enabled"

    assert fake_sudo.calls[0].args == [
        "systemctl",
        "show",
        SERVICE,
        "-p",
        "UnitFileState",
    ]
    assert fake_sudo.calls[0].kwargs == {
        "check": True,
        "capture_output": True,
        "text": True,
    }


def test_main_pid_returns_integer_value(fake_sudo):
    fake_sudo.queue_result(stdout="MainPID=4242\n")

    assert main_pid(SERVICE) == 4242

    assert fake_sudo.calls[0].args == [
        "systemctl",
        "show",
        SERVICE,
        "-p",
        "MainPID",
    ]
    assert fake_sudo.calls[0].kwargs == {
        "check": True,
        "capture_output": True,
        "text": True,
    }


def test_status_returns_status_model(fake_sudo):
    fake_sudo.queue_result(
        stdout=(
            "ActiveState=active\n"
            "SubState=running\n"
            "MainPID=4242\n"
            "UnitFileState=enabled\n"
            "FragmentPath=/etc/systemd/system/demo.service\n"
        ),
    )

    result = status(SERVICE)

    assert result.active_state == "active"
    assert result.sub_state == "running"
    assert result.pid == 4242
    assert result.unit_file_state == "enabled"
    assert result.service_path == "/etc/systemd/system/demo.service"
    assert fake_sudo.calls[0].args == [
        "systemctl",
        "show",
        SERVICE,
        "-p",
        "ActiveState",
        "-p",
        "SubState",
        "-p",
        "MainPID",
        "-p",
        "UnitFileState",
        "-p",
        "FragmentPath",
    ]
    assert fake_sudo.calls[0].kwargs == {
        "check": True,
        "capture_output": True,
        "text": True,
    }
