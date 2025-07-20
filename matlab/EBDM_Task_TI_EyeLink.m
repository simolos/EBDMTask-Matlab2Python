function EBDM_Task_TI_EyeLink(SubjectNum, block_name, nTrials, n_Effort_Trials, GV, flag_Eyetracker, flag_MultipleKeyPressed, flag_Population, flag_Language, flag_Stimulation)
    try
    % Code to run Effort - Reward decision making Task 
    %
    % ERTask(subjectnb, block, nTrials, GV)
    % Example:
    % ERTask(1, 2,32,0.6)
    % ------
    % Inputs:
    % 1) subjectnb: ID of subject (should be a number)
    % 2) block: number of block
    % 3) nTrials: number of trials in block; should be a multiple of 16 (4x4 design)
    % 4) GV is the max tapping frequency in Hz
    % ------
    % Pierre Vassiliadis, April 2023
    % Contact: pierre.vassiliadis@epfl.ch
    % BEFORE RUNNING THIS CODE, MAKE SURE YOU ARE IN THE FOLDER CONTAINING THE
    % 'TOOLBOXES' FOLDER
    
    
    % clear all; %for script mode
    
    ERTask_VERSION = '1.1'; % Adapted to Apathy-pj and pupillometry - ONGOING - Simona Losacco -S-
    
    %% Flag identification
    
    [flag_Eyetracker, flag_MultipleKeyPressed, flag_Population, flag_Language] = GetFlagCode(flag_Eyetracker, flag_MultipleKeyPressed, flag_Population, flag_Language);
 
    %% Eyelink initialization
    if flag_Eyetracker == 1
        Eyelink_Start(block_name)
    end
    
    %% Screen parameters definition
    
    ConstantLuminance = 0.5;
    
    % Set parameters for the block
    test_dev = 0;

    if test_dev == 1 % Debugging code   
        full_screen_Flag = 0; % 1 for full screen, otherwise 0
    else
        full_screen_Flag = 1; 
    end 
    
    % Parameters of task
    KEYBOARD_MODE = 1; 
    
    % Adjust to screen in vertical axis - for big screen 
    if full_screen_Flag == 1 
        gain_screen = 2;  % 1 for full screen window
    else 
        gain_screen = 1;  % 1 for small window
    end
    
    % Init CosyGraphics:
    InitScreen(full_screen_Flag)
    
    OneFrame = oneframe; % save it for the analysis program
    close all
    
    % Check screen frequency 
    Hz = getscreenfreq;
    % if round(Hz) ~= 100
    %     stopcosy;
    %     error(['Screen frequency is ' num2str(Hz) ' Hz!!! Aborted CosyGraphixcs!']) %error message if screen frequency is not 100Hz
    % end
      
        
    %% Conditions during block 

    [Cond_E_R, indx_Effort_Trials] = GetTrialCondition(nTrials, n_Effort_Trials, flag_Population);
    
    %% Durations of the different events in a trial in ms
    
    dur = GetTaskDuration(flag_Eyetracker, flag_Population);

    %% Trial Structure Initialization
    % trials = table for overview of data during experiment;
    empty = NaN + zeros(nTrials,1);
    trials.trial = (1:nTrials)';
    trials.effort= Cond_E_R(:,1);
    trials.efftested = Cond_E_R(:,1);
    trials.rewtested = Cond_E_R(:,2);
    trials.reward = Cond_E_R(:,2);
    trials.DecisionTime = NaN(nTrials,1); 
    trials.ReactionTimeEP = NaN(nTrials,1); 
    trials.Acceptance = NaN(nTrials,1); 
    trials.EffortProduction = NaN(nTrials,1);
    trials.durPrep_DM = round(round2frame(dur.DM_Preparation(1) + rand(nTrials,1) * diff(dur.DM_Preparation))); % min and max in dur.DM_Preparation
    trials.durPrep_EP = round(round2frame(dur.EP_Preparation(1) + rand(nTrials,1) * diff(dur.EP_Preparation))); % min and max in dur.EP_Preparation
    trials.success = empty;
    trials.Anticipation_EP = NaN(nTrials,1);
    trials.Anticipation_DM = zeros(nTrials,1);
    trials.KeyPositionTime = NaN(nTrials,1); % Time needed to have the hand in position for the first time (excluding 1s of keeping the pose)
    
    
    %% CURSOR Matrix initialization
    % Record the Cursor Position during the motor task--> Used for offline analyses
    nFrames = floor(dur.Task/oneframe); % number of frames during the task
    CURSOR = NaN((dur.Task./1000)*round(Hz),nTrials); % normalized force level; rows: samples in a trial; column: trials
   

    %% Create Offscreen Buffers 
    
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % Elements on screen
    % Position of highest point of the bar (in pixels)
    Y_GOAL = 200*gain_screen; %vertical coordinates for the target (max displacement)
    
    % Position of lowest point of the bar (in pixels)
    Y_HOME = -200*gain_screen; %vertical coordinates for the home position
    % Colors
    LIGHT_GREY = [0.9 0.9 0.9]; % red
    DARK_GREY = [0.6510    0.6510    0.6510];
    BLACK = [0 0 0];
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    x = 300*gain_screen;
    y = -80*gain_screen;
    sz = 15*gain_screen;% size of letters
    darkgrey = .2*[1 1 1]; 
    bargrey = .25*[1 1 1]; % color of the effort level bar

    [bRectCross, bDM, bDMcross, bTaskWait, bTaskWaitCross, bGetReadyForEP, bSuccess, bFailure, bRest, bAnticip, bEndOfTheTask, bPrepForER, bRedoEP, bEffortPerceptionEval, bPosition_fingers] = ...
        GetBuffers(gain_screen, Y_GOAL, Y_HOME, x, y, sz, darkgrey, bargrey, flag_Language);
    
