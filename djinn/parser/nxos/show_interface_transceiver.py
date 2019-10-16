"""
This file demonstrates how to create a new genie parser and dynamically bind it
into the framework so that a caller can invoke using the device.parse() method,
similar to any other parser that is packaged with the genie framework.

The specific parser is to support the calls:
    "show interface transceiver"
    'show interface {interface} transceiver'

The {interface} parameter can be any form that is accepted by the NXOS cli.  This includes
ranges, for example:

    In [3]: dev.parse('show interface Ethernet1/1 - 2 transceiver')
    Out[3]:
    {'Ethernet1/1': {'exists': True,
      'vendor': 'CISCO-FINISAR',
      'type': 'Fabric',
      'part_number': 'FTLX8570D3BCL-C2',
      'serial_number': 'FNS1947100T'},
     'Ethernet1/2': {'exists': True,
      'vendor': 'CISCO-FINISAR',
      'type': 'Fabric',
      'part_number': 'FTLX8570D3BCL-C2',
      'serial_number': 'FNS1947101K'}}

This parser was developed using the genie parsergen "markup" capabilities.  Very nice!

References
-----
https://developer.cisco.com/docs/genie-parsergen/
"""

import sys

from genie import parsergen as pg
from djinn.parser.extend import add_parser
from djinn.parser.schemas.show_interface_transceiver import ShowInterfaceTransceiverSchema


__all__ = ['ShowInterfaceTransceiver']


class ShowInterfaceTransceiver(ShowInterfaceTransceiverSchema):
    """
    Genie parser for NXOS that collects the interface transceiver inventory
    information.

    The specific parser is to support the calls:
        "show interface transceiver"
        'show interface {interface} transceiver'

    The {interface} parameter can be any form that is accepted by the NXOS cli.  This includes
    ranges, for example:

        In [3]: dev.parse('show interface Ethernet1/1 - 2 transceiver')
        Out[3]:
        {'Ethernet1/1': {'exists': True,
          'vendor': 'CISCO-FINISAR',
          'type': 'Fabric',
          'part_number': 'FTLX8570D3BCL-C2',
          'serial_number': 'FNS1947100T'},
         'Ethernet1/2': {'exists': True,
          'vendor': 'CISCO-FINISAR',
          'type': 'Fabric',
          'part_number': 'FTLX8570D3BCL-C2',
          'serial_number': 'FNS1947101K'}}

    """
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
    MARKUP_ATTRS = ['ifname', 'present', 'type',
                    'vendor', 'part_number', 'serial_number']

    pg.extend_markup(MARKUP_CONTENT)

    cli_command = [
        'show interface transceiver',
        'show interface {interface} transceiver'
    ]

    def cli(self, interface=None, output=None, **kwargs):

        cli_cmd = (self.cli_command[0] if not interface
                   else self.cli_command[1].format(interface=interface))

        # run the command to obtain the TEXT output so that we can then run it
        # through the parsergen.  We do this because if the caller does not
        # provide an interface, or the provided interface is a range, we will
        # need to parse the same output multiple times; once for each interface
        # found in the output.

        cli_output = self.device.execute(cli_cmd)

        # extract the interface names from the TEXT output so we know which
        # specific interface we will parse using the parsergen.

        if_name_list = self.find_interface_names(cli_output)
        if not if_name_list:
            # this results in: SchemaEmptyParserError: Parser Output is empty,
            # TODO: investigate the proper way to return empty data so
            #       an exception does not occur.
            return {}

        # the parsergen requires a list[tuple] to determine how to process the
        # text. in every case, we need to only provide the interface name; and
        # then have parsergen extract all other attributes.  The following code
        # sets up the dictionary that is then passed as a list of tuple items.

        find_attrs = {f'{self.MARKUP_PREFIX}.{attr}': None
                      for attr in self.MARKUP_ATTRS}

        # declare a dict variable that must returned from this method, and will
        # need to conform to the schema definition.

        schema_output = dict()

        # iterate through each interface found in the CLI TEXT output, running
        # for each through the parsergen system.

        for if_name in if_name_list:
            find_attrs['if-xcvr.ifname'] = if_name

            # the following call will create a parser that we can then invoke
            # notice that we use the device_os and device_output params here to
            # pass the original CLI text output multiple times through
            # parsergen.

            parser = pg.oper_fill(device_os=self.device.os,
                                  device_output=cli_output,
                                  show_command=('SHOW_INTF_<NAME>_XCVRS', [], {
                                      'ifname': interface
                                  }),
                                  attrvalpairs=find_attrs.items(),
                                  refresh_cache=False)

            ok = parser.parse()
            if not ok:
                # TODO: should probably log this error, need to investigate best practice
                #       with the Cisco team.
                continue

            # If the command was executed and parsed OK, we need to extract it
            # from the parser core data holder.  We use the key 'device_name'
            # include we are using the device_output call above.  Otherwise,
            # we would use the key=self.device.name

            parsed_attrs = pg.ext_dictio['device_name']

            # always create an entry for each interface, even if no transceiver
            # exists.  In that case the 'exists' key is set to False and we
            # continue to the next interface in the list to process.

            schema_output[if_name] = if_schema_data = {
                'exists':  parsed_attrs.get('if-xcvr.present', '') == 'present'
            }

            if not if_schema_data['exists']:
                continue

            # a transceiver exists, so copy the data out from parsergen into
            # the return dictionary variable.

            if_schema_data['vendor'] = parsed_attrs['if-xcvr.vendor']
            if_schema_data['type'] = parsed_attrs['if-xcvr.type']
            if_schema_data['part_number'] = parsed_attrs['if-xcvr.part_number']
            if_schema_data['serial_number'] = parsed_attrs['if-xcvr.serial_number']

        return schema_output


# This call dynamically add this parser to the parsegen framework; it must be
# after the the class definition.

add_parser(mod=sys.modules[__name__], package=__package__,
           os_name='nxos', parser=ShowInterfaceTransceiver)
