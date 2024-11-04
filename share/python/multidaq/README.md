# Python Package for biovision digitzer

## testet OS

The binaries are tested on following OS, but should work with others, too.

* Windows 10
* Windows 11
* Ubuntu 22.04
* Ubuntu 24.04 (graphic functions restricted)



## prerequisites

multidaq **depends only on numpy**.  
Needed binaries to access the hardware are included (DLL)



> **linux:** Two important points:
> you need **rights** to access the devices and a installed **SDL2** lib.  
>  There are at least 3 ways to get the rights. Method 3 is the safest. 
> 1. Be administrator or open python with sudo, you have all rights.
> 2. Add yoursel to dialout group: Open a terminal and enter following command with your username.  
> ```bash
> sudo usermod -a -G dialout <your_username>
> ```
> 3. Use udev: First download the file from [github](https://github.com/biodaq/biovision/blob/main/share/50-biovision-devices.rules)
> and copy to a system location:  
> ```bash
> sudo cp 50-biovision-devices.rules /etc/udev/rules.d/50-biovision-devices.rules
> ```
>
> 
> **SDL2** is widely used and probaly installed on your PC. If not, install at least:
> ```
> sudo apt-get install libsdl2-2.0-0 libsdl2-ttf-2.0-0 libsdl2-image-2.0-0
> ```
> .


## getting started

open a command terminal:

```bash
pip install multidaq
```

in python console or script you may test the installation with:

```python
import multidaq
dev = multidaq.multiDaq()
print(dev.listDevices())
```
output will be a list of strings with informations of devices on the bus. If no device is present you will get an empty list.  
An exception should not occur and would be an error.

## help

### examples

On [github examples](https://github.com/biodaq/biovision/tree/main/share/python) there are numerous example files. They show, how to handle the module.

### Version information

This PyPI package is a part of our [software](https://github.com/biodaq/biovision). The version number of this package is the version number of the DLL.  
A wiki to that project is [here](https://github.com/biodaq/biovision/wiki/).  

There is a version information string in the package. To get it open a python console:

```python
import multidaq
print(multidaq.__version__)
```

### builtin help

in python console you can get help to the modules included:

```python
import multidaq
help(multidaq)
```
and for the submodules with:

```python
help(multidaq.multiDaq())
help(multidaq.multiDaqLowLevel())
```









