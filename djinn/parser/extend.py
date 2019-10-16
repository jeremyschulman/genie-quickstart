from genie.libs.parser.utils.common import parser_data


def add_parser(mod, package, parser, os_name):
    output = dict()
    output['module_name'] = mod.__name__.rsplit('.', 1)[-1]
    output['package'] = package
    output['class'] = parser.__name__

    for cmd in parser.cli_command:
        if cmd not in parser_data:
            parser_data[cmd] = {}

        parser_data[cmd][os_name] = output

