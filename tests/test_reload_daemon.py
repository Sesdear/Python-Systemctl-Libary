import subprocess

import pytest

from pysysctllib.modules.reload_daemon import reload_daemon
from pysysctllib.exc import FileNotFound


def test_reload_daemon_runs_systemctl_daemon_reload(fake_sudo):
    assert reload_daemon() is True

    assert len(fake_sudo.calls) == 1
    call = fake_sudo.calls[0]
    assert call.args == ["systemctl", "daemon-reload"]
    assert call.kwargs == {
        "check": True,
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "text": True,
    }


def test_reload_daemon_maps_known_systemctl_return_code(fake_sudo):
    fake_sudo.queue_error(returncode=127)

    with pytest.raises(FileNotFound):
        reload_daemon()
