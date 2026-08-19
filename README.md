# Python Systemctl Library
<p align="center">
  <a href="https://pepy.tech/projects/pysysctllib">
    <img src="https://static.pepy.tech/personalized-badge/pysysctllib?period=total&units=NONE&left_color=BLACK&right_color=RED&left_text=Total+downloads" alt="Total Downloads">
  </a>
  <a href="https://pepy.tech/projects/pysysctllib">
    <img src="https://static.pepy.tech/personalized-badge/pysysctllib?period=monthly&units=NONE&left_color=BLACK&right_color=RED&left_text=Monthly+downloads" alt="Monthly Downloads">
  </a>
</p>
<p align="center">
  <img src="https://raw.githubusercontent.com/Sesdear/Python-Systemctl-Library/refs/heads/main/logo.svg" alt="Project Logo" width="240">
</p>

Python library providing a direct interface to **systemd** via `systemctl` for service management and inspection, with support for creating, reading, modifying and deleting unit files.

---

## Installation
Install from PyPI:
```bash
pip install pysysctllib
```
Or build from source:

```bash
git clone https://github.com/Sesdear/Python-Systemctl-Library.git
cd Python-Systemctl-Library
python -m venv .venv
source .venv/bin/activate
pip install poetry
poetry build
cd dist
pip install pysysctllib-*.whl
```

---

## Environment

* Python >= 3.11
* Linux with systemd
* `systemctl` available
* Appropriate privileges for service control

---

## Examples

### Start / stop an existing service
```python
from pysysctllib import Systemctl
from pysysctllib.exc import NoSuchService, PermissionError
from logging import info, error

svc = Systemctl("sshd.service")

try:
    if svc.start():
        info("Service started")
except NoSuchService:
    error("Service not found")
except PermissionError:
    error("Access denied")
```

### Check service state
```python
from pysysctllib import Systemctl

svc = Systemctl("sshd.service")

if svc.is_active():
    print("running")

if svc.is_enabled():
    print("enabled at boot")

status = svc.status()
print(status.active_state)   # "active"
print(status.sub_state)      # "running"
print(status.pid)            # 1234
print(status.unit_file_state)# "enabled"
print(status.service_path)   # "/etc/systemd/system/sshd.service"
```

### Create a new unit file and start it
```python
from pysysctllib import Systemctl, Systemd
from pysysctllib.exc import PermissionError
from pysysctllib.models import UnitModel, UnitPathType
from logging import info, error

def make_model() -> UnitModel:
    model = UnitModel()
    model.filename = "myapp.service"
    model.Unit.Description = "My App"
    model.Unit.After = "network.target"
    model.Service.Type = "simple"
    model.Service.User = "root"
    model.Service.WorkingDirectory = "/opt/myapp"
    model.Service.ExecStart = "/opt/myapp/run.sh"
    model.Service.Restart = "on-failure"
    model.Service.RestartSec = 5
    model.Install.WantedBy = "multi-user.target"
    model.path_type = UnitPathType.SYSTEM
    return model

sysd = Systemd()
svc = Systemctl("myapp.service")

try:
    if sysd.unit.create(make_model()):
        svc.reload_daemon()
        if svc.start():
            info("myapp started")
except PermissionError:
    error("Access denied")
```

### Enable / disable a service
```python
from pysysctllib import Systemctl

svc = Systemctl("myapp.service")
svc.enable()   # start at boot
svc.disable()  # remove from boot
```

### Mask / unmask a service
```python
from pysysctllib import Systemctl

svc = Systemctl("myapp.service")
svc.mask()    # prevent any start
svc.unmask()  # allow again
```

### Read and modify an existing unit file
```python
from pysysctllib import Systemd
from pysysctllib.models import UnitPathType

sysd = Systemd()

config_model = sysd.unit.read("myapp.service", UnitPathType.SYSTEM)
config_model.config.set("Service", "RestartSec", "10")

sysd.unit.write(config_model)
```

### Delete a unit file
```python
from pysysctllib import Systemd
from pysysctllib.models import UnitPathType
from pysysctllib.exc import FileNotFound, PermissionError

sysd = Systemd()

try:
    sysd.unit.delete("myapp.service", UnitPathType.SYSTEM)
except FileNotFound:
    print("Unit file not found")
except PermissionError:
    print("Access denied")
```

