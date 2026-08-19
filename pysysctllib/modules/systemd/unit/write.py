from pysysctllib.models import ConfigModel
def write(config_model: ConfigModel) -> (bool | None):
    import os
    from pysysctllib.exc import FileNotFound, PermissionError
    if not os.access(config_model.path, os.F_OK):
        raise FileNotFound
    if not os.access(config_model.path, os.W_OK | os.R_OK):
        raise PermissionError
    
    try:
        with open(config_model.path, 'w', encoding='utf-8') as configfile:
            config_model.config.write(configfile)
        return True
    except Exception as e:
        return False