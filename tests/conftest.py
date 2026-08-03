from dataclasses import dataclass
from types import SimpleNamespace
import subprocess

import pytest


@dataclass
class RunCall:
    args: list[str]
    kwargs: dict


class FakeSubprocessRun:
    def __init__(self):
        self.calls: list[RunCall] = []
        self._results: list[object] = []

    def queue_result(self, *, stdout: str = "", stderr: str = "", returncode: int = 0):
        result = SimpleNamespace(
            args=None,
            returncode=returncode,
            stdout=stdout,
            stderr=stderr,
        )
        self._results.append(result)
        return result

    def queue_error(self, returncode: int, cmd=None):
        error = subprocess.CalledProcessError(
            returncode=returncode,
            cmd=cmd or ["systemctl"],
        )
        self._results.append(error)
        return error

    def __call__(self, args, **kwargs):
        args = list(args)
        self.calls.append(RunCall(args=args, kwargs=dict(kwargs)))

        if not self._results:
            return SimpleNamespace(args=args, returncode=0, stdout="", stderr="")

        result = self._results.pop(0)
        if isinstance(result, BaseException):
            raise result

        result.args = args
        return result


@pytest.fixture(autouse=True)
def block_real_subprocess_run(monkeypatch):
    def blocked_run(*_args, **_kwargs):
        raise AssertionError(
            "subprocess.run must be faked in tests; real systemctl was not called"
        )

    monkeypatch.setattr(subprocess, "run", blocked_run)


@pytest.fixture
def fake_sudo(monkeypatch):
    fake = FakeSubprocessRun()
    monkeypatch.setattr(subprocess, "run", fake)
    return fake