%     %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%     % The next buffers are designed just to check their luminance (Gradually
%     % composed along the code)
% 
%     % Decision making with info + box ticked
%     bDM = newbuffer;
%     drawsquare([0 0 0], bDM, [-x 40], 20*gain_screen, 1);
%     drawsquare([0 0 0], bDM, [x 40], 20*gain_screen, 1);
%     drawtext('Is the reward worth the effort?', bDM, [0 230*gain_screen], 'Arial', sz, darkgrey);
%     drawrect([0 0 0], bDM, [0 0], [100*gain_screen Y_GOAL-Y_HOME], 4); 
%     drawtext('Yes', bDM, [-x -y], 'Arial', sz, darkgrey);
%     drawtext('No', bDM, [x -y], 'Arial', sz, darkgrey);
%     % Adding cross
%     drawrect([0 0 0], bDM, [-7 -62 7 62]); 
%     drawrect([0 0 0], bDM, [-62 -7 62 7]);
%     debug_LuminanceComputation(bDM)
% 
%     % Adding target level of effort 
%     drawrect(bargrey, bDM, [0 200], [110*gain_screen 8*gain_screen], 0);
%     drawtext(['For ' num2str(10) ' cents'], bDM, [150*gain_screen 200], 'Arial', sz, darkgrey);
%     debug_LuminanceComputation(bDM)
%     % Y/N selection
%     drawround(bargrey, bDM, [x 40], 12*gain_screen); % Box ticked only when the arrow is pressed -S-
%     debug_LuminanceComputation(bDM)
%    
%     
%            
%     % Go buffer
%     bTask = newbuffer;
%     drawrect([0 0 0], bTask, [0 0], [100*gain_screen Y_GOAL-Y_HOME], 4); 
%     rew_t = 0.8;
%     ypix_target = 200 * rew_t;
%     drawtext('Go !!!', bTask, [-250 ypix_target], 'Arial',sz+15,darkgrey); 
%     drawtext(['For ' num2str(rew_t) ' cents'], bTask, [340 ypix_target], 'Arial',sz+15,darkgrey);   
%     drawrect(bargrey, bTask, [0 ypix_target], [110*gain_screen 8*gain_screen], 0);   
%     % Adding moving bar
%     rew_t = 0.8;
%     ypix_target = 200 * rew_t;
%     ypix = 200 * 0.5;
%     drawrect(DARK_GREY, bTask, [0 ((ypix+Y_HOME)./2)], [110*gain_screen 8*gain_screen], 0);   
%     % Checking buffers luminance
%     debug_LuminanceComputation(bTask)
% 
% 
%     % Design Reward Screens for Success and Failure
%     bSuccess = newbuffer;
%     drawrect([0 0 0], bSuccess, [-7 -62 7 62]); 
%     drawrect([0 0 0], bSuccess, [-62 -7 62 7]);
%     drawrect([0 0 0], bSuccess, [0 0], [100*gain_screen Y_GOAL-Y_HOME], 4); 
%     drawtext('Success!', bSuccess, [-250 ypix_target], 'Arial',sz+10,darkgrey); 
%     drawtext(['+ ' num2str(20) ' cents'], bSuccess, [270 ypix_target], 'Arial',sz+10,darkgrey);   
%      % Checking buffers luminance
%     debug_LuminanceComputation(bSuccess)
% 
%     %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    
    %% Exp Loop
    keypr = NaN(nFrames, nTrials);
    keypr_ALL = cell(nFrames, nTrials);
    TaskTimings = cell(1000,2);
    timeIdx = 1;
    
    %%%%%%%%% Stim
    
