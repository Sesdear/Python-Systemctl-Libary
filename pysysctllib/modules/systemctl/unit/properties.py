def show(name: str):
    """Give dict with all parameters in output
    
    Args:
        service_name (str): Name of systemd Unit

    Returns:
        dict
    """
    import subprocess
    
    
    try:        
        result = subprocess.run(
            ['systemctl', 'show', name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        info = {
            key: value
            for key, value in (
                line.split("=", 1)
                for line in result.stdout.splitlines()
            )
        }
        
        return info
    except subprocess.CalledProcessError as e:
        from pysysctllib.modules.systemctl.exc import returncodes_map
        if e.returncode in returncodes_map:
            raise returncodes_map[e.returncode]() from e
        raise

