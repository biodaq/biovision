# biovision

Here are required binaries and Sources for biovision DAQ devices.

To keep the directory structure simple, there are files for different OS in the subfolders bin and lib.


Folders:
* bin: contain the fundamental binaries (dll for Win)
* include: contain the h files
* lib: contain the import lib (Win only) and the .so libs (linux)
* share: subfolders for Dokumentation and language specific binaries/examples
  * C: examples for the C low level interface
  * matlab: 64 bit mexfile and examples (Windows only)
  * octave: 64 bit mexfile and examples (Win / Linux)
  * python: python low level interface and examples (OS independent)

## Runtime

Running an example is OS dependent.

**Windows**

The generated binaries or scripts needs our DLL. You have to copy it in the folder of of Your binary or copy it to a position in PATH of Your choice.

If You want to use our tMsg system to communicate between applications, you must load the same dll in the same directory for all interacting applications.

simple approach for that:

copy all scripts, applications and the biovision dll to a folder of your choice and start the applications from that folder. Windows will search for the dlls first in that folder and the prerequisites are satisfied.

**Linux:**

We assume the \*.so dynamic libraries to be located in /usr/local/lib.
to ensure that, simply copy the needed files to that location.

The script install.sh in the root folder will do the job for you. Run simply 'sudo ./install.sh'. You will be asked for the administrator password.

If You want to use our tMsg system to communicate between applications the biovisionSharedMemDriver (in bin folder) must run. You may consider to start it in the autostart group. It enables communication between applications via linux shared Memory.

warning for terminal invocation of biovisionSharedMemDriver:

if You close the terminal via [x] button, biovisionSharedMemDriver is not notified to clean up the resources (tested on ubuntu 22.04). You have to reboot to get it working again. If you stop the driver via [CTRL C], you should have no problems.
