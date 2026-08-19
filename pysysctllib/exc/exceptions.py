class GenricError(Exception):
    """Genric error. More often means, what serice down in start."""
    pass
class NoSuchService(Exception):
    """Serice with follow name doesn't exist in system (Does not exist `.service` file)"""
    pass
class NotInstalled(Exception):
    """Program or configuration of service ot installed"""
    pass
class NotConfigured(Exception):
    """Service not configured"""
    pass
class NotRunningOrRefused(Exception):
    """Link to program not work or request to start rejected by manager"""
    pass
# PolicyKit Exceptions
class PermissionError(Exception):
    """Dont have permissons"""
    pass
class FileNotFound(Exception):
    """File not found"""
    pass

Exceptions: dict = {
    1: GenricError,
    4: NoSuchService,
    5: NotInstalled,
    6: NotConfigured,
    7: NotRunningOrRefused,
    
    126: PermissionError,
    127: FileNotFound
}
