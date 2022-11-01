/* biovisionMultiDaq.h
   h file for the biovisionMultiDaq.dll
   You will need a 64 bit compiler
   We recommend to use the mingw64 compiler suite
   but nevertheless it should work with other C or C++ compilers
   the interface is pure C, no name mangling is used
*/

/* You should define ADD_EXPORTS *only* when building the DLL. */
#ifdef ADD_EXPORTS
#define DLLAPI __declspec(dllexport)
#else
#define DLLAPI __declspec(dllimport)
#endif

/* Define calling convention in one place, for convenience. */
#define DLLCALL __cdecl

/* Make sure functions are exported with C linkage under C++ compilers. */
#ifdef __cplusplus
extern "C"
{
#endif
#include <stdint.h>

// DO not change the following two defines!!
#define MAX_NUM_DEVICES  4
#define MAX_NUM_CHANNELS 128 // that are channels per device

    // init the driver, a high priority task will be started
    int DLLCALL multiDaqInit(int debugLevel);
    // TODO implement
    // int DLLCALL   multiDaqRegisterCallback(int dev,funcptr *func,int nBytes);
    // int DLLCALL   multiDaqUnRegisterCallback(int dev);

    // deinit the driver, the high priority task will be stopped
    int DLLCALL multiDaqDeInit();

    // opens a channel (dev = 0..3 is allowed)
    // you need a id String, which you can extract from the answer of multiDaqListDevices()
    // idString: "id\tsystemlocation\tserialnumber"
    // where id is the devicename ("multi" or "bio"),systemlocation the COMPORT i.e "COMx"
    // and serialnumber is the serialnumber of the device
    int DLLCALL multiDaqOpen(int dev, char *idString);
    int DLLCALL multiDaqClose(int dev);

    // send a SCPI command, response is a string or a binary block, indicated by the value of isBinaryAnswer
    // in case binaryblock *bytesReceived hold the block size
    // otherwise you get a pointer to a null terminated string
    // user has to provide memory for *bytesReceived and *isBinaryAnswer
    char *DLLCALL multiDaqSendCmd(int dev, char *cmd, int *bytesReceived, int *isBinaryAnswer);
    char *DLLCALL multiDaqSendCmdWhileStreaming(int dev, char *cmd); // fire and forget
    int *DLLCALL  multiDaqSendSCPIbinBlock(int dev, char *data, int len);

    // convenience function to get the oversampling factor od ADC (only multidaq can deal with n!=1)
    int DLLCALL multiDaqGetAdcOversampling(int dev);

    // returns number of bytes, they will be a multiple of minaligned
    // minaligned should be the calculated samplesize
    // user has to provide the buffer *data
    int DLLCALL multiDaqGetStreamingData(int dev, char *data, int minaligned, int maxSize);

    // gets the last errormessage, if no error occurred this is an empty string
    char *DLLCALL multiDaqGetLastError(int dev); // call will clear the errormessage

    // handle with care, they are for synchronisation purposes of multiple devices
    int DLLCALL multiDaqDisableTx(void); // disable all transmissions for all devices
    int DLLCALL multiDaqEnableTx(void);  // enables again, commands bettween will fire in the high priority thread

    // litte helper for Timing, runs at 10 MHz on windows and 1 GHz on linux
    int64_t DLLCALL multiDaqGetTicks(void);

    // little helper to measure response times for the synchronized groups
    // Timestamps are based on 10 MHz clock on windows
    // after multiDaqEnableTx(), the timestamps will be measured after the call
    // so you have to wait a couple of ms to get the right values
    // *data will be filled with the timestamps (4 x int64_t =32 bytes)
    // and memory must be provided by the user
    void DLLCALL multiDaqGetTimeStampsFromSynchronizedGroup(int dev, int64_t *data);

    // little helpers to get information from biovision devices
    //
    const char *DLLCALL multiDaqListDevices();

    // little helper to get the version string of the dll
    const char *DLLCALL multiDaqGetVersion(void);

    /* Exported variables. */
    // extern DLLAPI int foo;
    // extern DLLAPI int bar;

#ifdef __cplusplus
} // __cplusplus defined.
#endif
