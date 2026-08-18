from pysysctllib.models import UnitModel
def create(unit_model: UnitModel) -> bool:
    import logging
    import os
    template = """[Unit]
Description={desc}
After={after}

[Service]
Type={type}
User={user}
WorkingDirectory={work_dir}
ExecStart={exec_start}
Restart={restart}
RestartSec={restart_sec}

[Install]
WantedBy={wantedby}
"""
    if unit_model.filename is None:
        logging.error("Filename required")
    try:
        if not os.path.exists(unit_model.path_type.value):
            logging.error(f"Directory not exist, try another UnitPathType's (Current: {unit_model.path_type.name}: {unit_model.path_type.value})")
            return False
        with open(unit_model.path_type.value + unit_model.filename, 'w') as f:
            f.write(template.format(
                desc=unit_model.Unit.Description, 
                after=unit_model.Unit.After, 
                type=unit_model.Service.Type,
                user=unit_model.Service.User,
                work_dir=unit_model.Service.WorkingDirectory,
                exec_start=unit_model.Service.ExecStart,
                restart=unit_model.Service.Restart,
                restart_sec=unit_model.Service.RestartSec,
                wantedby=unit_model.Install.WantedBy))
            
            return True
    except FileExistsError:
        logging.error("File exist")
        return False
    except Exception as e:
        logging.error(e)
        return False
    
    