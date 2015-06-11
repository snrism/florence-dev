import logging

# Global config dictionary
config = {}

# @var DEBUG_LEVELS
# Map from strings to debugging levels
DEBUG_LEVELS = {
    'debug': logging.DEBUG,
    'verbose': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'warn': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}

# @var CONFIG_DEFAULT
# The default configuration dictionary for Florence
CONFIG_DEFAULT = {
    # Miscellaneous options
    "list": False,
    "list_test_names": False,

    # Test selection options
    "test_spec": "",
    "test_file": None,
    "test_dir": "test",

    # Switch connection options
    "controller_host": "0.0.0.0",  # For passive bind
    "controller_port": 6653,
    "switch_ip": None,  # If not none, actively connect to switch
    "platform": "eth",
    "platform_args": None,
    "platform_dir": "platforms",
    "interfaces": [],
    "openflow_version": "1.3",

    # Logging options
    "log_file": "florence.log",
    "log_dir": None,
    "debug": "verbose",
    "xunit": False,
    "xunit_dir": "xunit",

    # Test behavior options
    "relax": False,
    "test_params": "None",
    "fail_skipped": False,
    "default_timeout": 2.0,
    "default_negative_timeout": 0.01,
    "minsize": 0,
    "random_seed": None,
    "disable_ipv6": False,
    "random_order": False,

    # Other configuration
    "port_map": {},
}
