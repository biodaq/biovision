# matlab mex binary and examples

First compile biovision_multidaq.c to a mex file.

for matlab a mex compiler (gcc) must be installed. octave has preinstalled
compiler per default (OS dependend).
translate.m will do the job for you.

**Windows:**

to run the examples, you need to have also biovisionMultiDaq.dll in your path.

**Linux*

biovision driver must be installed.

## prerequisites

* Win10 64 bit
* Matlab Version >= R2018a
* compatible biovisionMultiDaq.dll

examples and binary were tested with R2021a only.

## example description

* info.m:  (low level)  
 check all devices on USB and print the *idn? string
* multidaq.m: (high level interface for one device)   
 convenience class for simple measurements
* demo1.m:  (high level)  
demo for the convenience class
* getTdfData.m:  
utily to read *.tdf files produced by multiDaq.exe.
* viewTdf.m  
example how to use getTdfData.m

The low level functions are more powerful and flexibel. You can manage multiple devices and triggers.

