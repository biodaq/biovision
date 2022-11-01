rem edit and uncomment the forth line to set your environment properly
rem you need the 64 bit Version
rem example from my PC:
rem call "C:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Auxiliary\Build\vcvars64.bat"

echo ---------------------- build
cl info.c -I../../include /link ../../lib/libbiovisionmultidaq.a
cl demo1.c -I../../include /link ../../lib/libbiovisionmultidaq.a