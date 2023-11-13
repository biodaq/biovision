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

static int nBytes = 0, nCallback = 0, nChan;
static int maxNbytes = 0;
void       myCallback(char *in, int n)
{
    int i, k;
    nBytes += n;
    nCallback++;
    if (n > maxNbytes) maxNbytes = n;
    int16_t *p = (int16_t *)in;
    // raw data are int16_t (short), do what you want to do
    // printf is not really allowed here
    // but it works unless you do not use it in main
    // at the same time
    // it is only a demo, no production code !!
    printf("----- received %d bytes\n", n);
    for (i = 0; i < n / nChan / 2; i += nChan) // loop samples
    {
        for (k = 0; k < nChan; k++) printf(" %d", p[k + i]);
        printf("\n");
    }
    // You may test what happens, if this routine takes long time
    // Sleep(100); // 100 ms sleep
}

int main(int argc, char **argv)
{
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
        if (strncmp(token, "multi", 5) == 0) // look for the first valid multi device
        {
            printf("found device %s\n", token);
            comPort = token;
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
    ans = multiDaqSendCmd(0, "conf:sca:rat 1000", &bytesReceived, &isBinaryAnswer); // a nonzero response indicates an error
    // if(bytesReceived) // this or next line, it is the same
    if ((ans == NULL) || strlen(ans) != 0)
    {
        printf("---- Error by set rate: %s\n", ans);
        goto err_exit;
    }

    nChan           = 5; // 1 .. 8 possible
    int  samplesize = nChan * 2;
    char buf[100];
    sprintf(buf, "conf:dev 0,%d,0", nChan);
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
    printf("There were %d Callbacks,  %d bytes received, that are %d Samples\n", nCallback, nBytes, nBytes / (nChan * 2));
    printf("Callback delivered maximal %d bytes, that are %d samples\n", maxNbytes, maxNbytes / (nChan * 2));
    return EXIT_SUCCESS;
err_exit:
    multiDaqClose(0);
    multiDaqDeInit();
    printf("---- some error occurred\n");
    return 1;
}
