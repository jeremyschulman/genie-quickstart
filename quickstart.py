"""

See Also
--------
    Controlling logging:
    https://pubhub.devnetcloud.com/media/pyats/docs/log/implementation.html

"""
from genie.testbed import load
from genie.conf.base.device import Device

# load the testbed YAML file so that the tesetbed credential information is loaded
# properly and can be used when creating the Device instances

testbed = load("empty-testbed.yaml").testbed


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
    return {'cli': dict(host=hostname,
                        init_config_commands=[],
                        init_exec_commands=[],
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

    testbed : genie.libs.conf.testbed.Testbed
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
    return Device(hostname,
                  os=os_type, type=device_type,
                  custom={'abstraction': {'order': ['os']}},
                  tacacs=testbed.tacacs,
                  passwords=testbed.passwords,
                  connections=make_ssh_conn(ip_addr or hostname))