%     time_start_baseline1 = GetSecs() - TimeTaskStart;
  
%    WaitSecs(TaskParameters.BaselineTime*2)  % Because theta bursts start at 10 seconds
    
%     time_finish_baseline1  = GetSecs() - TimeTaskStart;
 
    
    
    if flag_Stimulation == 1
        disp('* Stimulating...');
        stimulationStatus = 1;
        send_trigger();
        if flag_Eyetracker == 1
            Eyelink('Message', 'TI TRIGGER');
        end

        TaskTimings{timeIdx, 1} = datetime('now', 'Format', 'HH:mm:ss.SSS');
        TaskTimings{timeIdx, 2} = sprintf('TI TRIGGER');
        timeIdx = timeIdx + 1;
        
        pause(5)
%         stim_start = GetSecs();
    end
    
    %%%%%%%%%
    
        
    for i = 1:nTrials 
        
        if i==1
        copybuffer(bTaskWaitCross, 0)
        displaybuffer(0, 5000, 'Blank1Init');
        end
        
        copybuffer(bTaskWaitCross, 0)
        displaybuffer(0, dur.Blank1, 'Blank1');
        
        % Setting the effort for the decision making part
    %     eff_t=trials.effort(i);
        eff_t = trials.effort(i) + 0.0125.*randn(1);% Gaussian distribution with mean the effort level required and SD of 2.5% (so that 2SD=5%) - 08.02.2024 : halved uncertainty to to have 2SD = 2.5%
