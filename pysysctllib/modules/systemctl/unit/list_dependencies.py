def list_dependencies(name) -> list:
    import subprocess
    from pysysctllib.modules.systemctl.exc import returncodes_map
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
        from pysysctllib.modules.systemctl.exc import returncodes_map
        if e.returncode in returncodes_map:
            raise returncodes_map[e.returncode]() from e
        raise