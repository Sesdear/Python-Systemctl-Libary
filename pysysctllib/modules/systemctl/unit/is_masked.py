def is_masked(name) -> bool:
    import subprocess
    
    try:
        result = subprocess.run(['systemctl', 'is-masked', name, '-p', ''], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout.strip() == 'masked'
    except subprocess.CalledProcessError as e:
        from pysysctllib.exc import Exceptions
        if e.returncode in Exceptions:
            raise Exceptions[e.returncode]() from e
        raise