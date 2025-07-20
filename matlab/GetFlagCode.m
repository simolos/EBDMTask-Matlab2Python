function [flag_Eyetracker, flag_MultipleKeyPressed, flag_Population, flag_Language] = GetFlagCode(flag_Eyetracker, flag_MultipleKeyPressed, flag_Population, flag_Language)

    if strcmp(flag_Eyetracker, 'EyeLink_on')
        flag_Eyetracker = 1; % eyetracking on
    elseif strcmp(flag_Eyetracker, 'EyeLink_off')
        flag_Eyetracker = 0; % debugging mode, no eyetracking
    else
        error('Check Eyelink flag')
    end
    
    if strcmp(flag_MultipleKeyPressed, 'MultipleKeyPressed_on')
        flag_MultipleKeyPressed = 1; % eyetracking on
    elseif strcmp(flag_MultipleKeyPressed, 'MultipleKeyPressed_off')
        flag_MultipleKeyPressed = 0; % debugging mode, no eyetracking
    else 
        error('Check MultipleKeyPressed flag')
    end
    
    if strcmp(flag_Population, 'HY')
        flag_Population = 1; % Healthy young
    elseif strcmp(flag_Population, 'HO')
        flag_Population = 2; % Healthy old
    elseif strcmp(flag_Population, 'DBS')
        flag_Population = 3; % Implanted patients
    else 
        error('Check Population flag')
    end

    if strcmp(flag_Language, 'F')
        flag_Language = 1; % Healthy young
    elseif strcmp(flag_Language, 'E')
        flag_Language = 2; % Healthy old
    else 
        error('Check Language flag')
    end


end