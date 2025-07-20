function send_trigger()

    ioObj = io64;
    status = io64(ioObj);

    % address = hex2dec('D050');
    address = hex2dec('3BC');

    data_out = 1;

    io64(ioObj, address,data_out);
    disp(data_out)
    pause(0.05)
    data_zero = 0;
    io64(ioObj, address,data_zero);
    clear io64
    
end


