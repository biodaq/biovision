/* file biovision_multidaq.c
# Copyright (c) 2022, Tantor GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer
#    in the documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

#include "mex.h"
#ifndef USE_OCTAVE
#include "matrix.h"
#endif

#include <ctype.h>
#include <stdint.h>

#include "biovisionMultiDaq.h"
#include <string.h>

#define MAX_POSSIBLE_PARAMS 10
#define MAX_NUM_PORTS       4 // do not change this value
#define MAX_ANSWER_LEN      16384
#define MAX_SIZE_PORTNAME   256

static const char *myMatlabId = "biovision_multidaq";

static int debugLevel    = 0;
static int isRegistered  = 0;
static int isInitialized = 0;

static int   isOpen[MAX_NUM_PORTS];
static int   deviceType   = 0; // 0=biodaq 1=multidaq
static char *answerString = "";

#define SCRATCHBUF_SIZE 8192 // internal temporal buf of main thread
static char  scratchBuf[SCRATCHBUF_SIZE + 1];
static char *params[MAX_POSSIBLE_PARAMS];
static int   paramLen[MAX_POSSIBLE_PARAMS];

static unsigned num_params;
static char     inputBuffer[1024 * 1024]; // at the moment 1 MByte, which is quite a lot
static unsigned isTxDisabled;             // use for synchronized groups, valid for all ports

static unsigned sampSize[MAX_NUM_PORTS];
static unsigned sampFormat[MAX_NUM_PORTS];
static char     answerBuffer[MAX_ANSWER_LEN];

/*--------------------------------------------------------------------------------*\
\*--------------------------------------------------------------------------------*/
static void moduleExit(void) // TODO aufräumen
{
    int i;
    if (isInitialized)
        multiDaqDeInit();
    isInitialized = 0;
    if (debugLevel) mexPrintf("matlab: moduleExit()\n");
}
/*--------------------------------------------------------------------------------*\
\*--------------------------------------------------------------------------------*/
static int checkSCPI(char **arguments, const char *cmd, const char *needle)
{
    char *ps          = (char *)needle;
    char *p           = (char *)cmd;
    int   gotUpper    = 0;
    int   gotLower    = 0;
    int   searchLower = 0;
    int   i;
    *arguments = NULL;
    if (p[0] == ':')
        p++;
    for (i = 0; i < strlen(needle); i++)
    {
        if (isupper(*ps))
        {
            if (tolower(*p) != tolower(*ps))
                return 0;
            gotUpper = 1;
        }
        else
        {
            if (*ps != tolower(*ps))
            {
                searchLower = 1;
            }
            if (*p == ':')
            {
                if (gotUpper == 0 || (searchLower == 1 && gotLower == 0))
                    return 0;
                while (*ps != ':')
                {
                    ps++;
                    i++;
                }
                if (*ps == 0)
                    return 0;
                searchLower = 0;
                gotUpper    = 0;
            }
            if (*p == 0 || isspace(*p))
            {
                if (gotUpper == 0 || (searchLower == 1 && gotLower == 0))
                    return 0;
                *arguments = p;
                return 1;
            }
            if (searchLower)
            {
                if (tolower(*p) != tolower(*ps))
                    return 0;
                gotLower = 1;
            }
        }
        p++;
        ps++;
    }
    return 0;
}
/*--------------------------------------------------------------------------------*\
\*--------------------------------------------------------------------------------*/
static int analyseConfigCommand(const char *cmd, unsigned *size, unsigned format, unsigned adcOvs)
{
    int      i, k;
    int      xPar = 0;
    unsigned vals[5];
    *size      = 1; // never set them 0
    int cmdlen = strlen(cmd);
    for (i = 0; i < cmdlen; i++)
    {
        if (isspace(cmd[i]))
        {
            xPar = i + 1;
            break;
        }
    }
    if (xPar == 0)
        return 1;
    *size = 0;
    for (k = 0; k < 5; k++)
    {
        int tmp = atoi(&cmd[xPar]);
        if (tmp < 0)
            return 1; // TODO FIXME, that is wrong
        for (; i < cmdlen; i++)
        {
            if (cmd[i] == ',')
            {
                i++;
                xPar = i;
                break;
            }
        }
        if (k == 0 && format == 2) // reject 32 bit channels TODO error handling
        {
            if (tmp)
            {
                *size = tmp;
                if (debugLevel) mexPrintf("size format=2 set to %d\n", *size);
                return 0;
            }
        }
        if (k == 1)
            *size += adcOvs * tmp; // ADC16 oversampling
        else if (k == 2)
            *size += 6 * tmp; // IMU6
        else
            *size += tmp;
        if (i == cmdlen)
            break;
    }
    if (*size == 0 || *size > MAX_NUM_CHANNELS)
    {
        *size = 1;
        return 1;
    }
    return 0; // success
}
/*--------------------------------------------------------------------------------*\
\*--------------------------------------------------------------------------------*/
void mexFunction(int nlhs, mxArray *plhs[],       // outputs
                 int nrhs, const mxArray *prhs[]) // inputs
{
    volatile int i;
    volatile int nrows, ncols;
    int          isOutString    = 1; // else array
    int          isBinaryAnswer = 0; // else array
    int          isInt64Answer  = 0; // TODO make an enum of it
                                     //    int64_t      responseTime   = 0;
    int      portNum       = 0;
    int      nFill         = 0;
    mxArray *outResults    = NULL;
    char    *outErrMessage = NULL;

    if (isRegistered == 0)
    {
        mexAtExit(&moduleExit);
        // -------------------------------------setting defaults
        for (i = 0; i < MAX_NUM_PORTS; i++)
        {
            sampFormat[i] = 2;
        }
        isRegistered = 1;
    }
    char *answerString = "";
#ifdef _WIN32
    // mexPrintf("caller prio %d\n", GetThreadPriority(GetCurrentThread()));
#else
    // setPrio();
    // mexPrintf("prios OTHER: %d %d\n", sched_get_priority_min(SCHED_OTHER), sched_get_priority_max(SCHED_OTHER));
    // mexPrintf("prios FIFO: %d %d\n", sched_get_priority_min(SCHED_FIFO), sched_get_priority_max(SCHED_FIFO));
#endif
    if (nrhs < 1)
    {
        mexErrMsgIdAndTxt(myMatlabId, "function has no input.");
    }
    //------------------------------------ get Parameters ----------------------
    num_params = 0;
    for (i = 0; i < MAX_POSSIBLE_PARAMS; i++)
    {
        paramLen[i] = 0;
        params[i]   = ""; // to prevent possible exceptions
    }
    char *pScratch = scratchBuf;
    int   tmp      = SCRATCHBUF_SIZE;
    for (i = 0; i < nrhs; i++)
    {
        if (mxGetClassID(prhs[i]) == mxCHAR_CLASS)
        {
            if (mxGetM(prhs[i]) != 1)
            {
                if (debugLevel) mexPrintf("should not be, len = %d\n", mxGetN(prhs[i]));
                mexErrMsgIdAndTxt(myMatlabId, "biovision_multidaq allows only one dimensional char arrays as parameter");
            }
            params[i]   = mxGetData(prhs[i]);
            paramLen[i] = mxGetN(prhs[i]);
        }
        else
        {
            mexErrMsgIdAndTxt(myMatlabId, "biovision_multidaq allows only char arrays as parameter");
        }

#if 1                                            // TODO remove, when atoi() etc are out of code, than remove scratchbuf
        if (mxGetString(prhs[i], pScratch, tmp)) // must be a String
        {
            mexErrMsgIdAndTxt(myMatlabId, "function accepts only strings");
        }
        // mexPrintf("inputArg(%d) =%s len = %d\n", i, pScratch, strlen(scratchBuf));
        params[i] = pScratch;
        tmp -= strlen(pScratch) + 1;
        if (tmp < 20)
            mexErrMsgIdAndTxt(myMatlabId, "size of stringbuffer not sufficient");
        pScratch += strlen(pScratch) + 1;
#endif
        num_params++;
    }
    if (nlhs > 5)
    {
        mexErrMsgIdAndTxt(myMatlabId, "Too many output arguments");
    }
    //------------------------------------------------------------------------
    if (strncmp(params[0], "get", 256) == 0)
    {
        int selectedPort = 0;
        if (num_params != 2)
            mexErrMsgIdAndTxt(myMatlabId, "Command Get needs one parameter, the channel number");
        i = atoi(params[1]);
        if (i == 0 || i > MAX_NUM_PORTS)
            mexErrMsgIdAndTxt(myMatlabId, "Command parameter out of Range, valid is 1 to MAX_NUM_PORTS");
        portNum = i - 1;
        if (isOpen[portNum])
        {
            int nIndex = 0;
            if (sampFormat[portNum] == 4) nIndex = 1;
            nFill = multiDaqGetStreamingData(portNum, (char *)inputBuffer, (sampSize[portNum] + nIndex) * sampFormat[portNum], sizeof(inputBuffer)); // TODO
            if (debugLevel)
                mexPrintf("get received %d bytes on port%d format=%d sampsize=%d\n", nFill, portNum, sampFormat[portNum], sampSize[portNum]);
            int32_t *p32Data = (int32_t *)inputBuffer; // TODO multiDaq 4 byte vs 2 byte
            int16_t *p16Data = (int16_t *)inputBuffer; // TODO multiDaq 4 byte vs 2 byte
            //     nFill           = 0;
            if (nFill >= 0)
            {
                ncols = sampSize[portNum];
                if (sampFormat[portNum] == 4)
                    ncols++;
                nrows = nFill / (sampFormat[portNum] * ncols);
            }
            else
            {
                nrows = 1;
                ncols = sampSize[portNum];
            }
            if (debugLevel)
            {
                if (debugLevel)
                    mexPrintf("Try Create outResults[%d] = mat(%d,%d) nFill=%d\n", portNum, nrows, ncols, nFill);
            }
            if (nFill == -1)
            {
                outResults = mxCreateDoubleMatrix(0, ncols, mxREAL);

                outErrMessage = "warning: stream timed out";
            }
            else
            {
                outResults = mxCreateDoubleMatrix(nrows, ncols, mxREAL);
            }
            if (outResults == NULL)
                mexErrMsgIdAndTxt(myMatlabId, "panic: could not allocate memory");
            double *dataOut = mxGetPr(outResults);
            if (dataOut != NULL)
            {
                int    k   = 0;
                double tmp = (double)nFill;
                // dataOut[0]          = .12345 + (double)i;

                if (sampFormat[portNum] == 4)
                {
                    for (k = 0; k < nrows; k++)
                    {
                        int ii;
                        for (ii = 0; ii < ncols; ii++)
                            dataOut[nrows * ii + k] = (double)*p32Data++;
                    }
                }
                else
                {
                    for (k = 0; k < nrows; k++)
                    {
                        int ii;
                        for (ii = 0; ii < ncols; ii++)
                            dataOut[nrows * ii + k] = (double)*p16Data++;
                    }
                }
            }
        }
        else
            mexErrMsgIdAndTxt(myMatlabId, "get() port not open");
        isOutString = 0;
        goto ALL_DONE;
    }
    //------------------------------------------------------------------------
    if (strncmp(params[0], "init", 256) == 0)
    {
        debugLevel = 0;
        if (num_params >= 2)
        {
            if (strncmp(params[1], "debug", 256) == 0)
            {
                debugLevel = 1;
                // if (debugLevel) mexPrintf("##################");
            }
        }
        if (isInitialized)
        {
            mexErrMsgIdAndTxt(myMatlabId, "You try to initialize an initialized Driver again.");
        }
        multiDaqInit(debugLevel);
        for (i = 0; i < MAX_NUM_PORTS; i++)
            sampFormat[i] = 2;
        isInitialized = 1;
        outResults    = mxCreateString("");
    }
    //------------------------------------------------------------------------
    if (strncmp(params[0], "deinit", 256) == 0)
    {
        if (num_params != 1)
        {
            mexErrMsgIdAndTxt(myMatlabId, "Command deinit requires no parameter");
        }
        // answerString = "";        outResults= mxCreateString("");
        outResults = mxCreateString("");
        multiDaqDeInit();
        // isRegistered = 0;
        if (!isInitialized)
            mexWarnMsgIdAndTxt(myMatlabId, "Nothing to do in Deinit, did you call it twice?");
        isInitialized = 0;
    }
    //------------------------------------------------------------------------
    if (strncmp(params[0], "open", 256) == 0)
    {
        if (num_params != 3)
            mexErrMsgIdAndTxt(myMatlabId, "Command open requires two parameters");
        i = atoi(params[1]);
        if (i == 0 || i > MAX_NUM_PORTS)
            mexErrMsgIdAndTxt(myMatlabId, "Command open needs a string as parameter, valid Range is from 1 to MAX_NUM_PORTS");
        portNum = i - 1;
        if (debugLevel) mexPrintf("open %s\n", params[2]);
        char *p     = params[2];
        int   count = 0;
        for (i = 0; p[i]; i++)
        {
            if (p[i] == '\t')
            {
                p[i] = 0;
                count++;
            }
        }
        if (count < 2)
            mexErrMsgIdAndTxt(myMatlabId, "Error in parameter string");
        if (debugLevel)
            mexPrintf("####:%s\n%s\n", params[2], p);
        if (strncmp(p, "multi", 5) == 0)
        {
            sampFormat[portNum] = 2;
        }
        else if (strncmp(p, "bio", 3) == 0)
        {
            sampFormat[portNum] = 4;
            if (debugLevel) mexPrintf("####: sampformat = 4\n", params[2], p);
        }
        else if (strncmp(p, "logger", 6) == 0)
        {
            sampFormat[portNum] = 4;
        }
        else if (strncmp(p, "trigger", 7) == 0)
        {
        }
        else
            mexErrMsgIdAndTxt(myMatlabId, "unknown device name");
        p = p + strlen(p) + 1;
        if (debugLevel)
            mexPrintf("open port %s\n", p);
        if (multiDaqOpen(portNum, p))
        {
            outErrMessage = "failed to open port";
        }
        isOpen[portNum] = 1;
        outResults      = mxCreateString("");
        goto ALL_DONE;
    }
    //------------------------------------------------------------------------
    if (strncmp(params[0], "close", 256) == 0)
    {
        if (num_params != 2)
            mexErrMsgIdAndTxt(myMatlabId, "Command close requires exact one parameter");
        i = atoi(params[1]);
        if (i == 0 || i > MAX_NUM_PORTS)
            mexErrMsgIdAndTxt(myMatlabId, "Command close needs a string as parameter, valid Range is from 1 to MAX_NUM_PORTS");
        portNum         = i - 1;
        isOpen[portNum] = 0;
        multiDaqClose(portNum);
        outResults = mxCreateString("");
        goto ALL_DONE;
    }
    //------------------------------------------------------------------------
    if (strncmp(params[0], "cmd", 256) == 0)
    {
        int waitOnAnswer = 1;
        if (num_params < 3 || num_params > 4)
            mexErrMsgIdAndTxt(myMatlabId, "Command cmd requires two or three parameters");
        i = atoi(params[1]);
        if (i == 0 || i > MAX_NUM_PORTS)
            mexErrMsgIdAndTxt(myMatlabId, "Command cmd error second parameter, valid Range is from 1 to MAX_NUM_PORTS");
        portNum = i - 1;
        if (num_params == 4)
        {
            if (strncmp(params[3], "stream", 256) == 0)
            {
                waitOnAnswer = 0;
                //                if (debugLevel) mexPrintf("stream command\n");
            }
            else if (debugLevel)
                mexPrintf("Warning: ignored the unknown Parameter 4"); // octave don not know mexWarnMsgIdAndTxt
        }
        // special operation for the abort command TODO check whether neccessary
        if (strncmp(params[2], "abort", 5) == 0)
        {
            if (debugLevel)
                mexPrintf("found abort\n");
            waitOnAnswer = 0;
        }
        // special operation for the device configure command to get the samplesize and sampleformat
        char *args = NULL;
        if (checkSCPI(&args, params[2], "CONFigure:DEVice"))
        // if ((strncmp(params[2], "conf:dev", 8) == 0) || (strncmp(params[2], "configure:dev", 13) == 0))
        {
            int ovs = multiDaqGetAdcOversampling(portNum);
            // TODO argument list is in args now
            if (analyseConfigCommand(params[2], &sampSize[portNum], sampFormat[portNum], ovs))
            {
                outErrMessage = "configuration Parameters are invalid";
            }
            // sampSize[portNum] = 5;
            // mexPrintf("Ssampsize =%d\n", sampSize[portNum]);
        }
        // special operation for the biodaq device lis command
        if (checkSCPI(&args, params[2], "CONFigure:SCAn:LISt"))
        // if (strncmp(params[2], "conf:sca:lis", 12) == 0)
        {
            // simply count the commas
            char *p     = params[2];
            int   count = 1;
            while (*p)
            {
                if (*p == ',')
                    count++;
                p++;
            }
            sampSize[portNum] = count;
        }
        if (debugLevel)
            mexPrintf("Sampsize =%d\n", sampSize[portNum]);
        int len;
        if (waitOnAnswer)
        {

            answerString = multiDaqSendCmd(portNum, params[2], &len, &isBinaryAnswer);
            // mexPrintf("sampleSizesfromdriver = %d\n", multiDaqGetSampleSize(portNum));
            // mexPrintf("sampleSizesorig = %d\n", sampSize[portNum]);
            // remove trailing \n\r
            char *p = answerString;
            while (*p) p++;
            while (p != answerString)
            {
                p--;
                if (*p == 10 || *p == 13) *p = 0;
                else break;
            }
        }
        else
        {
            int tmp = multiDaqSendCmdWhileStreaming(portNum, params[2]);
            if (tmp)
            {
                answerString = "Error: could not execute multiDaqSendCmdWhileStreaming()";
            }
            else
                answerString = "";
        }
        if (isBinaryAnswer)
        {
            outResults      = mxCreateNumericMatrix(1, len, mxUINT8_CLASS, mxREAL); // TODO clear the cast operation
            int8_t *dataOut = (int8_t *)mxGetPr(outResults);                        // the output array
            memcpy(dataOut, answerString, len);
        }
        else
            outResults = mxCreateString(answerString);
        goto ALL_DONE;
    }
    //------------------------------------------------------------------------
    if (strncmp(params[0], "binblock", 256) == 0)
    {
        if (debugLevel) mexPrintf("##############binblock %d\n", paramLen[2]);
        if (num_params != 3)
            mexErrMsgIdAndTxt(myMatlabId, "Command 'binblock' the port number and a char array");
        i = atoi(params[1]);
        if (i == 0 || i > MAX_NUM_PORTS)
            mexErrMsgIdAndTxt(myMatlabId, "Command cmd error second parameter, valid Range is from 1 to MAX_NUM_PORTS");
        portNum = i - 1;
        if (paramLen[2] < 1 || paramLen[2] > 4096)
        {
            if (debugLevel)
                mexPrintf("Error 'binblock': invalid parameter\n");
            outErrMessage = "Len of the block must be between 1 and 4096 inclusive";
        }
        else
        {
            if (debugLevel) mexPrintf("######################## %d\n", paramLen[2]);
            // now prhs[2] should be the data array with the values
            if (multiDaqSendSCPIbinBlock(portNum, params[2], paramLen[2]))
            {
                outErrMessage = "Command failed";
            }
        }
        outResults = mxCreateString("");
    }
    //------------------------------------------------------------------------
    if (strncmp(params[0], "txqueue", 256) == 0)
    {
        if (num_params != 2)
            mexErrMsgIdAndTxt(myMatlabId, "Command get requires one parameter");
        unsigned nn = atoi(params[1]);
        if (i == 0 || i > MAX_NUM_PORTS)
            mexErrMsgIdAndTxt(myMatlabId, "Command get needs a string as parameter, valid Range is from 1 to MAX_NUM_PORTS");
        int err;
        if (nn == 1)
        {
            isTxDisabled = 0;
            multiDaqEnableTx();
        }
        else
        {
            isTxDisabled = 1;
            err          = multiDaqDisableTx();
        }
        if (err)
        {
            outErrMessage = "txqueue failed";
        }
        if (debugLevel)
            mexPrintf("TxQueue = %u\n", nn);

        outResults = mxCreateString("");
        goto ALL_DONE;
    }
    //------------------------------------------------------------------------
    if (strncmp(params[0], "getticks", 256) == 0)
    {
        if (num_params != 1)
            mexErrMsgIdAndTxt(myMatlabId, "Command get requires no parameter");
        unsigned nn      = atoi(params[1]);
        outResults       = mxCreateNumericMatrix(1, 1, mxINT64_CLASS, mxREAL);
        int64_t *dataOut = (int64_t *)mxGetPr(outResults); // the output array
        *dataOut         = multiDaqGetTicks();
        goto ALL_DONE;
    }
    //------------------------------------------------------------------------
    if (strncmp(params[0], "gettimestamps", 256) == 0)
    {
        if (num_params != 2)
            mexErrMsgIdAndTxt(myMatlabId, "Command gettimestamps requires one parameter");
        unsigned nn = atoi(params[1]);
        if (nn == 0 || nn > MAX_NUM_PORTS)
            mexErrMsgIdAndTxt(myMatlabId, "Command get needs a string as parameter, valid Range is from 1 to MAX_NUM_PORTS");
        nn -= 1; // C count!
        int64_t results[4];
        multiDaqGetTimeStampsFromSynchronizedGroup(nn, results);               //   if (debugLevel) mexPrintf("ResponseTime[%d] = %d us\n", nn, (int)responseTime);
        outResults       = mxCreateNumericMatrix(1, 4, mxINT64_CLASS, mxREAL); // TODO clear the cast operation
        int64_t *dataOut = (int64_t *)mxGetPr(outResults);                     // the output array
        *dataOut++       = results[0];
        *dataOut++       = results[1];
        *dataOut++       = results[2];
        *dataOut++       = results[3];
        goto ALL_DONE;
    }
    //------------------------------------------------------------------------
    if (strncmp(params[0], "listdevices", 256) == 0)
    {
        if (num_params != 1)
            mexErrMsgIdAndTxt(myMatlabId, "Command get requires one parameter");
        char *p     = (char *)multiDaqListDevices();
        int   count = 0;
        for (i = 0; p[i]; i++)
        {
            if (p[i] == '\n')
            {
                p[i] = 0;
                count++;
            }
        }
        outResults = mxCreateCellMatrix(count, 1);
        for (mwIndex i = 0; i < count; i++)
        {
            mxArray *str = mxCreateString(p);
            p += strlen(p) + 1;
            mxSetCell(outResults, i, mxDuplicateArray(str));
            mxDestroyArray(str);
        }
        goto ALL_DONE;
    }

ALL_DONE:
    if (outResults != NULL)
        plhs[0] = outResults;
    else
        mexErrMsgIdAndTxt(myMatlabId, "ups, unknown command string\n"
                                      "known are: 'init','deinit','open','close','cmd',\n"
                                      "'get','txqueue','getticks','getresponsetime'");
    if (nlhs >= 2)
    {
        char *tmp = (outErrMessage == NULL) ? "" : outErrMessage;
        plhs[1]   = mxCreateString(tmp);
    }
}
