% You may call this convenience routine without the init command
A = biovision_multidaq('listdevices')
tmp = size(A);

if tmp(1) < 1
    fprintf('No Device found\n');
    return;
end

[ans, err] = biovision_multidaq('init');

for i = 1:tmp(1)

    if strfind(A{i}, 'bio')
        fprintf('found bioDaq device\n');
        [ans, err] = biovision_multidaq('open', '1', A{i});
        [ans, err] = biovision_multidaq('cmd', '1', '*idn?');
        fprintf('device answered to *idn?: %s\n', ans);
        [ans, err] = biovision_multidaq('close', '1');
    end

    if strfind(A{i}, 'multi')
        fprintf('found multiDaq device\n');
        [ans, err] = biovision_multidaq('open', '2', A{i});
        [ans, err] = biovision_multidaq('cmd', '2', '*idn?');
        fprintf('device answered to *idn?: %s\n', ans);
        [ans, err] = biovision_multidaq('close', '2');
    end

end

[ans, err] = biovision_multidaq('deinit');
