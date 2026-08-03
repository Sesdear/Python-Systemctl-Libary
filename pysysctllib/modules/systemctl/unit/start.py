def start(name):
    import subprocess
    import os
    from pysysctllib.exc import Exceptions
    
    try:
        subprocess.run(['systemctl', 'start', name], check=True)
        return True
    except subprocess.CalledProcessError as e:
        from pysysctllib.exc import Exceptions
        if e.returncode in Exceptions:
            raise Exceptions[e.returncode]() from e
        raise