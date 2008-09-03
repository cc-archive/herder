import os.path

import paste.deploy
import pylons
import herder.config.environment


def resolve_config(basename):
    """Resolve a configuration file name."""

    return os.path.abspath(basename)

def init_environment(config):
    """Load the application configuration from the specified config.ini 
    file to allow the Pylons models to be used outside of Pylons."""

    config = paste.deploy.appconfig('config:' + config)
    herder.config.environment.load_environment(
        config.global_conf, config.local_conf)
