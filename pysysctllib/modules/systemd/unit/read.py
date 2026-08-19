from pysysctllib.models import UnitPathType, ConfigModel
from configparser import ConfigParser
def read(unit_filename: str, unit_path_type: UnitPathType) -> ConfigModel:
    """Return ConfigParser object with unit file data"""
    import configparser
    from configparser import ParsingError
    from pysysctllib.exc import FileNotFound, PermissionError
    import os
    if not os.access(unit_path_type.value + unit_filename, os.F_OK):
        raise FileNotFound
    if not os.access(unit_path_type.value + unit_filename, os.R_OK | os.W_OK):
        raise PermissionError
    
    try:
        config = configparser.ConfigParser(strict=False)
        config.read(unit_path_type.value + unit_filename)
        config_model = ConfigModel()
        config_model.config = config
        config_model.path = unit_path_type.value + unit_filename
        config.optionxform = str
        return config_model
    except ParsingError as e:
        raise e