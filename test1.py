from djinn.parser.nxos import show_interface_transceiver

dev = add_device('atlrs21', 'nxos', testbed)
dev.connect(log_stdout=False)
