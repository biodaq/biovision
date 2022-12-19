INSTALLPATH=/usr/local
sudo mkdir -p ${INSTALLPATH}/lib
sudo mkdir -p ${INSTALLPATH}/include

sudo cp ../../lib/biovisionMultiDaq.so ${INSTALLPATH}/lib/biovisionMultiDaq.so
sudo cp ../../include/biovisionMultiDaq.h ${INSTALLPATH}/include/biovisionMultiDaq.h

