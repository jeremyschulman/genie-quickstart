"""
This file is a Work in Progress.  Attempting to create a Genie parser that will extract the interface
transciever information.

References
-----
https://developer.cisco.com/docs/genie-parsergen/

"""
from genie import parsergen as pg


MARKUP_show_interface_transceiver = """

OS: NXOS
CMD: SHOW_INTF_<NAME>_XCVRS
SHOWCMD: show interface {ifname} transceiver
PREFIX: if-xcvr

ACTUAL:
Ethernet2/2
    transceiver is present
    type is QSFP-H40G-AOC1M
    name is CISCO
    part number is FCBN410QE2C01-C1
    revision is D
    serial number is ABC1950011G-B
    nominal bitrate is 10300 MBit/sec
    Link length supported for AOC is 1 m
    cisco id is --
    cisco extended id number is 16

MARKUP:
XI<ifname>XEthernet2/2
    transceiver is XR<present>Xpresent
    type is XR<type>XQSFP-H40G-AOC1M
    name is XR<vendor>XCISCO
    part number is XR<part_number>XFCBN410QE2C01-C1
    revision is D
    serial number is XR<serial_number>ABCW1950011G-B
    nominal bitrate is 10300 MBit/sec
    Link length supported for AOC is 1 m
    cisco id is --
    cisco extended id number is 16    
"""

pg.extend_markup(MARKUP_show_interface_transceiver)


def get_if_xcvr(dev, if_name):

    attrValPairsToCheck = [
        ('if-xcvr.ifname', if_name),
        ('if-xcvr.present', None),
        ('if-xcvr.type', None),
        ('if-xcvr.vendor', None),
        ('if-xcvr.part_number', None),
        ('if-xcvr.serial_number', None),
    ]

    # the following call will create a parser that we can then invoke

    parser = pg.oper_fill(device=dev,
                          show_command=('SHOW_INTF_<NAME>_XCVRS', [], dict(ifname=if_name)),
                          attrvalpairs=attrValPairsToCheck,
                          refresh_cache=True)

    ok = parser.parse()
    if not ok:
        return False

    # If the command was executed and parsed OK, we need to extract it from the
    # parser core data holder.

    return pg.ext_dictio[dev.name]
