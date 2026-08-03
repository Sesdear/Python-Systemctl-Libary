def is_active(name) -> bool:
    import subprocess

    try:
        result = subprocess.run(['systemctl', 'show', name, '-p', 'ActiveState', '--value'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout.strip() == 'active'
    except subprocess.CalledProcessError as e:
        from pysysctllib.exc import Exceptions
        if e.returncode in Exceptions:
            raise Exceptions[e.returncode]() from e
        raise