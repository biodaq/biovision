
# C examples


* info.c
           
      read out the identification strings of all connected.biovision devices.
* demo1.c
      
      sample 2 channels for 1 second on the first listed device.
* demoCallback.c
      
      demonstration how Callback function for data works.
      samples for 3 seconds and stop then.



---

## build
**Windows**

with Mingw64 Compiler Suite:

* run cmd.exe in the share\\C subfolder of your downloaded folder.
* set the environment of the compiler executables properly.
* run build.bat


with Microsoft Compiler:

* adjust Path to the Compiler executetables in msvcbuild.bat
* run msvcbuild.bat

**Linux**

* cd to share/C in the downloaded folder
* run install.sh, if you did not installed the driver
* run build.sh, it will produce the binaries in that directory


## run

**Windows**

You need biovisionMultiDaq.dll in your path. It is in the 'bin' path. You may consider to copy the dll in a system path or set the %PATH% variable to your preferred installation folder.

**Linux**

You can run the demos from every location.  
If you not installed to /usr/local, you have to play with LD_LIBRARY_PATH.  
Or if you do not want to play with the environment, add the rpath linker option in the call of gcc.  
i.e. '-Wl,-rpath=/path/where/you/installed' in that case.  
