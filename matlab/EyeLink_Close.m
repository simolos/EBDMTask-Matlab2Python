function EyeLink_Close()

    % stop eye-tracker
    WaitSecs(0.1); % Add 100 msec of data to catch final events before stopping
    Eyelink('StopRecording');
    Eyelink('SetOfflineMode');
    Eyelink('CloseFile');
    status = Eyelink('ReceiveFile');
    ListenChar(0); % restore keyboard output to Matlab

end
