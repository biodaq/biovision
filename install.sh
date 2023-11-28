#!/bin/bash
# installation of the linux drivers
# the installation path must not be changed
# we hardcoded the path to mitigate problems with LD_LIBRARY_PATH
if [[ $EUID -ne 0 ]]; then
   echo "Script must be run with root privileges (\"sudo\")" 2>&1
   exit 1
fi

INSTALL_PATH=/usr/local

mkdir -p $INSTALL_PATH/bin
mkdir -p $INSTALL_PATH/lib
mkdir -p $INSTALL_PATH/include

echo install library
cp lib/libbiovisionMultiDaq.so $INSTALL_PATH/lib/libbiovisionMultiDaq.so
if [ $? -ne 0 ]; then
   echo "Error installing library occurred!"
   exit 1
fi

echo install header files
cp include/biovisionMultiDaq.h $INSTALL_PATH/include/biovisionMultiDaq.h
if [ $? -ne 0 ]; then
   echo "Error installing header files occurred!"
   exit 1
fi

echo install sharedMemdriver
killall biovisionSharedMemDriver 1>&- 2>&-
cp bin/biovisionSharedMemDriver $INSTALL_PATH/bin/biovisionSharedMemDriver
if [ $? -ne 0 ]; then
   echo "Error installing sharedMemdriver occurred!"
   exit 1
fi

echo install rules for udev
cp share/50-biovision-devices.rules /etc/udev/rules.d/50-biovision-devices.rules
if [ $? -ne 0 ]; then
   echo "Error installing rules for udev occurred!"
   exit 1
fi

echo
echo ..installation was completed successfully!
exit 0
