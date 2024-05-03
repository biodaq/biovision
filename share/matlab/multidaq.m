classdef multidaq < handle
    %% Public properties
    properties (Access = public)
        interface = 'usb';
        idnAnswer = '';
        nImu6 = 0;
        nAdc16 = 0;
        nAdc32 = 0;
        nAUX = 0;
    end

    %% Private properties
    properties (Access = private)
        isopen = false;
        isStreaming = 0;
        isMatlab = true;
        hasAdc32 = false;
        nTotalChan = 0;
        scaleImu = [];
        scaleAdc = [];
        scale = [];
    end

    %% Public methods
    methods (Access = public)
        %-----------------------------------------------------------------------
        function obj = multidaq(varargin)

            for i = 1:2:nargin

                if strcmp(varargin{i}, 'interface'), obj.interface = varargin{i + 1};
                else error('Invalid argument');
                end

            end

            octaveVersion = exist ('OCTAVE_VERSION', 'builtin');

            if octaveVersion ~= 0
                %print('OCTAVE_VERSION = %d\n',octaveVersion);
                obj.isMatlab = false;
            end

            %biovision_multidaq('init', 'debug');
            biovision_multidaq('init');
            %fprintf('constructor multidaq finished\n');
        end

        %-----------------------------------------------------------------------
        function delete(obj)
            %obj.dev.delete();
            biovision_multidaq('deinit');
            %fprintf('deconstructor multidaq from delete finished\n');
        end

        %-----------------------------------------------------------------------
        function devicenames = listdevices(obj, devicenames)
            %fprintf('multidaq.listdevices()\n');
            devicenames = biovision_multidaq('listdevices');
        end

        %-----------------------------------------------------------------------
        function ret = open(obj, devicename)
            %fprintf('multidaq.open()\n');

            ret = biovision_multidaq('open', '1', char(devicename));
            %ffff

            if length(ret) == 0
                obj.isopen = true;
            end

            obj.idnAnswer = biovision_multidaq('cmd', '1', "*idn?");

            ret = biovision_multidaq('cmd', '1', "conf:sca:num?");
            %printf("conf:sca:num=%s\n", ret);

            if strncmp(ret, "0,", 2) == 1 % startswith "0,"
                obj.hasAdc32 = false;
            else
                obj.hasAdc32 = true;
            end

        end

        %-----------------------------------------------------------------------
        function ret = isOpen(obj)
            %fprintf('daq_imu.isOpen()\n');
            ret = obj.isopen;
        end

        %-----------------------------------------------------------------------
        function ret = setSampleRate(obj, rate)
            %fprintf('setSampleRate()\n');
            cmd = sprintf ('conf:sca:rat %d\n', rate);
            ret = biovision_multidaq('cmd', '1', cmd);
        end

        %-----------------------------------------------------------------------
        function ret = clearConfig(obj)
            obj.nTotalChan = 0;
            obj.nImu6 = 0;
            obj.nAdc16 = 0;
            obj.scaleAdc = [];
            obj.scaleImu = [];
            obj.scale = [];
            %fprintf('clearConfig()\n');
            ret = '';
        end

        %-----------------------------------------------------------------------
        function ret = addImu6(obj, rangeAcc, rangeGyro)
            %fprintf('addImu6()\n');
            cmd = sprintf ('conf:imu:para %d,%d,%d', obj.nImu6, rangeAcc, rangeGyro);
            ret = biovision_multidaq('cmd', '1', cmd);
            obj.nImu6 = obj.nImu6 + 1;
            obj.scaleImu = [obj.scaleImu rangeAcc rangeGyro];
        end

        %-----------------------------------------------------------------------
        function ret = addAdc16(obj, range)
            %fprintf('addAdc16()\n');
            ret = '';

            if range ~= 6
                ret = 'addAdc16() parameter Error: must be 6';
                return;
            end

            %TODO implement new command in device firmware
            %cmd = sprintf ('conf:sca:range %d,%d\n',obj.nAdc16,range);
            %ret = biovision_multidaq('cmd','1',cmd)
            obj.nAdc16 = obj.nAdc16 + 1;
            obj.scaleAdc = [obj.scaleAdc range];
        end

        %-----------------------------------------------------------------------
        function ret = addAdc32(obj, A0)
            ret = '';

            if A0 != 1
                ret = 'Amplification must be 1'
                return
            end

            obj.nAdc32 = obj.nAdc32 + 1;
        end

        %-----------------------------------------------------------------------
        function ret = configure(obj)
            %fprintf('configure()\n');
            cmd = sprintf ('conf:dev %d,%d,%d', obj.nAdc32, obj.nAdc16, obj.nImu6);
            ret = biovision_multidaq('cmd', '1', cmd);
            obj.scale = [];
            nch = 0;
            printf("conf:: %s\n", cmd)

            if length(ret)
                printf("error: cmd = %s answer = %s\n", cmd, ret);
                return;
            end

            if obj.hasAdc32

                for i = 1:obj.nAdc32
                    obj.scale = [obj.scale (2.4/32768/65536)];
                    nch = nch + 1;
                end

                obj.nTotalChan = nch;
                pause(.3);
                return;
            end

            for i = 1:obj.nAdc16
                sc = 1/32768 * obj.scaleAdc(i);
                obj.scale = [obj.scale sc];
                nch = nch + 1;
            end

            for i = 1:obj.nImu6
                acc = 1/32768 * obj.scaleImu(2 * (i - 1) + 1);
                gy = 1/32768 * obj.scaleImu(2 * (i - 1) + 2);
                obj.scale = [obj.scale acc acc acc gy gy gy];
                nch = nch + 6;
            end

            pause(.3);
            obj.nTotalChan = nch;
        end

        %-----------------------------------------------------------------------
        function ret = startSampling(obj)
            %fprintf('startSampling()\n');
            ret = biovision_multidaq('cmd', '1', 'init', 'stream');
        end

        %-----------------------------------------------------------------------
        function ret = stopSampling(obj)
            %fprintf('stopSampling()\n');
            ret = biovision_multidaq('cmd', '1', 'abort', 'stream');
        end

        %-----------------------------------------------------------------------
        function dret = getStreamData(obj)
            dret = biovision_multidaq('get', '1');
            % scale them properly
            if numel(dret) == 0
                return;
            end

            if obj.hasAdc32 == true

                for i = 1:obj.nTotalChan
                    dret(:, i + 1) = obj.scale(i) * dret(:, i + 1);
                end

            else

                for i = 1:obj.nTotalChan
                    dret(:, i) = obj.scale(i) * dret(:, i);
                end

            end

        end

        %-----------------------------------------------------------------------
        function close(obj)
            biovision_multidaq('close', '1');
            obj.isopen = false;
        end

    end

end
