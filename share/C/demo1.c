/* demo1.c (requires a connected multidaq device)

   copyright: Tantor GmbH, 2022
   All rights reserved.

   Redistribution and use in source and binary forms, with or without
   modification, are permitted provided that the following conditions are met:
   1. Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.
   2. Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer
      in the documentation and/or other materials provided with the distribution.

   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
   AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
   THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
   PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
   EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
   PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
   PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
   LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
   NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
   EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/
/*
   Demonstrates simple data aquisition using the C interface.
   it connects to the first available device and collects data for 5 second
*/

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

// You have to provide a Receive Buffer
char    dat[65536];          // buffer for data in the loop
int32_t bigbuf[1024 * 1024]; // buffer for all collected data
char    result[1024];

int main(int argc, char **argv)
{
    int            i;
    char          *ans;
    int            Cnt = 0;
    char          *p8;
    const int16_t *p16 = (int16_t *)bigbuf;
    int            bytesReceived;
    int            isBinaryAnswer;
    const char    *tmp = multiDaqListDevices(); // call without initializing the driver is possible
    strncpy(result, tmp, sizeof(result) - 1);   // keep a copy here for strtok

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
#if 0
    // You may set the order of the analog input channels
    // first received channel is 0, second is input channel 7 (respective 1 and 8, if you count from 1)
    multiDaqSendCmd(0, "conf:sca:lis 0,7", &bytesReceived, &isBinaryAnswer);
    if (bytesReceived)
    {
        printf("Error by set list\n");
        goto err_exit;
    }
#endif

    int  nChan      = 2; // 1 .. 8 possible
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

    // start the aquisition
    if (multiDaqSendCmdWhileStreaming(0, "init"))
    {
        printf("Error sending command\n");
        goto err_exit;
    }

    //------------------ aquisition loop
    p8 = (char *)bigbuf;
    for (i = 0; i < 10; i++)
    {
        Sleep(100);
        int nBytes = multiDaqGetStreamingData(0, dat, samplesize, sizeof(dat));
        if (nBytes == -1)
        {
            printf("---- timeouted\n");
            goto err_exit;
        }
        else
        {
            printf("---- got %d samples\n", nBytes / samplesize);
            memcpy(p8, dat, nBytes);
            p8 += nBytes;
            Cnt += nBytes / samplesize; // count the samples
        }
        // if (Cnt > 1000) break;
    }

    // stop the aquisition, after that, the command multiDaqGetStreamingData() will timeout automaticly
    if (multiDaqSendCmdWhileStreaming(0, "abort"))
    {
        printf("Error sending Command\n");
    }
    multiDaqClose(0);
    multiDaqDeInit();

    // print the results
    double scal = 1. / (double)(1 << 15); // scale to +-1
    scal *= 6.00;                         // now you have data in volts
    int cols = nChan;
    int rows = Cnt;
    for (i = 0; i < rows; i++)
    {
        int k;
        printf("data[%d]:", i);
        for (k = 0; k < cols; k++) printf(" %1.5f", scal * (double)p16[cols * i + k]);
        printf("\n");
    }
    printf("---- all ok Cnt =%d\n", Cnt);
    return EXIT_SUCCESS;
err_exit:
    multiDaqClose(0);
    multiDaqDeInit();
    printf("---- some error occurred\n");
    return 1;
}
