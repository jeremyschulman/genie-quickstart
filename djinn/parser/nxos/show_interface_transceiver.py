"""
This file is a Work in Progress.  Attempting to create a Genie parser that will extract the interface
transciever information.

References
-----
https://developer.cisco.com/docs/genie-parsergen/

"""

import sys
import re
from copy import copy



from genie import parsergen as pg
from djinn.parser.extend import add_parser
from djinn.parser.schemas.show_interface_transceiver import ShowInterfaceTransceiverSchema


__all__ = ['ShowInterfaceTransceiver']


class ShowInterfaceTransceiver(ShowInterfaceTransceiverSchema):
    OS = 'nxos'
    MARKUP_PREFIX = 'if-xcvr'
    MARKUP_CONTENT = """
OS: """ + OS.upper() + """
CMD: SHOW_INTF_<NAME>_XCVRS
SHOWCMD: show interface {ifname} transceiver
PREFIX: """ + MARKUP_PREFIX + """

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
    type is XS<type>XQSFP-H40G-AOC1M
    name is XS<vendor>XCISCO
    part number is XS<part_number>XFCBN410QE2C01-C1
    revision is D
    serial number is XS<serial_number>XABCW1950011G-B
    nominal bitrate is 10300 MBit/sec
    Link length supported for AOC is 1 m
    cisco id is --
    cisco extended id number is 16    
    """
    MARKUP_ATTRS = ['ifname', 'type', 'vendor', 'part_number', 'serial_number']

    pg.extend_markup(MARKUP_CONTENT)

    cli_command = [
        'show interface transceiver',
        'show interface {interface} transceiver'
    ]

    def cli(self, interface=None, output=None):

        cli_cmd = (self.cli_command[0] if not interface
                   else self.cli_command[1].format(interface=interface))

        cli_output = self.device.execute(cli_cmd)

        import pdb
        pdb.set_trace()

        if_name_list = self.find_interface_names(cli_output)
        if not if_name_list:
            return False

        find_attrs = {f'{self.MARKUP_PREFIX}.{attr}': None
                      for attr in self.MARKUP_ATTRS}

        schema_output = dict()

        for if_name in if_name_list:
            find_attrs['if-xcvr.ifname'] = if_name

            # the following call will create a parser that we can then invoke

            parser = pg.oper_fill(device_os=self.device.os,
                                  device_output=cli_output,
                                  show_command=('SHOW_INTF_<NAME>_XCVRS', [], {
                                      'ifname': interface
                                  }),
                                  attrvalpairs=find_attrs,
                                  refresh_cache=True)

            ok = parser.parse()
            if not ok:
                continue

            # If the command was executed and parsed OK, we need to extract it from the
            # parser core data holder.

            parsed_attrs = pg.ext_dictio[self.device.name]
            schema_output[if_name] = if_schema_data = {
                'exists': 'present' in parsed_attrs['if-xcvr.present']
            }

            if not if_schema_data['exists']:
                continue

            if_schema_data['vendor'] = parsed_attrs['if-xcvr.vendor']
            if_schema_data['type'] = parsed_attrs['if-xcvr.type']
            if_schema_data['part_number'] = parsed_attrs['if-xcvr.part_number']
            if_schema_data['serial_number'] = parsed_attrs['if-xcvr.serial_number']

        return schema_output


add_parser(mod=sys.modules[__name__], package=__package__,
           os_name='nxos', parser=ShowInterfaceTransceiver)
