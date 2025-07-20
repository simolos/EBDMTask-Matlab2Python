function [bRectCross, bDM, bDMcross, bTaskWait, bTaskWaitCross, bGetReadyForEP, bSuccess, bFailure, bRest, bAnticip, bEndOfTheTask, bPrepForER, bRedoEP, bEffortPerceptionEval, bPosition_fingers, bGoEP] = GetBuffers(gain_screen, Y_GOAL, Y_HOME, x, y, sz, darkgrey, bargrey, flag_Language)

    if flag_Language == 1 % French version

        Screen('Preference', 'TextEncodingLocale','UTF-8') % apparently not needed

       
        bBLACK = newbuffer;
        drawrect([0 0 0], bBLACK, [-500*gain_screen -500*gain_screen 800*gain_screen 800*gain_screen], 2000); 
%         debug_LuminanceComputation(bBLACK)
    
       
        bWHITE = newbuffer;
        drawrect([1 1 1], bWHITE, [-500*gain_screen -500*gain_screen 800*gain_screen 800*gain_screen], 2000); 
        drawrect([0 0 0], bWHITE, [-100*gain_screen -100*gain_screen 100*gain_screen 100*gain_screen], 10); 
%         debug_LuminanceComputation(bWHITE)
    
        ScreenRes = get(0, 'ScreenSize');
        startpsych(1, ScreenRes(3:end), [.8 .8 .8]); % full screen mode    

       
       % Design buffer with cross (intertrial)
        bRectCross = newbuffer;
        drawrect([0 0 0], bRectCross, [0 0], [100*gain_screen Y_GOAL-Y_HOME], 4);  %was 4
        drawrect([0 0 0], bRectCross, [-7 -62 7 62]); 
        drawrect([0 0 0], bRectCross, [-62 -7 62 7]);
        % Checking buffers luminance
%         debug_LuminanceComputation(bRectCross)
        % Sion 20240315 "Brightness: 203.38, Contrast: 11.23"
    
    
        % Design Decision making screen
        bDM = newbuffer;
        drawsquare([0 0 0], bDM, [-x 40], 20*gain_screen, 1);
        drawsquare([0 0 0], bDM, [x 40], 20*gain_screen, 1);
        Screen('TextFont', bDM, 'Arial');
        Screen('TextSize', bDM, 30);        
        Screen('TextColor', bDM, darkgrey);

        DrawFormattedText(bDM, sprintf('La recompense en vaut-elle l''effort ?', char(233)), 'center', (y+220), darkgrey*256)    
        drawrect([0 0 0], bDM, [0 0], [100*gain_screen Y_GOAL-Y_HOME], 4); 
        drawtext('Oui', bDM, [-x -y], 'Arial', sz, darkgrey);
        drawtext('Non', bDM, [x -y], 'Arial', sz, darkgrey);
        % Checking buffers luminance
%         debug_LuminanceComputation(bDM)
        % Sion 20240315 "Brightness: 203.26, Contrast: 11.6"
    
        
       
        % Design Decision making screen
        bDMcross = newbuffer;
        drawsquare([0 0 0], bDMcross, [-x 40], 20*gain_screen, 1);
        drawsquare([0 0 0], bDMcross, [x 40], 20*gain_screen, 1);
        Screen('TextFont', bDMcross, 'Arial');
        Screen('TextSize', bDMcross, 30);        
        Screen('TextColor', bDMcross, darkgrey);

        DrawFormattedText(bDMcross, sprintf('La recompense en vaut-elle l''effort ?', char(233)), 'center', (y+220), darkgrey*256)    
        drawrect([0 0 0], bDMcross, [0 0], [100*gain_screen Y_GOAL-Y_HOME], 4); 
        drawtext('Oui', bDMcross, [-x -y], 'Arial', sz, darkgrey);
        drawtext('Non', bDMcross, [x -y], 'Arial', sz, darkgrey);
        drawrect([0 0 0], bDMcross, [-7 -62 7 62]); 
        drawrect([0 0 0], bDMcross, [-62 -7 62 7]);
        % Checking buffers luminance
%         debug_LuminanceComputation(bDMcross)
        % Sion 20240315 "Brightness: 203.08, Contrast: 13.08"
    
        
      
        % Design Preparation and Task Screens
        bTaskWait = newbuffer;
        drawrect([0 0 0], bTaskWait, [0 0], [100*gain_screen Y_GOAL-Y_HOME], 4); 
        % Checking buffers luminance
