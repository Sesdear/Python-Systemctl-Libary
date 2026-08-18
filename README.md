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


Python library providing a direct interface to **systemd** via `systemctl` for service management and inspection.


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

## Basic Usage

```python
from pysysctllib import Systemctl
from pysysctllib.exc import PermissonError
from logging import error, info

svc = Systemctl("sshd.service")
try:
  if svc.start():
      info("Service Start")
except PermssionError as e:
  error(e.code)

```

---

## API

### `Systemctl(service_name: str)`

Service unit controller bound to a specific systemd unit name.

### Lifecycle Operations

* `start() -> bool`
* `stop() -> bool`
* `restart() -> bool`
* `reload() -> bool`

### Enablement

* `enable() -> bool`
* `disable() -> bool`
* `is_enabled() -> bool`

### Masking

* `mask() -> bool`
* `unmask() -> bool`
* `is_masked() -> bool`

### State and Metadata

* `properties() -> dict` 
* `status() -> StatusModel`
* `is_active() -> bool`
* `main_pid() -> int`
* `unit_file_state() -> str`
* `list_dependencies() -> list`

### systemd Manager

* `reload_daemon() -> bool`

### Exceptions
* `GenricError` - Genric error. More often means, what serice down in start.
* `NoSuchService` - Serice with follow name doesn't exist in system (Does not exist `.service` file)
* `NotInstalled` - Program or configuration of service ot installed
* `NotConfigured` - Service not configured
* `NotRunningOrRefused` - Link to program not work or request to start rejected by manager
* `PermissionError` - Dont have permissons
* `FileNotFound` - Starting file not found
---
## ToDo
- [ ] Create unit files from code
---

## License

Licensed under the [GPL-2.0 License](LICENSE).

---

## Author

[Sesdear](https://github.com/sesdear)
