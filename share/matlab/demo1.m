function demo1
    fprintf('-------------------------------- demo1.m -------------------\n');
    a = multidaq; % create object
    A = a.listdevices();

    %----------- open the first detected device
    ret = a.open(A{1});

    %--------------------------------------- configure the device
    % ret is a char array and indicates an error, if not empty
    % error handling is up to you
    % non feasible parameter will force errors
    ret = a.clearConfig();
    ret = a.setSampleRate(1000);
    ret = a.addAdc16(6); % one line per channel
    ret = a.addAdc16(6);
    ret = a.addImu6(6, 250); % uncomment to add the first Imu

    if length(ret)
        fprintf('an error occurred\n');
        return;
    end

    ret = a.configure(); % this must be the last command in config

    %----------------------------- measurement loop
    fprintf('start\n');
    ret = a.startSampling();
    result = a.getStreamData();

    for i = 1:10
        pause(.1); % not neccessary, but you will mostly get zero length
        tmp = a.getStreamData();
        result = vertcat(result, tmp);
        % you may process the new data here
        % they are in tmp !
        [rows, cols] = size(tmp);
        fprintf('got data: Array size = %d rows x %d cols\n', rows, cols);
    end

    fprintf('stop\n');
    ret = a.stopSampling();
    pause(.1);

    %-------------------------------- tear down and plot some results
    a.close();

    % data are arranged in columns
    % first nAdc colummns are the data of the adcs
    % then next 3 cols are acc data of imu1
    % then next 3 cols are Gyro data of imu1
    % next 3 cols are acc data of imu2 and so on
    if a.nImu6 == 0
        plot(result);
        title('adc Measurement')
        ylabel ('[V]');
    else
        subplot(3, 1, 1);
        plot(result(:, 1:a.nAdc16));
        title('adc Measurement')
        ylabel('[V]');
        subplot(3, 1, 2);
        plot(result(:, a.nAdc16:a.nAdc16 + 3));
        title('Acc first IMU');
        ylabel('[g]');
        subplot(3, 1, 3);
        plot(result(:, a.nAdc16 + 3:a.nAdc16 + 6));
        title('Gyro first IMU');
        ylabel('[°/s]');
    end

    fprintf('normal end of demo1.m');
    return;
end