%         debug_LuminanceComputation(bTaskWait)
        % Sion 20240315 "Brightness: 203.56, Contrast: 9.46"
    
        
      
        % Design Preparation and Task Screens
        bTaskWaitCross = newbuffer;
        drawrect([0 0 0], bTaskWaitCross, [0 0], [100*gain_screen Y_GOAL-Y_HOME], 4); 
        % Adding cross
        drawrect([0 0 0], bTaskWaitCross, [-7 -62 7 62]); 
        drawrect([0 0 0], bTaskWaitCross, [-62 -7 62 7]);
        % Checking buffers luminance
%         debug_LuminanceComputation(bTaskWaitCross)
        % Sion 20240315 "Brightness: 203.38, Contrast: 11.23"
    
    
       
        % Design Position your fingers screen
        bPosition_fingers = newbuffer;
        % Adding cross
        drawrect([0 0 0], bPosition_fingers, [-7 -62 7 62]); 
        drawrect([0 0 0], bPosition_fingers, [-62 -7 62 7]);
        drawtext('Presser', bPosition_fingers, [0 (y+380)], 'Arial', sz, darkgrey);
        drawtext('A-W-E', bPosition_fingers, [0 (y+280)], 'Arial', sz, darkgrey);
        drawrect([0 0 0], bPosition_fingers, [0 0], [100*gain_screen Y_GOAL-Y_HOME], 4); 
%         debug_LuminanceComputation(bTaskWaitCross)
        % Sion 20240315 "Brightness: 203.28, Contrast: 11.87"
    
        
        
        % Design Preparation to EP
        bGetReadyForEP = newbuffer;
        % Adding cross
        drawrect([0 0 0], bGetReadyForEP, [-7 -62 7 62]); 
        drawrect([0 0 0], bGetReadyForEP, [-62 -7 62 7]);
        Screen('TextFont', bGetReadyForEP, 'Arial');
        Screen('TextSize', bGetReadyForEP, 27);        
        Screen('TextColor', bGetReadyForEP, darkgrey);
%         Screen('Preference', 'TextEncodingLocale','UTF-8') % apparently not needed
        DrawFormattedText(bGetReadyForEP, sprintf('Preparez-\nvous', char(233)), 'center', (y+280*2), darkgrey*256)
        drawrect([0 0 0], bGetReadyForEP, [0 0], [100*gain_screen Y_GOAL-Y_HOME], 4); 
        % Checking buffers luminance
%         debug_LuminanceComputation(bGetReadyForEP)
        % Sion 20240315 "Brightness: 203.3, Contrast: 11.71"
    
    
      
        % Design Reward Screens for Success 
        bSuccess = newbuffer;
        % Adding cross
        drawrect([0 0 0], bSuccess, [-7 -62 7 62]); 
        drawrect([0 0 0], bSuccess, [-62 -7 62 7]);
        Screen('TextFont', bSuccess, 'Arial');
        Screen('TextSize', bSuccess, 27);        
        Screen('TextColor', bSuccess, darkgrey);
        DrawFormattedText(bSuccess, sprintf('Succes !', char(232)), 'center', (y+280*2), darkgrey*256)    
        drawrect([0 0 0], bSuccess, [0 0], [100*gain_screen Y_GOAL-Y_HOME], 4); 
       % Checking buffers luminance
%         debug_LuminanceComputation(bSuccess)
        % Sion 20240315 "Brightness: 203.34, Contrast: 11.5"
    
    
        
       % Design Reward Screens for Failure
        bFailure = newbuffer;     
       % Adding cross
        drawrect([0 0 0], bFailure, [-7 -62 7 62]); 
        drawrect([0 0 0], bFailure, [-62 -7 62 7]);
        Screen('TextFont', bFailure, 'Arial');
        Screen('TextSize', bFailure, 27);        
        Screen('TextColor', bFailure, darkgrey);
        DrawFormattedText(bFailure, sprintf('Rate !', char(233)), 'center', (y+280*2), darkgrey*256)    
        drawrect([0 0 0], bFailure, [0 0], [100*gain_screen Y_GOAL-Y_HOME], 4); 
       % Checking buffers luminance
