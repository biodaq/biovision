# installation of the linux drivers
# the installation path must be not changed
# we hardcoded the path to mitigate problems with LD_LIBRARY_PATH 
INSTALLPATH=/usr/local
sudo mkdir -p $INSTALLPATH/bin
sudo mkdir -p $INSTALLPATH/lib
sudo mkdir -p $INSTALLPATH/include
sudo cp lib/biovisionMultiDaq.so $INSTALLPATH/lib/libbiovisionMultiDaq.so
if [ $? -ne 0 ]; then
   echo "Error occurred!"
   exit 1
fi
sudo cp include/biovisionMultiDaq.h $INSTALLPATH/include/biovisionMultiDaq.h
if [ $? -ne 0 ]; then
   echo "Error occurred!"
   exit 1
fi
sudo cp bin/biovisionMultiDaq.h $INSTALLPATH/bin/biovisionMultiDaq.h
if [ $? -ne 0 ]; then
   echo "Error occurred!"
   exit 1
fi
exit 0

