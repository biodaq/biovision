/* add.h

   Declares a function and variables to be imported by our application, and
   exported by our DLL.
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

// TODO #define MAX_NUM_DEVICES 4
#define MAX_NUM_CHANNELS 128 // that are channels per device

    int DLLCALL multiDaqInit(int debugLevel);
    // TODO implement
    // int DLLCALL   multiDaqRegisterCallback(int dev,funcptr *func,int nBytes);
    // int DLLCALL   multiDaqUnRegisterCallback(int dev);

    int DLLCALL multiDaqDeInit();
    int DLLCALL multiDaqOpen(int dev, char *systemLocation);
    int DLLCALL multiDaqClose(int dev);

    char *DLLCALL multiDaqSendCmd(int dev, char *cmd, int *bytesReceived, int *isBinaryAnswer);
    char *DLLCALL multiDaqSendCmdWhileStreaming(int dev, char *cmd); // fire and forget

    // convenience function to get the oversampling factor od ADC (only multidaq can deal with n!=1)
    int DLLCALL multiDaqGetAdcOversampling(int dev);

    // returns number of bytes, they will be a multiple of minaligned
    // minaligned should be the calculated samplesize
    // user has to provide the buffer *data
    int DLLCALL   multiDaqGetStreamingData(int dev, char *data, int minaligned, int maxSize);
    char *DLLCALL multiDaqGetLastError(int dev); // call will clear the errormessage

    // handle with care, they are for synchronisation purposes
    int DLLCALL multiDaqDisableTx(void); // disable all transmissions for all devices
    int DLLCALL multiDaqEnableTx(void);  // enables again, commands bettween will fire in a high priority thread

    // litte helper for Timing, runs at 10 MHz on windows and 1 GHz on linux
    int64_t DLLCALL multiDaqGetTicks(void);

    // little helper to measure response times for the synchronized groups
    // Timestamps are based on 10 MHz clock on windows
    // after multiDaqEnableTx(), the timestamps will be measured after the call
    // so you have to wait a couple of ms to get the right values
    // *data will be filled with the timestamps (4 x int64_t =32 bytes)
    // and must be provided by the user
    void DLLCALL multiDaqGetTimeStampsFromSynchronizedGroup(int dev, int64_t *data);

    // little helpers to get information from biovision devices
    char *DLLCALL multiDaqListDevices();
    char *DLLCALL multiDaqGetVersion(void);

    /* Exported variables. */
    // extern DLLAPI int foo;
    // extern DLLAPI int bar;

#ifdef __cplusplus
} // __cplusplus defined.
#endif
