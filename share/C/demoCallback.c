#include <biovisionMultiDaq.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#ifdef _WIN32
#include <windows.h> // for Sleep only
#else
#include <unistd.h>
void Sleep(int ms) // Sleep for Linux
{
    usleep(ms * 1000); // That are microseconds
}
#endif

static int isBioDaq=0;     // set one for bioDaq, 0 for multiDaq

static int nBytes = 0, nCallback = 0, nChan=3;
static int maxNbytes = 0;
static int mySampleSize=0;


void       myCallback(char *in, int n)
{
    int i, k;
    nBytes += n;
    nCallback++;
    if (n > maxNbytes) maxNbytes = n;

    int sampleSize = multiDaqGetSampleSize(0);//mySampleSize;//

    int8_t *p8 = (int8_t *)in;
    int16_t *p16 = (int16_t *)p8;
    int32_t *p32 = (int32_t *)p8;

    // raw data are int16_t (short), do what you want to do
    // printf is not really allowed here
    // but it works unless you do not use it in main
    // at the same time
    // it is only a demo, no production code !!
    #if 1
    //printf("----- received %d bytes\n", n);
    for (i = 0; i < n/sampleSize ; i ++) // loop samples
    {
        if(isBioDaq)
        {
            int step=sampleSize/4;
            for (k = 0; k < (sampleSize/4); k++) printf(" %d", p32[(k + i*step)]);
        }
        else
        {
            int step=sampleSize/2;
            for (k = 0; k < (sampleSize/2); k++) printf(" %d", p16[(k + i*step)]);
        }
        printf("\n");
    }
    #endif
    // You may test what happens, if this routine takes long time
    // Sleep(100); // 100 ms sleep
}

int main(int argc, char **argv)
{
    //int nChan           = 2; // 1 .. 8 possible

    int         i;
    char       *ans;
    int         Cnt = 0;
    char       *p8;
    char        result[1024];
    int         bytesReceived;
    int         isBinaryAnswer;
    const char *tmp = multiDaqListDevices();  // call without initializing the driver is possible
    strncpy(result, tmp, sizeof(result) - 1); // keep a copy here for strtok

    printf("Result listdevices(%d):\n%s\n\n", (int)strlen(result), result);
    if (strlen(result) == 0)
    {
        printf("no device found: exit now\n");
        return 1;
    }
    /* get the first token */
    char *token   = strtok(result, "\n");
    char *comPort = "";
    /* walk through other tokens */
    while (token != NULL)
    {
        if (strncmp(token, "bio", 3) == 0) // look for the first valid bio device
        {
        isBioDaq=1;
            printf("found device %s\n", token);
            comPort = token;
            mySampleSize = 4*(1+nChan);
            break;
        }
        if (strncmp(token, "multi", 3) == 0) // look for the first valid multi device
        {
            isBioDaq=0;
            printf("found device %s\n", token);
            comPort = token;
            mySampleSize = 2*nChan;
            break;
        }
        token = strtok(NULL, "\n");
    }
    if (strlen(comPort) == 0)
    {
        printf("Error: no device found, exit now\n");
        return 1;
    }
    printf("device is on comPort: %s\n", comPort);

    // initialize the driver
    if (multiDaqInit(0)) // argument is debuglevel, if set, it will print messages to stdout
    {
        printf("---- init failed\n");
        return 1;
    }

    if (multiDaqOpen(0, comPort))
    {
        printf("---- Could not open port\n");
        multiDaqDeInit();
        return 1;
    }

    // set the datarate
    ans = multiDaqSendCmd(0, "conf:sca:rat 500", &bytesReceived, &isBinaryAnswer); // a nonzero response indicates an error
    // if(bytesReceived) // this or next line, it is the same
    if ((ans == NULL) || strlen(ans) != 0)
    {
        printf("---- Error by set rate: %s\n", ans);
        goto err_exit;
    }

    //int  samplesize = nChan * 4+4;
    char buf[100];
    //sprintf(buf, "conf:dev %d,0,0", nChan);
    sprintf(buf, "conf:sca:lis 0,1,2");
    if (multiDaqSendCmd(0, buf, &bytesReceived, &isBinaryAnswer) == NULL)
    {
        printf("SendCmd failed!\n");
        goto err_exit;
    }
    if (bytesReceived)
    {
        printf("Error configuring the device\n");
        goto err_exit;
    }
    Sleep(100);
    mySampleSize =multiDaqGetSampleSize(0);
    printf("samplesize = %d bytes\n",multiDaqGetSampleSize(0));
    Sleep(100); // configuring will take 50 milliseconds

    //------------ set the callback function, device must be open
    // after that command, internal queues fo the driver will not be serviced
    // all data are directed to the callback function
    multiDaqSetCallbackData(0, myCallback);

    // start the aquisition
    if (multiDaqSendCmdWhileStreaming(0, "init"))
    {
        printf("Error sending command\n");
        goto err_exit;
    }

    // do nothing for 3 seconds, callbacks will be active then
    puts("please wait 3 seconds");
    Sleep(3000);
    // stop the aquisition, after that, the command multiDaqGetStreamingData() will timeout automaticly
    if (multiDaqSendCmdWhileStreaming(0, "abort"))
    {
        printf("Error sending Command\n");
    }
    multiDaqClose(0);
    multiDaqDeInit();
    printf("There were %d Callbacks,  %d bytes received, that are %d Samples\n", nCallback, nBytes, nBytes / mySampleSize );
    printf("Callback delivered maximal %d bytes, that are %d samples\n", maxNbytes, maxNbytes / mySampleSize );
    return EXIT_SUCCESS;
err_exit:
    multiDaqClose(0);
    multiDaqDeInit();
    printf("---- some error occurred\n");
    return 1;
}
