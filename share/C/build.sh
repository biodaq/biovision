# do not change the install path
INSTALLPATH=/usr/local
# you may change the EXEPATH
EXEPATH=.
#mkdir -p ${INSTALLPATH}/bin
gcc -I${INSTALLPATH}/include -L${INSTALLPATH}/lib info.c -lbiovisionMultiDaq -o info
gcc -I${INSTALLPATH}/include -L${INSTALLPATH}/lib demo1.c -lbiovisionMultiDaq -o demo1
