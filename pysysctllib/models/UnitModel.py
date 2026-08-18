from pysysctllib.models.UnitPathType import UnitPathType
class UnitModel():
    filename: str
    path_type: UnitPathType = UnitPathType.SYSTEM
    class Unit:
        Description: str
        After: str = "network.target"
    class Service:
        Type: str
        User: str
        WorkingDirectory: str
        ExecStart: str
        Environment: str = ""
        Restart: str = "on-failure"
        RestartSec: int = 5
    class Install:
        WantedBy: str = "multi-user.target"
        