%         debug_LuminanceComputation(bFailure)
        % Sion 20240315 "Brightness: 203.35, Contrast: 11.44"
    
      
        % Design Reward Screens for Failure
        bRest = newbuffer;     
        % Adding cross
        drawrect([0 0 0], bRest, [-7 -62 7 62]); 
        drawrect([0 0 0], bRest, [-62 -7 62 7]);
        drawtext('Repos', bRest, [0 (y+280)], 'Arial', sz, darkgrey);
        drawrect([0 0 0], bRest, [0 0], [100*gain_screen Y_GOAL-Y_HOME], 4); 
        % Checking buffers luminance
%         debug_LuminanceComputation(bRest)
        % Sion 20240315 "Brightness: 203.33, Contrast: 11.55"
        
        
           
        % Design anticipation buffer
        bAnticip = newbuffer;
        drawrect([0 0 0], bAnticip, [-7 -62 7 62]); 
        drawrect([0 0 0], bAnticip, [-62 -7 62 7]);
        Screen('TextFont', bAnticip, 'Arial');
        Screen('TextSize', bAnticip, 27);        
        Screen('TextColor', bAnticip, darkgrey);
        DrawFormattedText(bAnticip, sprintf('Anticipe !', char(233)), 'center', (y+280*2), darkgrey*256)    
        drawrect([0 0 0], bAnticip, [0 0], [100*gain_screen Y_GOAL-Y_HOME], 4); 
        % Checking buffers luminance
%         debug_LuminanceComputation(bAnticip)
        % Sion 20240315 "Brightness: 203.33, Contrast: 11.53"
    
        
          
        bEndOfTheTask = newbuffer;
        drawtext('Fin de la tache', bEndOfTheTask, [0 230*gain_screen], 'Arial', sz, darkgrey);
        % Checking buffers luminance
%         debug_LuminanceComputation(bAnticip)
        % Sion 20240315 "Brightness: 203.9, Contrast: 3.74"
    
       
          
        bPrepForER = newbuffer;
        drawtext('Veuillez noter la perception de votre effort...', bPrepForER, [0 (y-10)], 'Arial', sz, darkgrey);
        % Checking buffers luminance
%         debug_LuminanceComputation(bPrepForER)
        % Sion 20240315 "Brightness: 203.72, Contrast: 6.38"
    
        
      
        
        bRedoEP = newbuffer;
        Screen('TextFont', bRedoEP, 'Arial');
        Screen('TextSize', bRedoEP, 30);        
        Screen('TextColor', bRedoEP, darkgrey);
        DrawFormattedText(bRedoEP, sprintf('Rate! Veuillez essayer à nouveau', char(233)), 'center', (y+282*3), darkgrey*256)   
        % Checking buffers luminance
%         debug_LuminanceComputation(bRedoEP)
        % Sion 20240315 "Brightness: 203.78, Contrast: 5.72"

       
  
%         
        % Design buffer to rate the effort-perception
        bEffortPerceptionEval = newbuffer;
        width_VASbar = 600*gain_screen;
        Screen('TextFont', bEffortPerceptionEval, 'Arial');
        Screen('TextSize', bEffortPerceptionEval, 30);        
        Screen('TextColor', bEffortPerceptionEval, darkgrey);
        DrawFormattedText(bEffortPerceptionEval, sprintf('Effort percu', char(231)), 'center', (y+220), darkgrey*256)          
        drawrect([0 0 0], bEffortPerceptionEval, [0 0], [width_VASbar 10*gain_screen], 4); 
        drawsquare([0 0 0], bEffortPerceptionEval, [0 0], 10*gain_screen); % Middle-scale sign
        DrawFormattedText(bEffortPerceptionEval, sprintf('0'), width_VASbar/2, (y+750), darkgrey*256)          
        DrawFormattedText(bEffortPerceptionEval, sprintf('Pas d''effort'), width_VASbar/2, (y+715), darkgrey*256)          
        DrawFormattedText(bEffortPerceptionEval, sprintf('Effort maximum'), 3/2*width_VASbar, (y+715), darkgrey*256)          
        DrawFormattedText(bEffortPerceptionEval, sprintf('10'), 3/2*width_VASbar, (y+750), darkgrey*256)          
