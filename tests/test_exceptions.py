from pysysctllib.exc import (
    FileNotFound,
    GenricError,
    NoSuchService,
    NotConfigured,
    NotInstalled,
    NotRunningOrRefused,
    PermissionError,
    returncodes_map,
)


def test_returncodes_map_exports_known_systemctl_exceptions():
    assert returncodes_map == {
        1: GenricError,
        4: NoSuchService,
        5: NotInstalled,
        6: NotConfigured,
        7: NotRunningOrRefused,
        126: PermissionError,
        127: FileNotFound,
    }
