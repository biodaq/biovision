# matlab mex binary and examples

we put matlab binary and example scripts into the same directory.
to run the examples, you need to have biovisionMultiDaq.dll in your path.

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
utility to read *.tdf files produced by multiDaq.exe.
* viewTdf.m  
example how to use getTdfData.m

The low level functions are more powerful and flexible. You can manage multiple devices and triggers.

