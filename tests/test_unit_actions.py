import importlib
import subprocess

import pytest

from pysysctllib.exc import NoSuchService


SERVICE = "demo.service"

ACTION_MODULES = [
    ("pysysctllib.modules.systemctl.unit.start", "start", "start"),
    ("pysysctllib.modules.systemctl.unit.stop", "stop", "stop"),
    ("pysysctllib.modules.systemctl.unit.restart", "restart", "restart"),
    ("pysysctllib.modules.systemctl.unit.enable", "enable", "enable"),
    ("pysysctllib.modules.systemctl.unit.disable", "disable", "disable"),
    ("pysysctllib.modules.systemctl.unit.reload", "reload", "reload"),
    ("pysysctllib.modules.systemctl.unit.mask", "mask", "mask"),
    ("pysysctllib.modules.systemctl.unit.unmask", "unmask", "unmask"),
]


def load_function(module_name: str, function_name: str):
    module = importlib.import_module(module_name)
    return getattr(module, function_name)


@pytest.mark.parametrize("module_name,function_name,systemctl_action", ACTION_MODULES)
def test_unit_action_runs_expected_systemctl_command(
    fake_sudo,
    module_name,
    function_name,
    systemctl_action,
):
    function = load_function(module_name, function_name)

    assert function(SERVICE) is True

    assert len(fake_sudo.calls) == 1
    call = fake_sudo.calls[0]
    assert call.args == ["systemctl", systemctl_action, SERVICE]
    assert call.kwargs == {"check": True}


@pytest.mark.parametrize("module_name,function_name,_systemctl_action", ACTION_MODULES)
def test_unit_action_maps_known_systemctl_return_code(
    fake_sudo,
    module_name,
    function_name,
    _systemctl_action,
):
    function = load_function(module_name, function_name)
    fake_sudo.queue_error(returncode=4)

    with pytest.raises(NoSuchService):
        function(SERVICE)


@pytest.mark.parametrize("module_name,function_name,_systemctl_action", ACTION_MODULES)
def test_unit_action_reraises_unknown_systemctl_return_code(
    fake_sudo,
    module_name,
    function_name,
    _systemctl_action,
):
    function = load_function(module_name, function_name)
    fake_sudo.queue_error(returncode=99)

    with pytest.raises(subprocess.CalledProcessError) as exc_info:
        function(SERVICE)

    assert exc_info.value.returncode == 99
