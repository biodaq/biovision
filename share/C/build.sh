# do not change the install path
INSTALLPATH=/usr/local
# you may change the EXEPATH
EXEPATH=.
#mkdir -p ${INSTALLPATH}/bin
gcc -I${INSTALLPATH}/include -L${INSTALLPATH}/lib biovisionDevInfo.c -lbiovisionMultiDaq -o biovisionDevInfo
gcc -I${INSTALLPATH}/include -L${INSTALLPATH}/lib demo1.c -lbiovisionMultiDaq -o demo1
gcc -I${INSTALLPATH}/include -L${INSTALLPATH}/lib demoCallback.c -lbiovisionMultiDaq -o demoCallback