%         rew_t = trials.reward(i)+ rand(1) * 0.2 *trials.reward(i)
%         %+ ((trials.reward(i)*0.2)/3).*randn(1);
        rew_t = round(trials.reward(i) + ((trials.reward(i)*0.2)/3).*randn(1),1);

        if flag_Eyetracker == 1
            Eyelink('Message', 'T%d TRIAL BEGINNING', i);
        end

        TaskTimings{timeIdx, 1} = datetime('now', 'Format', 'HH:mm:ss.SSS');
        TaskTimings{timeIdx, 2} = sprintf('T%d TRIAL BEGINNING', i);
        timeIdx = timeIdx + 1;
    
        copybuffer(bDMcross, 0) % Preparing the offscreen buffer
        
        % Decision Making
        % Represent target level of force
        ypix_target = Y_HOME + ((Y_GOAL - Y_HOME).*(eff_t - 0.3)/0.7); 
     
        % Initialize parameters
        tt1 = 0; 
        tt = 0;
        resp = -1; % -1 if no response
        posi = []; % -S-
    
        displaybuffer(0, trials.durPrep_DM(i), 'PrepDM');                      % Here is when the "Is the reward worth the effort?" is presented (still, w/o the effort-reward information!)
        tic
        tt = toc;
        tt1 = tt;
    
        if flag_Eyetracker == 1
            Eyelink('Message', 'T%d Prep DM', i);
        end

        TaskTimings{timeIdx, 1} = datetime('now', 'Format', 'HH:mm:ss.SSS');
        TaskTimings{timeIdx, 2} = sprintf('T%d Prep DM', i);
        timeIdx = timeIdx + 1;
    
    
        while tt-tt1 < trials.durPrep_DM(i)/1000
            ky = checkkeydown;                                                    % Check is CTRL key has been pressed 
            tt = toc;
            if (ky(1) == 37 || ky(1) == 39)
                trials.Anticipation_DM(i) = 1;           
            end
        end
    
     %% Decision Making
    ttresp=NaN;
    tt2 = toc;
    TriggerFlag = 0;
    DecisionMadeFlag = 0;
    % FlagInformationAppearance = 0;
    while tt-tt2 < dur.DM/1000                                                 % While time for DM is not over     
    
         copybuffer(bDM, 0);
         drawrect(bargrey, 0, [0 ypix_target], [110*gain_screen 8*gain_screen], 0);

         if flag_Language == 1 % French
             disp('sto entrando qui')
            drawtext(['Pour ' num2str(rew_t) ' cents'], 0, [150*gain_screen ypix_target], 'Arial', sz, darkgrey); % Appearance of the effort-reward information 
         elseif flag_Language == 2 % English
            drawtext(['For ' num2str(rew_t) ' cents'], 0, [150*gain_screen ypix_target], 'Arial', sz, darkgrey); % Appearance of the effort-reward information
         end


         ky = checkkeydown;                                                    % Check is CTRL key has been pressed 
                   
         
         if DecisionMadeFlag == 0
     
            if ky(1) == 37 % left arrow --> the reward is worth the effort
                ttresp = tt; % time of response
    
                if flag_Eyetracker == 1
                    Eyelink('Message', 'T%d Decided Yes', i); % EYELINK TRIGGER (zero)
                end

                TaskTimings{timeIdx, 1} = datetime('now', 'Format', 'HH:mm:ss.SSS');
                TaskTimings{timeIdx, 2} = sprintf('T%d Decided Yes', i);
                timeIdx = timeIdx + 1;
    
                DecisionMadeFlag = 1;
    %             startsound;                                                  % starts playing. -S-
                posi = -x;  
                resp = 1; % left --> yes response:1
                drawround(bargrey, 0, [posi 40], 12*gain_screen); % Box ticked only when the arrow is pressed -S-
               
            elseif ky(1) == 39 % right arrow --> the reward is NOT WORTH the effort
                ttresp = tt;
    
                if flag_Eyetracker == 1
                    Eyelink('Message', 'T%d Decided No', i); % EYELINK TRIGGER (zero)
                end

                TaskTimings{timeIdx, 1} = datetime('now', 'Format', 'HH:mm:ss.SSS');
                TaskTimings{timeIdx, 2} = sprintf('T%d Decided No', i);
                timeIdx = timeIdx + 1;
    
                DecisionMadeFlag = 1;
    %             startsound;                                                  % starts playing. -S-
                posi = x;
                resp = 0; % right --> no response:2 -S-
                drawround(bargrey, 0, [posi 40], 12*gain_screen); % Box ticked only when the arrow is pressed -S-


            elseif ky(1) == 81 % If the Q key is pressed --> quit
                
                stoppsych;
                stopcosy;
       
                if flag_Eyetracker == 1
                    % stop eye-tracker
                    EyeLink_Close()
                end
    
            end
        
         end
    
        % Keep the box ticked after the arrow button release -S- 
        if ~isempty(posi)
            drawround(bargrey, 0, [posi 40], 12*gain_screen); 
        end 
    
    
        tt = displaybuffer(0, oneframe, 'DM'); % Here is when the reward-effort information is presented!
        tt = toc;

        if TriggerFlag == 0

             if flag_Eyetracker == 1
                Eyelink('Message', 'T%d Start DM', i);
             end

             TaskTimings{timeIdx, 1} = datetime('now', 'Format', 'HH:mm:ss.SSS');
             TaskTimings{timeIdx, 2} = sprintf('T%d Start DM', i);
             timeIdx = timeIdx + 1;    

             TriggerFlag = 1;
        end

        if tt-ttresp > dur.TimeAfterDMade/1000 % will break one second following the response of the subject (if the subject responds more than 1s before the dur.DM
            break 
        end 
         
        
    end

    if resp == -1 % if no response at all
        trials.DecisionTime(i) = NaN;
        trials.Acceptance(i) = -1;                                             % -1 if no decision is made
    else 
        trials.DecisionTime(i) = ttresp-tt2;
        trials.Acceptance(i) = resp;                                          % 1 if accepted, 0 if not accepted
    end 
            
    %% Effort production section
    if trials.Acceptance(i) == 1 && ismember(i, indx_Effort_Trials)  

  
         trials.EffortProduction(i) = 1; % 1 if the specific effort-reward combination is produced
        
         if  flag_MultipleKeyPressed==1
             % Preparation - Position fingers 
             check_pos = 0; check_time = 0; 
             [~, ~, k_time_start] = checkkeydown;

             displaybuffer(bPosition_fingers, 'Position');  
             if flag_Eyetracker == 1
                Eyelink('Message', 'T%d Start Hand Position', i);
             end

             while true                        
                 [k, ~, k_time] = checkkeydown;   
                 disp((k_time - k_time_start) - check_time)
                 if isempty(setdiff([65 69 87], k)) && check_pos == 0  && length(k) == 3
                    check_pos = 1;                                             % hand in position!
                    check_time = k_time - k_time_start;
                    trials.KeyPositionTime(i) = check_time;                % How many seconds it takes to get the correct hold position
                    disp(check_time)
                 elseif isempty(setdiff(k, [65 69 87])) && length(k) == 3 && check_pos == 1 && (k_time - k_time_start) - check_time > dur.TimeAfterPositionRight   
                    % Break if hand has been in the correct position for more than 1s
                    disp((k_time - k_time_start) - check_time)
                    break
                 end  
             end 
         end
         
         % Preparation - GET ready
         initAnticipTime = displaybuffer(bGetReadyForEP, trials.durPrep_EP(i), 'Prep');    % Start preparing the task and checking for anticipation
         tic 
         initAnticipTime = toc;
         newAnticipTime = initAnticipTime;
    
         if flag_Eyetracker == 1
            Eyelink('Message', 'T%d Prep EP', i); % EYELINK TRIGGER
         end

         TaskTimings{timeIdx, 1} = datetime('now', 'Format', 'HH:mm:ss.SSS');
         TaskTimings{timeIdx, 2} = sprintf('T%d Prep EP', i);
         timeIdx = timeIdx + 1;
            
            
         % Anticipation for KEYBOARD MODE (Check if keyboard pressed before "go!" signal)
         
         if KEYBOARD_MODE
            
            while newAnticipTime - initAnticipTime < trials.durPrep_EP(i)/1000 % [s]
    
                if flag_MultipleKeyPressed == 1
                    ActiveKey = 70; % F
                else
                    ActiveKey = 17; % CTRL
                end
                
                k = checkkeydown;
                
                if any(k == ActiveKey)  % if "F" key has been pressed CTRL = 71
                    anticip = 1;
                      break
                elseif any(k == 81) % If the Q key is pressed 
                
                    stoppsych;
                    stopcosy;

                    if flag_Eyetracker == 1
                        % stop eye-tracker
                        EyeLink_Close()
                    end
                    
                else
                    anticip = 0;
                end   
    
    %             newAnticipTime = displaybuffer(bTask, 0, 'GetTime'); % too slow
                    newAnticipTime = toc;
            end        
            
         end

        StartEffortProdFlag = 0;
    
        %% Beginning of the effort-production

        cursor_pos = 0; % cursor relative position (home is 0.0, max force is 1.0)
        started = 0; 
        cont = 0;
        t1 = 0;
        f=1;
        HandInPosition = 0;
        if ~anticip
            % Go signal
            copybuffer(bTaskWait, 0)                                                   % Preparing the offscreen buffer for the effort production
            
            if flag_Language == 1 % French
                drawtext('Go !!!', 0, [-250 ypix_target], 'Arial',sz+15,darkgrey); 
                drawtext(['Pour ' num2str(rew_t) ' cents'], 0, [340 ypix_target], 'Arial',sz+15,darkgrey);   
            else % English
                drawtext('Go !!!', 0, [-250 ypix_target], 'Arial',sz+15,darkgrey); 
                drawtext(['For ' num2str(rew_t) ' cents'], 0, [340 ypix_target], 'Arial',sz+15,darkgrey); 
            end

            drawrect(bargrey, 0, [0 ypix_target], [110*gain_screen 8*gain_screen], 0);   

            t = displaybuffer(0, oneframe, 'Task');     
            
            while true
                copybuffer(bTaskWait,0);
                
                if flag_Language == 1 % French
                    drawtext('Go !!!', 0, [-250 ypix_target], 'Arial',sz+15,darkgrey); 
                    drawtext(['Pour ' num2str(rew_t) ' cents'], 0, [340 ypix_target], 'Arial',sz+15,darkgrey);   
                else % English
                    drawtext('Go !!!', 0, [-250 ypix_target], 'Arial',sz+15,darkgrey); 
                    drawtext(['For ' num2str(rew_t) ' cents'], 0, [340 ypix_target], 'Arial',sz+15,darkgrey); 
                end   

                drawrect(bargrey, 0, [0 ypix_target], [110*gain_screen 8*gain_screen], 0);   
    
                if KEYBOARD_MODE
                    k = checkkeydown;
                    
                    keypr_ALL(f,i)= {k};% All keys pressed for each frame 
                    
                    if  flag_MultipleKeyPressed == 1
                    
                        if isempty(setdiff([65 87 69], k)) && length(k) == 3   % if ONLY the position keys are pressed
                            HandInPosition = 1;    % (AWEF-thumb on space)                   
                        end

                        if any(k == 70) && HandInPosition == 1             
                            % a = 65; w = 87; e = 69; f = 70; space = 32; r = 82; g = 71
                            keypr(f,i) = 1; 
                            if started == 0
                                trials.ReactionTimeEP(i) = toc;
                            end
                            started = 1; % Flag 
                            HandInPosition = 0;

                        elseif started == 0 % i.e. ctrl still not pressed in the current trial
                            keypr(f,i) = 0; % no ctrl-pressed event

                        elseif any(k == 70)  == 0  || HandInPosition == 0 % if F key not pressed at all 
                            keypr(f,i) = 0;

                        end
                        
                    else 
                        if (k(1) == 17 && cont == 0) % 17 = code of "Ctrl" key for Keyboard mode
                            keypr(f,i) = 1; %0.025
                            if started == 0
                                trials.ReactionTimeEP(i) = toc;
                            end
                            started = 1; % Flag 
                            cont = 1;

                        elseif started == 0 % i.e. ctrl still not pressed in the current trial
                            keypr(f,i) = 0; % no ctrl-pressed event
                            cont = 0;

                        % Handling the delay between key release and while loop speed
                        elseif (k(1) == 17 && cont == 1) % if ctrl pressed again while cont == 1 (i.e. it's not the first time)
                            keypr(f,i) = 0; % key-released event

                        elseif k(1) == 0 % if no key is pressed at all
                            keypr(f,i) = 0;
                            cont = 0;

                        end 
                    end 
                                     
                    cursor_pos = (((mean(keypr(1:f,i), "omitnan").*Hz)./GV)- 0.3)./0.7; % scaling cursor pos to the bar that goes from 30% to 100% of MTS
%                   cursor_pos = (mean(keypr(1:f,i), "omitnan").*Hz)./GV;  % GV is max tapping freq in Hz % 1 to i
    
                    if cursor_pos < 0
                        cursor_pos = 0;
                    end
    
                else % if not keyboard mode
                    v = -1.*axis(AI,2);               
                    volt = median(v);
                    cursor_pos = (volt - BASELINE_VOLTAGE) / GV; %%% Normalization in % MVC???       
                end
               
                
                    % Draw position 
                    ypix = min(Y_HOME + (Y_GOAL - Y_HOME) * cursor_pos, 200*gain_screen); % set a limit to avoid that the bar goes over the box upper limit
                       
                    
                %% Grey moving bar - version adapted to pupillometry

                drawrect(DARK_GREY, 0, [0 ypix], [110*gain_screen 8*gain_screen], 0);                

                t = displaybuffer(0, oneframe, 'Task'); % This is when the effort production should start!!! before then, the trial is anticipated
                
    
                if StartEffortProdFlag == 0
                    tic % needed to take the ReactionTimeEP
                    if flag_Eyetracker == 1
                        Eyelink('Message', 'T%d Start EP', i); % EYELINK TRIGGER
                    end 

                    TaskTimings{timeIdx, 1} = datetime('now', 'Format', 'HH:mm:ss.SSS');
                    TaskTimings{timeIdx, 2} = sprintf('T%d Start EP', i);
                    timeIdx = timeIdx + 1;

                    StartEffortProdFlag = 1;
                end
                
                if t1 == 0 
                    t1 = t;
                end
                           
                f = round(((t-t1))/oneframe) + 1; % index of frame
                
    
    
    
                if f <= nFrames
                    CURSOR(f,i) = cursor_pos; % CURSOR matrix takes the moving average of the tapping frequency
    %                 sprintf("CURSOR(%d,%d) = %f \n", f, i, CURSOR)
    
                else
                    break % <================ BREAK ================!!! will break the while loop when trial is over
                end
    
            end % end while loop
        end % end *if ~anticip* loop
    
        % Blank 2 - black cross
        copybuffer(bTaskWaitCross, 0)
        displaybuffer(0, dur.Blank2, 'Blank2'); % Interval waiting for reward

        if flag_Eyetracker == 1
            Eyelink('Message', 'T%d WaitingFeedback', i); % EYELINK TRIGGER
        end

        TaskTimings{timeIdx, 1} = datetime('now', 'Format', 'HH:mm:ss.SSS');
        TaskTimings{timeIdx, 2} = sprintf('T%d WaitingFeedback', i);
        timeIdx = timeIdx + 1;
         
    %     sprintf("CURSOR(%d,%d) = %f \n", f, i, CURSOR)
    
        % Reward
        if ~anticip
            if (mean(keypr(1:nFrames,i), "omitnan").*Hz)/GV >= eff_t % if mean of the frequency of tapping is above the required threshold --> success
                isSuccess = true;
                copybuffer(bSuccess, 0)
                drawtext(['+ ' num2str(rew_t) ' cents'], 0, [270 y+280], 'Arial', sz+10, darkgrey);
                displaybuffer(0, dur.Reward, 'Reward');

                if flag_Eyetracker == 1
                    Eyelink('Message', 'T%d FeedbackSuccess', i); % EYELINK TRIGGER
                end

                TaskTimings{timeIdx, 1} = datetime('now', 'Format', 'HH:mm:ss.SSS');
                TaskTimings{timeIdx, 2} = sprintf('T%d FeedbackSuccess', i);
                timeIdx = timeIdx + 1;
    
            elseif (mean(keypr(1:nFrames,i), "omitnan").*Hz)/GV < 0.7 .* eff_t % NEW FEB 2024 : If the person does not try --> he/she looses the amount that was at stake
                isSuccess = -1; % -1 = big failure
                 copybuffer(bFailure, 0)
                 drawtext(['- ' num2str(rew_t) ' cents'], 0, [270 y+280], 'Arial', sz+10, darkgrey);
                 displaybuffer(0, dur.Reward, 'Reward');
                if flag_Eyetracker == 1
                    Eyelink('Message', 'T%d FeedbackBigFailure', i); % EYELINK TRIGGER
                end 
            else          
                isSuccess = false; % i.e. failure -S-
                displaybuffer(bFailure, dur.Reward, 'Reward');
                if flag_Eyetracker == 1
                    Eyelink('Message', 'T%d FeedbackFailure', i); % EYELINK TRIGGER
                end

                TaskTimings{timeIdx, 1} = datetime('now', 'Format', 'HH:mm:ss.SSS');
                TaskTimings{timeIdx, 2} = sprintf('T%d FeedbackFailure', i);
                timeIdx = timeIdx + 1;
                
            end
        else   
            isSuccess = false; % i.e. anticipated  
            displaybuffer(bAnticip, dur.Reward, 'AnticipError');
            
            if flag_Eyetracker == 1
                    Eyelink('Message', 'T%d FeedbackAnticip', i); % EYELINK TRIGGER
            end

            TaskTimings{timeIdx, 1} = datetime('now', 'Format', 'HH:mm:ss.SSS');
            TaskTimings{timeIdx, 2} = sprintf('T%d FeedbackAnticip', i);
            timeIdx = timeIdx + 1;
            
        end  
    
        % Pupil baseline recovery
        displaybuffer(bRectCross, dur.TimeForPupilBaselineBack, 'StartPupilRecov'); 
    
        displaybuffer(bRectCross); % To make sure that there are not grey buffers before starting the next trial

    
        % (Store Data)
        if ~anticip
            trials.success(i) = isSuccess;
            trials.Anticipation_EP(i) = false;
        else
    %         trials.success(i) = false;
            trials.Anticipation_EP(i) = true;
        end
        
    end

    displaybuffer(bRectCross); % To make sure that there are not grey buffers before starting the next trial
         
    if i == nTrials % display on last trial
        total_gains = nansum(trials.reward.*(~(trials.success == 0)).*(~(trials.success == -1)).*(trials.Acceptance == 1).*(~(trials.Anticipation_EP == 1)))/100;   % FEB2024 : removes trial with big failure (indicated as -1 in trials.success) 
        total_gains = total_gains - (sum(trials.reward(trials.success == -1))./100);
        btotal = newbuffer;
        drawtext(['Total = ' num2str(total_gains) ' CHF'], btotal, [0 0], 'Arial', sz+10, darkgrey); 
        displaybuffer(btotal, 5000, 'Total');
        wait(5000);

        if flag_Eyetracker == 1
            Eyelink('Message', 'T%d TotalReward', i); % EYELINK TRIGGER
        end

        TaskTimings{timeIdx, 1} = datetime('now', 'Format', 'HH:mm:ss.SSS');
        TaskTimings{timeIdx, 2} = sprintf('T%d TotalReward', i);
        timeIdx = timeIdx + 1;
    end
     
    % Save the true effort level (taken from normal distribution)
    trials.efftested(i) = eff_t; 
    trials.rewtested(i) = rew_t; 
    
    % (Intertrial)
%     stoptrial; % -----------------------------------------------------
        
     
    end
    
    %% Saving and closing the toolboxes
    
    savefile = ['S' num2str(SubjectNum) '_' block_name datesuffix];
    save(savefile)
    
    stoppsych;
    stopcosy;
    
    fprintf('------   \n');
    fprintf('Block finished :) \n');
    fprintf('------   \n'); 
    
    if flag_Eyetracker == 1
        % stop eye-tracker        
        EyeLink_Close()
    end

    catch MException
%         savefile = ['catch_' 'S' num2str(SubjectNum) '_' block_name datesuffix];
%         save(savefile) 
        rethrow(MException)
    end

end