%         drawtext('0\nPas d''effort', bEffortPerceptionEval, [-x -y], 'Arial',sz, darkgrey);
%         drawtext('Effort maximum (10)', bEffortPerceptionEval, [x -y], 'Arial',sz, darkgrey);
        % Checking buffers luminance
%         debug_LuminanceComputation(bEffortPerceptionEval)
        % Sion 20240315 "Brightness: 203.15, Contrast: 12.49"
    
        
        
     
        % Design EP Go!!!
        bGoEP = newbuffer;
        % Adding cross
        drawrect([0 0 0], bGoEP, [-7 -62 7 62]); 
        drawrect([0 0 0], bGoEP, [-62 -7 62 7]);
        drawtext('Go!!!', bGoEP, [0 (y+280)], 'Arial', sz, darkgrey);
        drawrect([0 0 0], bGoEP, [0 0], [100*gain_screen Y_GOAL-Y_HOME], 4); 
        % Checking buffers luminance
%         debug_LuminanceComputation(bGoEP)
        % Sion 20240315 "Brightness: 203.35, Contrast: 11.45"

    else % English version

        bBLACK = newbuffer;
        drawrect([0 0 0], bBLACK, [-500*gain_screen -500*gain_screen 800*gain_screen 800*gain_screen], 2000); 
    %     debug_LuminanceComputation(bBLACK)
    
    
        bWHITE = newbuffer;
        drawrect([1 1 1], bWHITE, [-500*gain_screen -500*gain_screen 800*gain_screen 800*gain_screen], 2000); 
        drawrect([0 0 0], bWHITE, [-100*gain_screen -100*gain_screen 100*gain_screen 100*gain_screen], 10); 
    %     debug_LuminanceComputation(bWHITE)
    
    
       % Design buffer with cross (intertrial)
        bRectCross = newbuffer;
        drawrect([0 0 0], bRectCross, [0 0], [100*gain_screen Y_GOAL-Y_HOME], 4);  %was 4
        drawrect([0 0 0], bRectCross, [-7 -62 7 62]); 
        drawrect([0 0 0], bRectCross, [-62 -7 62 7]);
        % Checking buffers luminance
    %     debug_LuminanceComputation(bRectCross)
    
        
        
        % Design Decision making screen
        bDM = newbuffer;
        drawsquare([0 0 0], bDM, [-x 40], 20*gain_screen, 1);
        drawsquare([0 0 0], bDM, [x 40], 20*gain_screen, 1);
        drawtext('Is the reward worth the effort?', bDM, [0 230*gain_screen], 'Arial', sz, darkgrey);
        drawrect([0 0 0], bDM, [0 0], [100*gain_screen Y_GOAL-Y_HOME], 4); 
        drawtext('Yes', bDM, [-x -y], 'Arial', sz, darkgrey);
        drawtext('No', bDM, [x -y], 'Arial', sz, darkgrey);
        % Checking buffers luminance
%         debug_LuminanceComputation(bDM)
        % Sion 20240315 "Brightness: 203.3, Contrast: 11.33"
    
    
        
        % Design Decision making screen
        bDMcross = newbuffer;
        drawsquare([0 0 0], bDMcross, [-x 40], 20*gain_screen, 1);
        drawsquare([0 0 0], bDMcross, [x 40], 20*gain_screen, 1);
        drawtext('Is the reward worth the effort?', bDMcross, [0 230*gain_screen], 'Arial', sz, darkgrey);
        drawrect([0 0 0], bDMcross, [0 0], [100*gain_screen Y_GOAL-Y_HOME], 4); 
        drawtext('Yes', bDMcross, [-x -y], 'Arial', sz, darkgrey);
        drawtext('No', bDMcross, [x -y], 'Arial', sz, darkgrey);
        drawrect([0 0 0], bDMcross, [-7 -62 7 62]); 
        drawrect([0 0 0], bDMcross, [-62 -7 62 7]);
        % Checking buffers luminance
%         debug_LuminanceComputation(bDMcross)
        % Sion 20240315 "Brightness: 203.12, Contrast: 12.85"
        
      
    
        % Design Preparation and Task Screens
        bTaskWait = newbuffer;
        drawrect([0 0 0], bTaskWait, [0 0], [100*gain_screen Y_GOAL-Y_HOME], 4); 
        % Checking buffers luminance