### Get all service properties
```python
from pysysctllib import Systemctl

props = Systemctl("sshd.service").properites()
print(props["MainPID"])
print(props["ActiveState"])
```

### List service dependencies
```python
from pysysctllib import Systemctl

deps = Systemctl("sshd.service").list_dependencies()
for dep in deps:
    print(dep)
```

---

## API

### `Systemd()`

Unit files controller for operations with systemd unit files.

#### `unit.create(model: UnitModel) -> bool`
Creates a unit file at the path defined by `model.path_type`.

#### `unit.delete(unit_filename: str, unit_path_type: UnitPathType) -> bool`
Deletes a unit file. Raises `FileNotFound` or `PermissionError`.

#### `unit.read(unit_filename: str, unit_path_type: UnitPathType) -> ConfigModel`
Reads a unit file into a `ConfigModel`. Raises `FileNotFound`, `PermissionError`, `ParsingError`.

#### `unit.write(config_model: ConfigModel) -> bool`
Writes changes back to the file stored in `config_model.path`. Raises `FileNotFound`, `PermissionError`.

#### `UnitPathType`

| Value | Path |
|---|---|
| `SYSTEM` | `/etc/systemd/system/` |
| `USER` | `~/.config/systemd/user/` |
| `SYSTEM_PM` | `/lib/systemd/system/` |
| `USER_PM` | `/usr/lib/systemd/user/` |
| `TEMP_SYSTEM` | `/run/systemd/system/` |
| `TEMP_USER` | `/run/systemd/user/` |

---

### `Systemctl(service_name: str)`

Service unit controller bound to a specific systemd unit.

#### Lifecycle

| Method | Returns | Description |
|---|---|---|
| `start()` | `bool` | Start the service |
| `stop()` | `bool` | Stop the service |
| `restart()` | `bool` | Restart the service |
| `reload()` | `bool` | Reload service config |

#### Enablement

| Method | Returns | Description |
|---|---|---|
| `enable()` | `bool` | Enable at boot |
| `disable()` | `bool` | Disable at boot |
| `is_enabled()` | `bool` | Check if enabled |

#### Masking

| Method | Returns | Description |
|---|---|---|
| `mask()` | `bool` | Mask the service |
| `unmask()` | `bool` | Unmask the service |
| `is_masked()` | `bool` | Check if masked |

#### State and Metadata

| Method | Returns | Description |
|---|---|---|
| `is_active()` | `bool` | Check if running |
| `status()` | `StatusModel` | Full status snapshot |
| `main_pid()` | `int` | Main process PID |
| `unit_file_state()` | `str` | `enabled`, `disabled`, `masked` |
| `properites()` | `dict` | All `systemctl show` properties |
| `list_dependencies()` | `list` | Service dependency list |

#### systemd Manager

| Method | Returns | Description |
|---|---|---|
| `reload_daemon()` | `bool` | Reload systemd manager config |

---

### `StatusModel`

Returned by `Systemctl.status()`.

| Field | Type | Description |
|---|---|---|
| `active_state` | `str` | `active`, `inactive`, `failed` |
| `sub_state` | `str` | `running`, `dead`, etc. |
| `unit_file_state` | `str` | `enabled`, `disabled`, `masked` |
| `pid` | `int` | Main PID |
| `service_path` | `str` | Path to the unit file |

---

### Exceptions

| Exception | Description |
|---|---|
| `GenricError` | Generic error, service likely failed to start |
| `NoSuchService` | Unit file does not exist in the system |
| `NotInstalled` | Program or service configuration not installed |
| `NotConfigured` | Service not configured |
| `NotRunningOrRefused` | Process link broken or start rejected by manager |
| `PermissionError` | Not enough permissions |
| `FileNotFound` | Unit file not found |

---

## ToDo
- [X] Create unit files from code
- [X] Delete existing systemd units
- [X] Modify existing systemd units

---

## License

Licensed under the [GPL-2.0 License](LICENSE).

---

## Author

[Sesdear](https://github.com/sesdear)
