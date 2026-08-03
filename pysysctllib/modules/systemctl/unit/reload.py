def reload(name) -> bool:
    import subprocess
    import os
    
    try:
        subprocess.run(['systemctl', 'reload', name], check=True)
        return True
    except subprocess.CalledProcessError as e:
        from pysysctllib.exc import Exceptions
        if e.returncode in Exceptions:
            raise Exceptions[e.returncode]() from e
        raise