gcc biovisionDevInfo.c -o biovisionDevInfo.exe -O2 -std=c99 -Wall -I../../include -L../../lib -lbiovisionmultidaq -s -Wl,--subsystem,console
gcc demo1.c -o demo1.exe -O2 -std=c99 -Wall -I../../include -L../../lib -lbiovisionmultidaq -s -Wl,--subsystem,console
gcc demoMsg.c ../../src/serial.c -o demoMsg.exe -O2 -std=c99 -Wall -I../../include -L../../lib -lbiovisionmultidaq -s -Wl,--subsystem,console
gcc demoCallback.c -o demoCallback.exe -O2 -std=c99 -Wall -I../../include -L../../lib -lbiovisionmultidaq -s -Wl,--subsystem,console
