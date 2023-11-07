%getTdfData
%  [trial] = getTdfData(fName)
%   converts *.tdf file to structured matlab data.
%   returns trial:             metadata of measurement and measurement data
%               imu6:           Array of structured IMU data with channel description
%               adc16:          Array of structured ADC data with description
%               sampleRate      integer number (IMU samplerate)
%               sampleSize      in bytes
%               adcOversample   ADC is normally oversampled samplerate = samplerate(IMU) * adcOversample
%               timestamp       unix Time at Start of measurement
%
%               substructures:
%                     imu6(i):   rangeAcc rangeGyro name accdata(n) gyrodata(n)
%                                accdata,gyrodata themself are Array(n,3)
%                     adc16(i):  ymin ymax scale intercept name data(n)
%
% Copyright (c) 2023, Tantor GmbH
% All rights reserved.
%
% Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
% 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
% 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer
%     in the documentation and/or other materials provided with the distribution.
%
% THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING,
% BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
% SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
% DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
% INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
% NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
function trial = getTdfData(filename)
    startData = 0;
    fp = fopen(filename);

    for i = 1:10000 % search the first zero in file
        x = fread(fp, [1], 'uint8');

        if x == 0
            break;
        end

    end

    startData = i; % position of first data
    frewind(fp);
    isError = false;
    imu6cnt = 1; % code is simpler if we start with 1 (see below)
    adc16cnt = 1;
    matchcnt = 0;
    %--------------------------------- parse header ---------------------------
    while ftell(fp) < startData - 1
        tline = fgetl(fp);
        % throw away empty and comment lines
        if (length(tline) == 0 || (tline(1) == '!' || tline(1) == '#' || tline(1) == ';'))
            continue;
        end

        %disp(tline);
        tmp = strfind(tline, 'sampleRate');

        if length(tmp) > 0 && tmp(1) == 1
            c = strsplit(tline, '=');

            if length(c) != 2
                isError = true;
            end

            matchcnt = matchcnt + 1;
            trial.sampleRate = str2num(c{:, 2});
        end

        tmp = strfind(tline, 'sampleSize');

        if length(tmp) > 0 && tmp(1) == 1
            c = strsplit(tline, '=');

            if length(c) != 2
                isError = true;
            end

            matchcnt = matchcnt + 1;
            trial.sampleSize = str2num(c{:, 2});
        end

        tmp = strfind(tline, 'adcOversample');

        if length(tmp) > 0 && tmp(1) == 1
            c = strsplit(tline, '=');

            if length(c) != 2
                isError = true;
            end

            matchcnt = matchcnt + 1;
            trial.adcOversample = str2num(c{:, 2});
        end

        tmp = strfind(tline, 'timestamp');

        if length(tmp) > 0 && tmp(1) == 1
            c = strsplit(tline, '=');

            if length(c) != 2
                isError = true;
            end

            matchcnt = matchcnt + 1;
            trial.timestamp = str2num(c{:, 2});
        end

        tmp = strfind(tline, 'adc16');

        if length(tmp) > 0 && tmp(1) == 1
            c = strsplit(tline, '\t');

            if length(c) != 6
                isError = true;
            end

            matchcnt = matchcnt + 1;
            trial.adc16(adc16cnt).ymin = str2num(c{:, 2});
            trial.adc16(adc16cnt).ymax = str2num(c{:, 3});
            trial.adc16(adc16cnt).scale = str2num(c{:, 4});
            trial.adc16(adc16cnt).intercept = str2num(c{:, 5});
            trial.adc16(adc16cnt).name = c{:, 6}; % get name
            adc16cnt = adc16cnt + 1;
        end

        tmp = strfind(tline, 'imu6');

        if length(tmp) > 0 && tmp(1) == 1
            c = strsplit(tline, '\t');

            if length(c) != 4
                isError = true;
            end

            matchcnt = matchcnt + 1;
            %str2num(tline)
            trial.imu6(imu6cnt).rangeAcc = str2num(c{:, 2}); % get rangeacc rangegyro
            trial.imu6(imu6cnt).rangeGyro = str2num(c{:, 3});
            trial.imu6(imu6cnt).name = c{:, 4}; % get name
            imu6cnt = imu6cnt + 1;
        end

    end

    % correct to real count of devices (see above)
    imu6cnt = imu6cnt - 1;
    adc16cnt = adc16cnt - 1;
    %----------------------- check plausibilty of header -----------------------
    %TODO refinement
    if isError
        error('format error in header');
    end

    if imu6cnt == 0 && adc16cnt == 0
        error('no data in file');
    end

    if trial.sampleSize == 0 || trial.sampleRate == 0
        error('strange header');
    end

    if matchcnt < 5
        error('header empty?');
    end

    %----------------------------- set filepointer -----------------------------
    fseek(fp, 0, 'eof');
    filelength = ftell(fp);
    numSamples = (filelength - startData) / trial.sampleSize

    if numSamples == 0
        error('no data in file');
    end

    fseek(fp, startData, 'bof');
    %------------------------------------- get data ----------------------------
    A = fread(fp, 'int16');
    B = reshape(A, [trial.sampleSize / 2, numSamples])'; %samplesize is in bytes
    dataidx = 1;
    adcstep = trial.adcOversample; %oversampling factor
    %-------------------------------- extract adc data -------------------------
    for cntadc = 1:adc16cnt
        A = upsample(B(:, dataidx), adcstep);

        for k = 1:(adcstep - 1)
            A = A + upsample(B(:, dataidx + adc16cnt * (k - 1)), adcstep, k);
        end

        m = (1 / (2 ^ 15)) * .5 * (trial.adc16(cntadc).ymax - trial.adc16(cntadc).ymin) * trial.adc16(cntadc).scale;
        b = (1 / (2 ^ 15)) * .5 * (trial.adc16(cntadc).ymax + trial.adc16(cntadc).ymin) * trial.adc16(cntadc).scale + trial.adc16(cntadc).intercept;
        trial.adc16(cntadc).data = m * A + b;
        dataidx = dataidx + 1;
    end

    dataidx = dataidx + (adcstep - 1) * adc16cnt;
    %---------------------------------- extract imu data -----------------------
    for cntimu = 1:imu6cnt
        trial.imu6(cntimu).accdata = trial.imu6(cntimu).rangeAcc / 32768 * B(:, dataidx:dataidx + 2);
        trial.imu6(cntimu).gyrodata = trial.imu6(cntimu).rangeGyro / 32768 * B(:, dataidx + 3:dataidx + 5);
        dataidx = dataidx + 6;
    end

    fclose(fp);
end
