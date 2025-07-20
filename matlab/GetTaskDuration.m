function dur = GetTaskDuration(flag_Eyetracker, flag_Population)

    % Specify here the parameters for the task!!
    if flag_Population == 1 % Healthy       

        dur.Blank1 = 2000; % intertrial interval 1 s (starting at the beginning of the for loop)
        dur.DM_Preparation = [1000 1400]; % between bDMcross and bDM+"For x cents"
        dur.DM = 4000; % decision-making phase 
        dur.TimeAfterDMade = 1000; % 1s after the decision is made, force the next phase
        dur.TimeAfterPositionRight= 1000;% Time that the program waits after detection of correct hold keys until next screen
        dur.GetReadyForEP = 1000;
        dur.EP_Preparation = [1000 1400]; % between bGetReadyForEP and effort bar + Go!
        dur.Task = 8000; % duration of the EP (from Go! to end of effort-production phase) 
        dur.Blank2 = 500; % between end of effort-production phase and reward
        dur.Reward = 1000; % duration of the reinforcement feedback (bReward presented)
        if flag_Eyetracker == 1
            dur.TimeForPupilBaselineBack = 2000; % 10 s to allow for pupil baseline recovery after effort production
        else
            dur.TimeForPupilBaselineBack = 2000; % 2 s for the patient
        end
        
    elseif flag_Population == 2 % Old 
        
        dur.Blank1 = 2000; % intertrial interval 1 s (starting at the beginning of the for loop)
        dur.DM_Preparation = [1000 1400]; % between bDMcross and bDM+"For x cents"
        dur.DM = 6000; % decision-making phase    
        dur.TimeAfterDMade = 1000; % 1s after the decision is made, force the next phase
        dur.TimeAfterPositionRight= 1000;% Time that the program waits after detection of correct hold keys until next screen
        dur.GetReadyForEP = 1000;
        dur.EP_Preparation = [1800 2200]; % between bGetReadyForEP and effort bar + Go!
        dur.Task = 6000; % duration of the EP (from Go! to end of effort-production phase) 
        dur.Blank2 = 500; % between end of effort-production phase and reward
        dur.Reward = 1000; % duration of the reinforcement feedback (bReward presented)
        if flag_Eyetracker == 1
            dur.TimeForPupilBaselineBack = 2000; % 10 s to allow for pupil baseline recovery after effort production
        else
            dur.TimeForPupilBaselineBack = 2000; % 2 s for the patient
        end
        
    elseif flag_Population == 3 % DBS implanted 
            dur.Blank1 = 2000; % intertrial interval 1 s (starting at the beginning of the for loop)
            dur.DM_Preparation = [1000 1400]; % between bDMcross and bDM+"For x cents"
            dur.DM = 6000; % decision-making phase    
            dur.TimeAfterDMade = 1000; % 1s after the decision is made, force the next phase
            dur.TimeAfterPositionRight= 1000;% Time that the program waits after detection of correct hold keys until next screen
            dur.GetReadyForEP = 1000;
            dur.EP_Preparation = [1800 2200]; % between bGetReadyForEP and effort bar + Go!
            dur.Task = 6000; % duration of the EP (from Go! to end of effort-production phase) 
            dur.Blank2 = 500; % between end of effort-production phase and reward
            dur.Reward = 1000; % duration of the reinforcement feedback (bReward presented)
            if flag_Eyetracker == 1
                dur.TimeForPupilBaselineBack = 2000; % 10 s to allow for pupil baseline recovery after effort production
            else
                dur.TimeForPupilBaselineBack = 2000; % 2 s for the patient
            end
    end

end