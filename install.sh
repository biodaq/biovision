# installation of the linux drivers
# the installation path must be not changed
# we hardcoded the path to mitigate problems with LD_LIBRARY_PATH 
INSTALLPATH=/usr/local
sudo mkdir -p $INSTALLPATH/bin
sudo mkdir -p $INSTALLPATH/lib
sudo mkdir -p $INSTALLPATH/include

echo install SDL2
sudo apt-get install libsdl2-2.0-0 libsdl2-ttf-2.0-0 libsdl2-image-2.0-0
if [ $? -ne 0 ]; then
   echo "Error occurred!"
   exit 1
fi

echo install library
sudo cp lib/libbiovisionMultiDaq.so $INSTALLPATH/lib/libbiovisionMultiDaq.so
if [ $? -ne 0 ]; then
   echo "Error occurred!"
   exit 1
fi
echo install headerfiles
sudo cp include/biovisionMultiDaq.h $INSTALLPATH/include/biovisionMultiDaq.h
if [ $? -ne 0 ]; then
   echo "Error occurred!"
   exit 1
fi
sudo killall biovisionSharedMemDriver
echo install sharedMemdriver
sudo cp bin/biovisionSharedMemDriver $INSTALLPATH/bin/biovisionSharedMemDriver
if [ $? -ne 0 ]; then
   echo "Error occurred!"
   exit 1
fi
echo install rules for udev
sudo cp share/50-biovision-devices.rules /etc/udev/rules.d/50-biovision-devices.rules
if [ $? -ne 0 ]; then
   echo "Error occurred!"
   exit 1
fi
echo installation was successful
exit 0

