from pysysctllib.models import UnitPathType
def delete(unit_filename: str, unit_path_type: UnitPathType) -> (bool | None):
    import os
    from pysysctllib.exc import FileNotFound, PermissionError

    if not os.access(unit_path_type.value + unit_filename, os.F_OK):
        raise FileNotFound
    if not os.access(unit_path_type.value + unit_filename, os.W_OK | os.R_OK):
        raise PermissionError
    
    try:
        os.remove(unit_path_type.value + unit_filename)
        return True
    except FileNotFoundError:
        raise FileNotFound
    except PermissionError:
        raise PermissionError