gcc info.c -o info.exe -O2 -std=c99 -Wall -I../../include -L../../lib -lbiovisionmultidaq -s -Wl,--subsystem,console
gcc demo1.c -o demo1.exe -O2 -std=c99 -Wall -I../../include -L../../lib -lbiovisionmultidaq -s -Wl,--subsystem,console
