def is_masked(name) -> bool:
    import subprocess
    
    try:
        result = subprocess.run(['systemctl', 'is-masked', name, '-p', ''], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout.strip() == 'masked'
    except subprocess.CalledProcessError as e:
        from pysysctllib.modules.systemctl.exc import returncodes_map
        if e.returncode in returncodes_map:
            raise returncodes_map[e.returncode]() from e
        raise