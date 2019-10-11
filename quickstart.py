"""
This file contains a "Quick Start" example using pyATS / Genie.  User Story:

    As a network engineer I want to quickly use genie to connect to a device and execute
    arbitrary commands either using the `execute()` method or the `parse()` method.
    I do not want to create a complex "testbed" file that contains all of the devices;
    but I do want to use the testbed file so that I can pass my credentials via environment
    variables.

        export PYATS_USERNAME=<your-login-username>
        export PYATS_PASSWORD=<your-login-password

    This script will load the testbed file called "empty-testbed.yaml" for this purpose.

    You can then create specific instances of any device:

        dev = add_device("switch1", "nxos", testbed)
        dev.connect()
        text = dev.execute('show version')     # returns the string
        data = dev.parse('show version')       # returns dict of parsed string


Notes
-----
    You can control the output logging:

    A) When you connect to the device:
        dev.connect(log_stdout=False)

    *after* you have connected to the device using one of two methods:

    B.1)
        import logging
        dev.connectionmgr.log.setLevel(logging.ERROR)

    B.2)
        dev.log_user(enable=False)  # disable a device logs on screen
        dev.log_user(enable=True)  # enable a device logs on screen

"""
import sys
import os

import logging
from genie.testbed import load
from genie.conf.base.device import Device

# load the testbed YAML file so that the tesetbed credential information is loaded
# properly and can be used when creating the Device instances

try:
    assert all(os.environ[env] for env in ['PYATS_USERNAME', 'PYATS_PASSWORD'])
except KeyError as exc:
    sys.exit(f"ERROR: missing ENVAR: {exc}")


testbed = load("empty-testbed.yaml")
print(f"Genie loaded testbed: {testbed.name}")


def disable_console_log(dev):
    dev.connectionmgr.log.setLevel(logging.ERROR)


def make_ssh_conn(hostname):
    """
    This function creates a connections dict used when creating a new Device
    instance.  The returned dict will only contain an SSH connection.  For more
    details on connection schema, see this doc:
    https://pubhub.devnetcloud.com/media/pyats/docs/topology/schema.html#production-yaml-schema

    Parameters
    ----------
    hostname : str
        The DNS hostname or IP address to connect to the device.

    Returns
    -------
    dict
    """
    return {'default': dict(host=hostname,
                            arguments=dict(init_config_commands=[],
                                           init_exec_commands=[]),
                            protocol='ssh')}


def add_device(hostname, os_type, testbed, device_type='switch', ip_addr=None):
    """
    This function will create a Device instance that can then be used to connect, execute,
    and parse commands.

    Examples
    --------
        dev = add_device('switch1', 'nxos', testbed)
        dev.connect()
        dev.parse('show version')

    Parameters
    ----------
    hostname : str
        The hostname of the device

    os_type : str
        The OS type of the device.  Must be one of the values listed on the docs website:
        https://pubhub.devnetcloud.com/media/pyats-getting-started/docs/quickstart/manageconnections.html#manage-connections

    testbed : Testbed
        The testbed attributed from the loaded testbed file

    device_type : str
        User device device-type string

    ip_addr : str
        Optional.  The IP address for the hostname.  If given, this value will be used
        to open the connection.  If not given, then the `hostname` parameter must be in DNS.

    Returns
    -------
    Device
        New device instance that you can then use to execute the `.connect()` method.
    """

    dev = Device(hostname,
                 os=os_type, type=device_type,
                 custom={'abstraction': {'order': ['os']}},     # genie uses this to select parsers by os_type
                 connections=make_ssh_conn(ip_addr or hostname))

    testbed.add_device(dev)
    return dev
