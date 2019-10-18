"""
This file contains a "Quick Start" example using pyATS / Genie.  User Story:

    As a network engineer I want to quickly use genie to connect to a device
    and execute arbitrary commands either using the `execute()` method or the
    `parse()` method. I do not want to create any testbed file, rather
    programmatically construct a testbed instance and use credentials from my
    environment:

        export PYATS_USERNAME=<your-login-username>
        export PYATS_PASSWORD=<your-login-password>

    You can then create specific instances of any device, connect, and return
    the Device instance:

        dev = connect_device("switch1", "nxos", testbed)
        text = dev.execute('show version')     # returns the string
        data = dev.parse('show version')       # returns dict of parsed string

References
----------
    To programmatically create a Testbed:
    https://pubhub.devnetcloud.com/media/pyats/docs/topology/creation.html#manual-creation

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

from pyats.topology import Testbed
from pyats.topology.credentials import Credentials
from genie.conf.base.device import Device


def ensure_environment():
    try:
        assert all(os.environ[env] for env in ['PYATS_USERNAME', 'PYATS_PASSWORD'])
    except KeyError as exc:
        sys.exit(f"ERROR: missing environment variable: {exc}")


def make_testbed(name):
    testbed = Testbed(name)

    testbed.credentials=Credentials(dict(default=dict(
                     username=os.environ['PYATS_USERNAME'],
                     password=os.environ['PYATS_PASSWORD'])))

    print(f"Created Genie testbed: {testbed.name}")
    return testbed


def disable_console_log(dev):
    dev.connectionmgr.log.setLevel(logging.ERROR)


def connect_device(hostname, os_type, testbed, device_type='switch', ip_addr=None, log_stdout=False):
    """
    This function will create a Device instance and initiate the connection
    with log_stdout disabled by default.  If the device already exists and is
    connected then this function will return what already exists.

    Examples
    --------
        dev = connect_device('switch1', 'nxos', testbed)
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
        Optional.  The IP address for the hostname.  If given, this value will
        be used to open the connection.  If not given, then the `hostname`
        parameter must be in DNS.

    log_stdout : bool
        Optional, default=False.  Controls the initial connection setting to
        disable/enable stdout logging.

    Returns
    -------
    Device
        Connected device instance
    """

    # see if the device already exists and is connected.  If it is, then return
    # what we have, otherwise proceed to create a new device and connect.

    has_device = testbed.devices.get(hostname)
    if has_device:
        if has_device.is_connected():
            return has_device
        else:
            del testbed.devices[hostname]

    dev = Device(hostname,
                 os=os_type,  # required
                 type=device_type,  # optional

                 # genie uses the 'custom' field to select parsers by os_type

                 custom={'abstraction': {'order': ['os']}},

                 # connect only using SSH, prevent genie from making config
                 # changes to the device during the login process.

                 connections={'default': dict(host=(ip_addr or hostname),
                                              arguments=dict(init_config_commands=[],
                                                             init_exec_commands=[]),
                                              protocol='ssh')})

    testbed.add_device(dev)
    dev.connect(log_stdout=log_stdout)

    return dev


if __name__ == "__main__":
    ensure_environment()
    testbed = make_testbed(name='quickstart-notestbedfile')
