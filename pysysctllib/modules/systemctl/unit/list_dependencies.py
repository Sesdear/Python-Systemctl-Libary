def list_dependencies(name) -> list:
    import subprocess
    from pysysctllib.exc import Exceptions
    try:
        result = subprocess.run(['systemctl', 'list-dependencies', name, '--plain', '--no-pager', '--output', 'json'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout.strip()
        dependencies = []
        for line in output.splitlines():
            line = line.strip()
            if line and not line.startswith(name):
                dependencies.append(line)
        return dependencies
    except subprocess.CalledProcessError as e:
        from pysysctllib.exc import Exceptions
        if e.returncode in Exceptions:
            raise Exceptions[e.returncode]() from e
        raise