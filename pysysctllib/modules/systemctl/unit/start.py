def start(name):
    import subprocess
    import os
    from pysysctllib.modules.systemctl.exc import returncodes_map
    
    try:
        subprocess.run(['systemctl', 'start', name], check=True)
        return True
    except subprocess.CalledProcessError as e:
        from pysysctllib.modules.systemctl.exc import returncodes_map
        if e.returncode in returncodes_map:
            raise returncodes_map[e.returncode]() from e
        raise