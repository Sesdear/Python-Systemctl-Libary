class GenricError(Exception):
    desc: str = """Genric error. More often means, what serice down in start."""
class NoSuchService(Exception):
    desc: str = """Serice with follow name doesn't exist in system (Does not exist `.service` file)"""
class NotInstalled(Exception):
    des: str = """Program or configuration of service ot installed"""
class NotConfigured(Exception):
    desc: str = """Service not configured"""
class NotRunningOrRefused(Exception):
    desc: str = """Link to program not work or request to start rejected by manager"""

# PolicyKit Exceptions
class PermissonError(Exception):
    desc: str = """Dont have permissons"""
class FileNotFound(Exception):
    desc: str = """Starting file not found"""


returncodes_map: dict = {
    1: GenricError,
    4: NoSuchService,
    5: NotInstalled,
    6: NotConfigured,
    7: NotRunningOrRefused,
    
    126: PermissionError,
    127: FileNotFound
}