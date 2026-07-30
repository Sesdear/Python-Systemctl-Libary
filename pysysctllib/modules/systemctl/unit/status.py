from pysysctllib.models import StatusModel


def status(service_name):
    import subprocess
    
    try:
        result = subprocess.run([
            'systemctl', 'show', service_name,
            '-p', 'ActiveState', 
            '-p', 'SubState', 
            '-p', 'MainPID', 
            '-p', 'UnitFileState'
            '-p', 'FragmentPath'
            ], check=True, capture_output=True, text=True)
        data = {}
        
        for line in result.stdout.splitlines():
            key, value = line.split("=", 1)
            data[key] = value
        
        status_model = StatusModel()
        
        status_model.active_state = data["ActiveState"]
        status_model.sub_state = data["SubState"]
        status_model.unit_file_state = data["UnitFileState"]
        status_model.pid = int(data["MainPID"])
        status_model.service_path = data["FragmentPath"]
        
        
        return status_model
    except subprocess.CalledProcessError as e:
        from pysysctllib.modules.systemctl.exc import returncodes_map
        if e.returncode in returncodes_map:
            raise returncodes_map[e.returncode]() from e
        raise