/* info.c

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
    list all connected devices and print out some information
*/
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
    printf("\n########################### biovisionDevInfo\n");
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
        ans = multiDaqSendCmd(0, "syst:vers:svn?", &bytesReceived, &isBinaryAnswer); // response on *idn? is always a string
        printf("detected build version: %s\n", ans);
        multiDaqClose(0);
        token = strtok(NULL, "\n");
    }
    if (strlen(multiDaqGetSystemErrors())) printf("system Errrors occurred, errnumbers: %s\n", multiDaqGetSystemErrors());
    else printf("No System Errors detected, all ok\n");
    multiDaqDeInit();
    return EXIT_SUCCESS;
}