%         debug_LuminanceComputation(bTaskWait)
        % Sion 20240315 "Brightness: 203.56, Contrast: 9.46"
    
        
        
      
        % Design Preparation and Task Screens
        bTaskWaitCross = newbuffer;
        drawrect([0 0 0], bTaskWaitCross, [0 0], [100*gain_screen Y_GOAL-Y_HOME], 4); 
        % Adding cross
        drawrect([0 0 0], bTaskWaitCross, [-7 -62 7 62]); 
        drawrect([0 0 0], bTaskWaitCross, [-62 -7 62 7]);
        % Checking buffers luminance
%         debug_LuminanceComputation(bTaskWaitCross)
        % Sion 20240315 "Brightness: 203.38, Contrast: 11.23"
    
    
        
     
        % Design Position your fingers screen
        bPosition_fingers = newbuffer;
        % Adding cross
        drawrect([0 0 0], bPosition_fingers, [-7 -62 7 62]); 
        drawrect([0 0 0], bPosition_fingers, [-62 -7 62 7]);
        drawtext('Hold', bPosition_fingers, [0 (y+380)], 'Arial', sz, darkgrey);
        drawtext('A-W-E', bPosition_fingers, [0 (y+280)], 'Arial', sz, darkgrey);
        drawrect([0 0 0], bPosition_fingers, [0 0], [100*gain_screen Y_GOAL-Y_HOME], 4); 
        % Checking buffers luminance
%         debug_LuminanceComputation(bPosition_fingers)
        % Sion 20240315 "Brightness: 203.3, Contrast: 11.76"
    
    
        
        % Design Preparation to EP
        bGetReadyForEP = newbuffer;
        % Adding cross
        drawrect([0 0 0], bGetReadyForEP, [-7 -62 7 62]); 
        drawrect([0 0 0], bGetReadyForEP, [-62 -7 62 7]);
        drawtext('Get ready', bGetReadyForEP, [0 (y+280)], 'Arial', sz, darkgrey);
        drawrect([0 0 0], bGetReadyForEP, [0 0], [100*gain_screen Y_GOAL-Y_HOME], 4); 
        % Checking buffers luminance
%         debug_LuminanceComputation(bGetReadyForEP)
        % Sion 20240315 "Brightness: 203.31, Contrast: 11.68"
    
    
            
          
        % Design Reward Screens for Success 
        bSuccess = newbuffer;
       % Adding cross
        drawrect([0 0 0], bSuccess, [-7 -62 7 62]); 
        drawrect([0 0 0], bSuccess, [-62 -7 62 7]);
    %     drawtext('Success!', bSuccess, [0 (y+280)], 'Arial', sz, darkgrey);
        drawtext('Success!', bSuccess, [-250 y+280], 'Arial',sz+10,darkgrey); 
    
        drawrect([0 0 0], bSuccess, [0 0], [100*gain_screen Y_GOAL-Y_HOME], 4); 
        % Checking buffers luminance
%         debug_LuminanceComputation(bSuccess)
        % Sion 20240315 "Brightness: 203.27, Contrast: 11.92"
    
  
    
        % Design Reward Screens for Failure
        bFailure = newbuffer;     
        % Adding cross
        drawrect([0 0 0], bFailure, [-7 -62 7 62]); 
        drawrect([0 0 0], bFailure, [-62 -7 62 7]);
        drawtext('Failed!', bFailure, [-250 (y+280)], 'Arial', sz+10, darkgrey);
        drawrect([0 0 0], bFailure, [0 0], [100*gain_screen Y_GOAL-Y_HOME], 4); 
        % Checking buffers luminance
%         debug_LuminanceComputation(bFailure)
        % Sion 20240315 "Brightness: 203.29, Contrast: 11.78"
        
        
              
   
    
        % Design Reward Screens for Failure
        bRest = newbuffer;     
        % Adding cross
        drawrect([0 0 0], bRest, [-7 -62 7 62]); 
        drawrect([0 0 0], bRest, [-62 -7 62 7]);
        drawtext('Rest', bRest, [0 (y+280)], 'Arial', sz, darkgrey);
        drawrect([0 0 0], bRest, [0 0], [100*gain_screen Y_GOAL-Y_HOME], 4); 
        % Checking buffers luminance
