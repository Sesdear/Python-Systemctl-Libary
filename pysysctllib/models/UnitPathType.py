from enum import Enum

class UnitPathType(Enum):
    SYSTEM = "/etc/systemd/system/"
    USER = "~/.config/systemd/user/"
    SYSTEM_PM = "/lib/systemd/system/"
    USER_PM = "/usr/lib/systemd/user/"
    TEMP_SYSTEM = "/run/systemd/system/"
    TEMP_USER = "/run/systemd/user/"