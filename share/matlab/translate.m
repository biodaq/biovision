function translate()

    if exist ('OCTAVE_VERSION', 'builtin') > 0

        if ispc()
            fprintf('Windows/Octave found\n')
            mex '-D USE_OCTAVE' 'biovision_multidaq.c' '-Llib' '-lbiovisionMultiDaq' '-Wl,--no-insert-timestamp'
            exit(B)
        else
            fprintf('linux/Octave found\n')
            mex '-D USE_OCTAVE' 'biovision_multidaq.c' '-L/usr/local/lib' '-lbiovisionMultiDaq'
            exit (B)
        end

    else

        if ispc()
            fprintf('windows/matlab found\n')
            mex '-R2018a' 'biovision_multidaq.c' '-Llib' '-lbiovisionMultiDaq' '-Wl,--no-insert-timestamp'
        else
            mex '-R2018a' 'biovision_multidaq.c' '-I/usr/local/' '-L/usr/local/lib' '-lbiovisionMultiDaq'
        end

    end

end
