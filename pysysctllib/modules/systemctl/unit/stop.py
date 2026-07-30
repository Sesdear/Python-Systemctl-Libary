def stop(name) -> bool:
    import subprocess
    import os
    
    if os.geteuid() != 0:
        raise PermissionError("Root privileges are required to stop a service.")
    
    try:
        subprocess.run(['systemctl', 'stop', name], check=True)
        return True
    except subprocess.CalledProcessError as e:
        from pysysctllib.modules.systemctl.exc import returncodes_map
        if e.returncode in returncodes_map:
            raise returncodes_map[e.returncode]() from e
        raise
        