%         debug_LuminanceComputation(bRest)
        % Sion 20240315 "Brightness: 203.34, Contrast: 11.47"
        
        
              
        % Design anticipation buffer
        bAnticip = newbuffer;
        drawrect([0 0 0], bAnticip, [-7 -62 7 62]); 
        drawrect([0 0 0], bAnticip, [-62 -7 62 7]);
        drawtext(['Anticipated'], bAnticip, [0 (y+280)], 'Arial', sz-2, darkgrey);
        drawrect([0 0 0], bAnticip, [0 0], [100*gain_screen Y_GOAL-Y_HOME], 4); 
        % Checking buffers luminance
%         debug_LuminanceComputation(bAnticip)
        % Sion 20240315 "Brightness: 203.31, Contrast: 11.66"
        
   
    
        bEndOfTheTask = newbuffer;
        drawtext('End of the task', bEndOfTheTask, [0 230*gain_screen], 'Arial', sz, darkgrey);
        % Checking buffers luminance
%         debug_LuminanceComputation(bAnticip)
        % Sion 20240315 "Brightness: 203.9, Contrast: 3.9"
    
        
     
        bPrepForER = newbuffer;
        drawtext('Please rate your effort perception...', bPrepForER, [0 (y-10)], 'Arial', sz, darkgrey);
        % Checking buffers luminance
%         debug_LuminanceComputation(bAnticip)
        % Sion 20240315 "Brightness: 203.77, Contrast: 5.76"
        
     
     
        bRedoEP = newbuffer;
        drawtext('Failure! Please repeat the trial', bRedoEP, [0 (y-10)], 'Arial', sz, darkgrey);
        % Checking buffers luminance
%         debug_LuminanceComputation(bRedoEP)
        % Sion 20240315 "Brightness: 203.8, Contrast: 5.48"
        
%           ScreenRes = get(0, 'ScreenSize');
%         startpsych(1, ScreenRes(3:end), [.8 .8 .8]); % full screen mode    
% %  
        
        
        % Design buffer to rate the effort-perception
        bEffortPerceptionEval = newbuffer;
        width_VASbar=600*gain_screen;
        Screen('TextFont', bEffortPerceptionEval, 'Arial');
        Screen('TextSize', bEffortPerceptionEval, 30);        
        Screen('TextColor', bEffortPerceptionEval, darkgrey);      
        drawtext('Effort perceived', bEffortPerceptionEval, [0 230*gain_screen], 'Arial', sz, darkgrey);
        drawrect([0 0 0], bEffortPerceptionEval, [0 0], [width_VASbar 10*gain_screen], 4); 
        drawsquare([0 0 0], bEffortPerceptionEval, [0 0], 10*gain_screen); % Middle-scale sign
        DrawFormattedText(bEffortPerceptionEval, sprintf('0'), width_VASbar/2, (y+750), darkgrey*256)          
        DrawFormattedText(bEffortPerceptionEval, sprintf('No effort at all'), width_VASbar/2, (y+715), darkgrey*256)          
        DrawFormattedText(bEffortPerceptionEval, sprintf('Maximum effort'), 3/2*width_VASbar, (y+715), darkgrey*256)          
        DrawFormattedText(bEffortPerceptionEval, sprintf('10'), 3/2*width_VASbar, (y+750), darkgrey*256)          
%      % Checking buffers luminance
%         debug_LuminanceComputation(bEffortPerceptionEval)
        % Sion 20240315 "Brightness: 203.1, Contrast: 12.76"
        
%         ScreenRes = get(0, 'ScreenSize');
%         startpsych(1, ScreenRes(3:end), [.8 .8 .8]); % full screen mode    

    
        % Design EP Go!!!
        bGoEP = newbuffer;
        % Adding cross
        drawrect([0 0 0], bGoEP, [-7 -62 7 62]); 
        drawrect([0 0 0], bGoEP, [-62 -7 62 7]);
        drawtext('Go!!!', bGoEP, [0 (y+280)], 'Arial', sz, darkgrey);
        drawrect([0 0 0], bGoEP, [0 0], [100*gain_screen Y_GOAL-Y_HOME], 4); 
        % Checking buffers luminance
%         debug_LuminanceComputation(bGoEP)
        % Sion 20240315 "Brightness: 203.35, Contrast: 11.45"
        
    end

    

end
