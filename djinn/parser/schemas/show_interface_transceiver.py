import re
from genie.metaparser import MetaParser

from genie.metaparser.util.schemaengine import (
    Any, Optional)

__all__ = ["ShowInterfaceTransceiverSchema"]


class ShowInterfaceTransceiverSchema(MetaParser):
    """
    Schema definition for parser: "show interface <interface> transceiver"
    """
    schema = {
        Any(): {
            'exists': bool,
            Optional('vendor'): str,
            Optional('type'): str,
            Optional('part_number'): str,
            Optional('serial_number'): str,
        }
    }

    find_interface_names = re.compile(r"^(\S+)[\r]?$", re.M).findall
