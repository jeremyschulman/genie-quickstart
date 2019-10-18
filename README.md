# Cisco pyATS Genie Quickstart

This file contains a "Quick Start" example using pyATS / Genie.  

## Using a Testbed file without Devices defined

User Story:

    As a network engineer I want to quickly use genie to connect to a device and execute
    arbitrary commands either using the `execute()` method or the `parse()` method.
    I do not want to create a complex "testbed" file that contains all of the devices;
    but I do want to use the testbed file so that I can pass my credentials via environment
    variables.  

```shell script
export PYATS_USERNAME=<your-login-username>
export PYATS_PASSWORD=<your-login-password>
```    

The [quickstart](quickstart.py) script will load the testbed file called *empty-testbed.yaml* for this purpose.    
You can then create specific instances of any device:

```python
dev = add_device("switch1", "nxos", testbed)
dev.connect()
text = dev.execute('show version')     # returns the string
data = dev.parse('show version')       # returns dict of parsed string
```    

## No Testbed File

User Story:

    As a network engineer I want to quickly use genie to connect to a device
    and execute arbitrary commands either using the `execute()` method or the
    `parse()` method. I do not want to create any testbed file, rather
    programmatically construct a testbed instance and use credentials from my
    environment
    
```shell script
export PYATS_USERNAME=<your-login-username>
export PYATS_PASSWORD=<your-login-password>
```    

The [quickstart-notestbedfile](quickstart-notestbedfile.py) does not require a testbed YAML file.  A `testbed`
variable will be programmatically created, and then you can:

```python
dev = connect_device("switch1", "nxos", testbed)
text = dev.execute('show version')     # returns the string
data = dev.parse('show version')       # returns dict of parsed string
```    

    
