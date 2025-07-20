function InitScreen(full_screen_Flag)

    % Change here the size of the screen!

    if full_screen_Flag == 1 
        ScreenRes = get(0, 'ScreenSize');
        startpsych(1, ScreenRes(3:end), [.8 .8 .8]); % full screen mode 
%         startpsych(0, ScreenRes(3:end), [.8 .8 .8]); % forced 0 bcs of random error

    else 
            startpsych(0, [800 600], [.8 .8 .8]); % debugging mode (small window)
    end

end