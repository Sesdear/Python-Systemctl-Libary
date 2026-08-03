class GenricError(Exception):
    """Genric error. More often means, what serice down in start."""
    code: int = 1
class NoSuchService(Exception):
    """Serice with follow name doesn't exist in system (Does not exist `.service` file)"""
    code: int = 4
class NotInstalled(Exception):
    """Program or configuration of service ot installed"""
    code: int = 5
class NotConfigured(Exception):
    """Service not configured"""
    code: int = 6
class NotRunningOrRefused(Exception):
    """Link to program not work or request to start rejected by manager"""
    code: int = 7
# PolicyKit Exceptions
class PermissionError(Exception):
    """Dont have permissons"""
    code: int = 126
class FileNotFound(Exception):
    """Starting file not found"""
    code: int = 127

Exceptions: dict = {
    1: GenricError,
    4: NoSuchService,
    5: NotInstalled,
    6: NotConfigured,
    7: NotRunningOrRefused,
    
    126: PermissionError,
    127: FileNotFound
}
