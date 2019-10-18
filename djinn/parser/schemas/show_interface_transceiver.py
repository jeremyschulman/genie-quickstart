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
            Optional('vendor'): str,
            Optional('type'): str,
            Optional('part_number'): str,
            Optional('serial_number'): str,
        }
    }

    find_interface_blocks = re.compile(r"^(\S+)[\r]?$", re.M).finditer
