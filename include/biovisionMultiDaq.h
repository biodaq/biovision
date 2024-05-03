/* copyright: Tantor GmbH, 2022
   biovisionMultiDaq.h
   h file for the biovisionMultiDaq.dll
   You will need a 64 bit compiler
   We recommend to use the mingw64 compiler suite on Windows, and gcc 64 bit on Linux
   but nevertheless it works with other C or C++ compilers
   the interface is pure C, no name mangling is used
*/

/* You should define ADD_EXPORTS *only* when building the DLL. */
#ifdef ADD_EXPORTS
#ifdef _WIN32
#define DLLAPI  __declspec(dllimport)
#define DLLCALL __declspec(dllexport)
#else
#define DLLAPI
#define DLLCALL
#endif
#else
#ifdef _WIN32
#define DLLCALL __cdecl
#else
#define DLLCALL
#endif
#endif
/* Make sure functions are exported with C linkage under C++ compilers. */
#ifdef __cplusplus
extern "C"
{
#endif
#include <stdint.h>

// DO not change the following three defines!!
#define MAX_NUM_DEVICES  4
#define MAX_NUM_CHANNELS 128 // that are 16 bit channels per device
#define MAX_NUM_SLAVES   4

    // init the driver, a high priority task will be started
    int DLLCALL multiDaqInit(int debugLevel);

    // deinit the driver, the high priority task will be stopped
    int DLLCALL multiDaqDeInit();

    // opens a channel (dev = 0..3 is allowed)
    // you need either an id String, which you can extract from the answer of multiDaqListDevices()
    // idString: "id\tsystemlocation\tserialnumber"
    // where id is the devicename ("multi" or "bio"),systemlocation the COMPORT i.e "COMx"
    // and serialnumber is the serialnumber of the device
    // or simply the device port, which you can find out with the device manager
    int DLLCALL multiDaqOpen(int dev, char *idString);
    int DLLCALL multiDaqClose(int dev);

    // set the callbackfunction for data
    // internal queues are not used, if pfunc is != NULL
    // complete data exchange must be handled via callback function
    // user has to manage all
    int DLLCALL multiDaqSetCallbackData(int dev, void (*pfunc)(char *data, int len));

    // send a SCPI command, response is a string or a binary block, indicated by the value of isBinaryAnswer
    // in case binaryblock *bytesReceived hold the block size
    // otherwise you get a pointer to a null terminated string
    // user has to provide memory for *bytesReceived and *isBinaryAnswer
    // returns NULL pointer in case of an error
    char *DLLCALL multiDaqSendCmd(int dev, char *cmd, int *bytesReceived, int *isBinaryAnswer);

    int DLLCALL multiDaqSendCmdWhileStreaming(int dev, char *cmd); // fire and forget
    int DLLCALL multiDaqSendSCPIbinBlock(int dev, char *data, int len);

    // convenience function to get the oversampling factor of the ADC (only multidaq can deal with n!=1)
    int DLLCALL multiDaqGetAdcOversampling(int dev); // 1 or 2, values are set in the 'conf:sca:ove' cmd
    // returns samplesize, is valid after successful "conf:dev" command
    int DLLCALL multiDaqGetSampleSize(int dev); // in bytes, values are set in 'conf:dev' command

    // returns number of bytes, they will be a multiple of minaligned
    // returns -1 for fatal error and -2 for timeouted, (-2 is quite normal after the 'abort' command)
    // minaligned should be the calculated samplesize
    // user has to provide the buffer *data
    int DLLCALL multiDaqGetStreamingData(int dev, char *data, int minaligned, int maxSize);

    // gets the last errormessage, if no error occurred this is an empty string
    // returns NULL pointer in case of an error
    char *DLLCALL multiDaqGetLastError(int dev); // call will clear the errormessage

    // clear and get fatal system Errors, which are not monitored by GetLastError()
    void DLLCALL multiDaqClearSystemErrors(void);
    // returns empty string, if all ok or list of hexadecimal error numbers
    // Value 0x0 tells: no error on that channel
    char *DLLCALL multiDaqGetSystemErrors(void);

    // handle with care, they are designed for synchronisation purposes of multiple devices
    // commands bettween will fire in the high priority thread after EnableTX()
    // and the Timestamp collector resumes
    int DLLCALL multiDaqDisableTx(void); // disable all transmissions for all devices
    int DLLCALL multiDaqEnableTx(void);  // enables again

    // litte helper for Timing, runs at 10 MHz on windows and 1 GHz on linux
    int64_t DLLCALL multiDaqGetTicks(void);

    // little helper to measure response times for the synchronized groups
    // Timestamps are based on 10 MHz clock on windows
    // after multiDaqEnableTx(), the timestamps will be measured after the call
    // so you have to wait a couple of ms to get the right values
    // *data will be filled with the timestamps (4 x int64_t =32 bytes)
    // memory must be provided by the user
    int DLLCALL multiDaqGetTimeStampsFromSynchronizedGroup(int dev, int64_t *data);

    // little helpers to get information from biovision devices
    // returns cstring with linefeed delimited lines [or empty cstring (no device detected)]
    const char *DLLCALL multiDaqListDevices();

    // little helper to get the version string of the dll
    const char *DLLCALL multiDaqGetVersion(void);

    /*---------------------- tMsg System related functions ---------------*/
    int DLLCALL tMsgInit();
    int DLLCALL tMsgRegisterAsMaster(void);
    int DLLCALL tMsgRegisterAsSlave(void);
    int DLLCALL tMsgUnregisterAsMaster(int);
    int DLLCALL tMsgUnregisterAsSlave(int);
    int DLLCALL tMsgSetSlaveCallback(void (*pfunc)(char *data), int address);
    int DLLCALL tMsgSetMasterCallback(void (*pfunc)(char *data));

    int DLLCALL tMsgSendMsgToSlave(char *, int address);
    int DLLCALL tMsgSendMsgToAllSlaves(char *);
    int DLLCALL tMsgSendMsgToMaster(char *, int address);
    int DLLCALL tMsgGetMasterMsg(char *, int address);
    int DLLCALL tMsgGetSlaveMsg(char *, int address);
    int DLLCALL tMsgGetTimeStamps(int64_t *, int address);
    int DLLCALL tMsgClearAllSlaveMessages();

    /*---------------------- gaphics ---------------*/
    int DLLCALL sdl2Window(int posx, int posy, int width, int height);
    int DLLCALL sdl2WindowConfigure(int devID, int samplesInWindow);
    int DLLCALL sdl2KillWindow(void);

#ifdef __cplusplus
} // __cplusplus defined.
#endif
