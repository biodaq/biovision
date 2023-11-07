%viewTdf.m
% example file to handle tdf files

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
% NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

[FileName, PathName] = uigetfile('*.tdf', 'Select the data-file');
file = sprintf('%s', FileName);
Nsegments = 0;
% get data from file
[trial] = getTdfData(file);

% plot ADC data, if any present
Np = size(trial.adc16)(1, 2);

if Np >= 1
    figure(1);

    for i = 1:Np
        subplot(Np, 1, i);
        plot(trial.adc16(i).data);
        title(sprintf('ADC %d Data', i));
    end

end

% plot IMU data, if any present
Np = size(trial.imu6)(1, 2);

if Np >= 1
    figure(2);

    for i = 1:Np
        subplot(Np, 1, i);
        plot(trial.imu6(i).accdata); % 3 dim Array
        title(sprintf('Acc %d Data', i));
    end

    figure(3);

    for i = 1:Np
        subplot(Np, 1, i);
        plot(trial.imu6(i).gyrodata);
        title(sprintf('Gyro %d Data', i));
    end

end
