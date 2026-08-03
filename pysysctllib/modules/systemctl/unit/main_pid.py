def main_pid(service_name: str) -> int:
    import subprocess
    
    try:
        result = subprocess.run([
            'systemctl', 'show', service_name,
            '-p', 'MainPID'
            ], check=True, capture_output=True, text=True)
        data = {}
        
        for line in result.stdout.splitlines():
            key, value = line.split("=", 1)
            data[key] = value
        
        
        return int(data["MainPID"])
    except subprocess.CalledProcessError as e:
        from pysysctllib.exc import Exceptions
        if e.returncode in Exceptions:
            raise Exceptions[e.returncode]() from e
        raise