import os
import json
import configparser
import optimus_manager.envs as envs


class ConfigError(Exception):
    pass


def load_config():

    if os.path.isfile(envs.USER_CONFIG_PATH):
        user_config_path = envs.USER_CONFIG_PATH
    elif os.path.isfile(envs.DEPRECATED_USER_CONFIG_PATH):
        print("Warning : Your configuration file is at the deprecated location %s.\n"
              "Please move it to %s" % (envs.DEPRECATED_USER_CONFIG_PATH, envs.USER_CONFIG_PATH))
        user_config_path = envs.DEPRECATED_USER_CONFIG_PATH
    else:
        user_config_path = None

    config = configparser.ConfigParser()

    try:
        if user_config_path is not None:
            config.read([envs.DEFAULT_CONFIG_PATH, user_config_path])
        else:
            config.read(envs.DEFAULT_CONFIG_PATH)

    except configparser.ParsingError as e:
        raise ConfigError("Parsing error : %s" % str(e))

    validate_config(config)

    return config


def validate_config(config):

    folder_path = os.path.dirname(os.path.abspath(__file__))
    schema_path = os.path.join(folder_path, "config_schema.json")

    with open(schema_path, "r") as f:
        schema = json.load(f)

    # Checking if the config file has the required sections and options
    for section in schema.keys():

        if section not in config.keys():
            raise ConfigError("Cannot find header for section [%s]" % section)

        for option in schema[section].keys():

            if option not in config[section].keys():
                raise ConfigError("Cannot find option \"%s\" in section [%s]" % (option, section))

            multi_values, possible_values = schema[section][option]

            if multi_values:
                values = config[section][option].replace(" ", "").split(",")
                for val in values:
                    if val not in possible_values:
                        raise ConfigError("Invalid value \"%s\" for option \"%s\" in section [%s]" % (val, option, section))

            else:
                val = config[section][option]
                if val not in possible_values:
                    raise ConfigError("Invalid value \"%s\" for option \"%s\" in section [%s]" % (val, option, section))

    # Checking if the config file has no unknown section or option
    for section in config.keys():

        if section == "DEFAULT":
            continue

        if section not in schema.keys():
            raise ConfigError("Unknown section %s" % section)

        for option in config[section].keys():

            if option not in schema[section].keys():
                raise ConfigError("Unknown option %s in section %s" % (option, section))


def load_extra_xorg_options():

    xorg_extra = {}

    try:
        config_lines = _load_extra_xorg_file(envs.EXTRA_XORG_OPTIONS_INTEL_PATH)
        print("Loaded extra Intel Xorg options (%d lines)" % len(config_lines))
        xorg_extra["intel"] = config_lines
    except FileNotFoundError:
        pass

    try:
        config_lines = _load_extra_xorg_file(envs.EXTRA_XORG_OPTIONS_NVIDIA_PATH)
        print("Loaded extra Nvidia Xorg options (%d lines)" % len(config_lines))
        xorg_extra["nvidia"] = config_lines
    except FileNotFoundError:
        pass

    return xorg_extra


def _load_extra_xorg_file(path):

    with open(path, 'r') as f:

        config_lines = []

        for line in f:

            line = line.strip()
            line_nospaces = line.replace(" ", "")

            if len(line_nospaces) == 0 or line_nospaces[0] == "#":
                continue

            else:
                config_lines.append(line)

        return config_lines
