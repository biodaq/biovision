/* info.c
   get the idn strings of all connected biovision devices
*/

#include "serialportinfo.h"
#include <biovisionMultiDaq.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv)
{
    char *ans;
    int   bytesReceived;
    int   isBinaryAnswer;

    if (multiDaqInit(0)) // argument is debuglevel, if set, it will print messages to stdout
    {
        printf("---- init failed\n");
        return 1;
    }
    multiDaqClearSystemErrors(); // if you want to monitor system errors

    char        result[1024];
    const char *tmp; // this is a cstring of lines with LF as separator
    printf("\n########################### info.exe\n");
    printf("\nResult DLL Version: %s\n\n", multiDaqGetVersion());

    tmp = multiDaqListDevices();              // this is a cstring of lines with LF as separator
    strncpy(result, tmp, sizeof(result) - 1); // keep a copy here for strtok
    printf("Results listdevices:\n%s\n\n", result);

    if (strlen(result) == 0)
    {
        printf("no device found: exit now\n");
        multiDaqDeInit();
        return 1;
    }
    /* get the first token */
    char *token = strtok(result, "\n");
    /* walk through other tokens */
    while (token != NULL)
    {
        printf("open device: %s\n", token);

        if (multiDaqOpen(0, token))
        {
            printf("---- Error: Could not open port %s\n", token);
            printf("---- is it busy?\n");
            token = strtok(NULL, "\n");
            continue;
        }
        ans = multiDaqSendCmd(0, "*idn?", &bytesReceived, &isBinaryAnswer); // response on *idn? is always a string
        printf("response *idn?: %s\n", ans);
        multiDaqClose(0);
        token = strtok(NULL, "\n");
    }
    if (strlen(multiDaqGetSystemErrors())) printf("system Errrors occurred, errnumbers: %s\n", multiDaqGetSystemErrors());
    multiDaqDeInit();
    return EXIT_SUCCESS;
}
