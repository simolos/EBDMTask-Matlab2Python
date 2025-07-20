function [Cond_E_R, indx_Effort_Trials] = GetTrialCondition(nTrials, n_Effort_Trials, flag_Population)

if flag_Population == 1 % Healthy    
    Eff_Proposed = [0.5 0.65 0.8 0.95]'; % in percentage of max force
else
    Eff_Proposed = [0.45 0.6 0.75 0.9]'; % in percentage of max force
end


Rew_Proposed = [1 5 10 20]'; % in eurocents
N_total_comb = numel(Eff_Proposed)*numel(Rew_Proposed);
Cond_E_R = [];

% Create all    
[Effort, Reward] = meshgrid(Eff_Proposed, Rew_Proposed);
all_combinations = [Effort(:), Reward(:), zeros(length(Effort(:)),1)]; % third col =0 --> flag for decision-making only
all_combinations_EP = [Effort(:), Reward(:), ones(length(Effort(:)),1)];

if fix(nTrials/N_total_comb) > 0 % need to repeat more times some or all_combinations 

    EP_vector = [repmat(N_total_comb, [fix(n_Effort_Trials/N_total_comb) 1])' mod(n_Effort_Trials,N_total_comb)];
    EP_vector = [EP_vector zeros(1,fix(nTrials/N_total_comb)-length(EP_vector))];

    for b = 1:fix(nTrials/N_total_comb)     

        % Number of rows to select for each unique value (i.e. missing
        % conditions)
        rows_per_value = ceil(EP_vector(b)/length(Eff_Proposed));

        % Initialize a variable to store selected rows
        selected_rows = [];

        % Loop over unique values in the first column (i.e. Eff_Proposed)
        unique_values = unique(all_combinations(:, 1));
        for value = unique_values'
            % Find rows with the current unique value
            rows_with_value = all_combinations(all_combinations(:, 1) == value, :);
            if size(rows_with_value, 1) <= rows_per_value
                % If less, add the rows directly without shuffling
                selected_rows = [selected_rows; rows_with_value];
            else
                % Randomly shuffle and select rows_per_value rows
                selected_rows = [selected_rows; datasample(rows_with_value, rows_per_value, 'Replace', false)];
            end
        end


%             all_combinations(randperm(N_total_comb, EP_vector(b)),3) = 1;
        all_combinations(find(ismember(all_combinations, selected_rows, 'rows')),3) = 1;

        Cond_E_R = [Cond_E_R; all_combinations]; 

        all_combinations = [Effort(:), Reward(:), zeros(length(Effort(:)),1)]; % third col =0 --> flag for decision-making only
   
    end

    % Add missing EP-trials or remove extra EP-trials
    if length(find(Cond_E_R(:,3) == 1)) < n_Effort_Trials
        Cond_E_R = [Cond_E_R; all_combinations_EP(randperm(N_total_comb, n_Effort_Trials-length(find(Cond_E_R(:,3) == 1))), :)]; 
    elseif length(find(Cond_E_R(:,3) == 1)) > n_Effort_Trials % if there are more EP trials than expected
        Delete_EPtrial_idx = find(Cond_E_R(:,3) == 1);
        Cond_E_R(Delete_EPtrial_idx(randperm(length(Delete_EPtrial_idx), length(Delete_EPtrial_idx)-n_Effort_Trials)),:) = [];
    end

    % Add non-EP trials

    % Number of rows to select for each unique value (i.e. missing
    % conditions)
    rows_per_value = fix((nTrials - size(Cond_E_R,1))/length(Eff_Proposed));

    % Initialize a variable to store selected rows
    selected_rows = [];

    % Loop over unique values in the first column (i.e. Eff_Proposed)
    unique_values = unique(Cond_E_R(:, 1));
    for value = unique_values'
        % Find rows with the current unique value
        rows_with_value = all_combinations(all_combinations(:, 1) == value, :);
        if size(rows_with_value, 1) <= rows_per_value
            % If less, add the rows directly without shuffling
            selected_rows = [selected_rows; rows_with_value];
        else
            % Randomly shuffle and select rows_per_value rows
            selected_rows = [selected_rows; datasample(rows_with_value, rows_per_value, 'Replace', false)];
        end
    end
    
    % Add missing non-EP trials
    Cond_E_R = [Cond_E_R; selected_rows; all_combinations(randperm(N_total_comb, max(0,nTrials-size(Cond_E_R,1)-size(selected_rows,1))), :)]; 

else % all_combinations are enough to create Cond_E_R (nTrials < N_total_comb) --> select only nTrials uniformely  
    
    % SELECTION OF THE COMBINATIONS FOR THE DECISION-MAKING PHASE
    Cond_E_R = all_combinations; 
    
    % How many times will each effort be tested (will handle extra/missing combinations later!)
    single_effort_repetition_num = ceil(nTrials/length(Eff_Proposed));

    selected_combinations = [];

    % Loop over each effort
    for effort = Eff_Proposed'
        % Find rows with the current unique value
        rows_w_effort = all_combinations(all_combinations(:, 1) == effort, :);
        
        % Randomly shuffle and select rows_per_value rows
        selected_combinations = [selected_combinations; datasample(rows_w_effort, single_effort_repetition_num, 'Replace', false)];
    end
    
    Cond_E_R = all_combinations(find(ismember(all_combinations, selected_combinations, 'rows')),:);

    % Handle missing/extra DM trials
    if length(find(Cond_E_R(:,3) == 0)) < nTrials %PROBABLY NEVER THE CASE!!!!

        rows_per_value = nTrials - length(find(Cond_E_R(:,3) == 0));

        % Balance the DM trials to be added 
        unique_values = unique(all_combinations(:, 1));
        selected_rows = [];
        for value = unique_values'
            % Find rows with the current unique value
            rows_with_value = all_combinations(all_combinations(:, 1) == value, :);
            
            if size(rows_with_value, 1) <= rows_per_value
                % If less, add the rows directly without shuffling
                selected_rows = [selected_rows; rows_with_value];
            else
                % Randomly shuffle and select rows_per_value rows
                selected_rows = [selected_rows; datasample(rows_with_value, rows_per_value, 'Replace', false)];
            end
        end

        Delete_EPtrial_idx = find(ismember(Cond_E_R, selected_rows, 'rows'));


        Cond_E_R = [Cond_E_R; all_combinations(randperm(nTrials, nTrials-size(Cond_E_R,1)), :)]; % Here are randomly selected! no balance :(
    elseif length(find(Cond_E_R(:,3) == 0)) > nTrials % if there are more DM trials than expected

        % Balance the DM trials to be deleted 

        NumExtraTrials = (length(find(Cond_E_R(:,3) == 0)) - nTrials);
        rows_per_value = ceil(NumExtraTrials/length(Eff_Proposed));

        unique_values = unique(Cond_E_R(:, 1));
        selected_rows = [];
        for value = unique_values'

            % Find rows with the current unique value
            rows_with_value = Cond_E_R(Cond_E_R(:, 1) == value, :);

            if size(rows_with_value, 1) <= rows_per_value
                % If less, add the rows directly without shuffling
                selected_rows = [selected_rows; rows_with_value];
            else
                % Randomly shuffle and select rows_per_value rows
                selected_rows = [selected_rows; datasample(rows_with_value, rows_per_value, 'Replace', false)];
            end

        end

        Delete_EPtrial_idx = find(ismember(Cond_E_R, selected_rows, 'rows'));

        Cond_E_R(Delete_EPtrial_idx(randperm(length(Delete_EPtrial_idx), NumExtraTrials)),:) = [];           

    end




    % NOW SELECTION OF THE EFFORT-PRODUCTION PHASE COMBINATIONS
    % Number of rows to select for each unique value
    rows_per_value = ceil(n_Effort_Trials/length(Eff_Proposed));

    % Initialize a variable to store selected rows
    selected_rows = [];

    % Loop over unique values in the first column (i.e. Eff_Proposed)
    unique_values = unique(Cond_E_R(:, 1));
    for value = unique_values'
        % Find rows with the current unique value
        rows_with_value = Cond_E_R(Cond_E_R(:, 1) == value, :);

        if size(rows_with_value, 1) <= rows_per_value
            % If less, add the rows directly without shuffling
            selected_rows = [selected_rows; rows_with_value];
        else
            % Randomly shuffle and select rows_per_value rows
            selected_rows = [selected_rows; datasample(rows_with_value, rows_per_value, 'Replace', false)];
        end
    end
     
    Cond_E_R(find(ismember(Cond_E_R, selected_rows, 'rows')),3) = 1;

    % Handle missing/extra EP trials 
    if length(find(Cond_E_R(:,3) == 1)) < n_Effort_Trials % if there are less EP trials than expected
        
        DM_trials = Cond_E_R(find(Cond_E_R(:,3)==0),:);
        NumMissingTrials = n_Effort_Trials - length(find(Cond_E_R(:,3) == 1));
        rows_per_value = ceil(NumMissingTrials/length(Eff_Proposed));

        % Balance the DM trials to be added 
        unique_values = unique(Cond_E_R(:, 1));
        selected_rows = [];
        for value = unique_values'
            % Find rows with the current unique value
            rows_with_value = DM_trials(DM_trials(:, 1) == value, :);
            
            if size(rows_with_value, 1) <= rows_per_value
                % If less, add the rows directly without shuffling
                selected_rows = [selected_rows; rows_with_value];
            else
                % Randomly shuffle and select rows_per_value rows
                selected_rows = [selected_rows; datasample(rows_with_value, rows_per_value, 'Replace', false)];
            end
        end

        Delete_EPtrial_idx = find(ismember(Cond_E_R, selected_rows, 'rows'));
        
        Cond_E_R(Delete_EPtrial_idx(randperm(length(Delete_EPtrial_idx), NumMissingTrials)),3) = 1;           
    
    elseif length(find(Cond_E_R(:,3) == 1)) > n_Effort_Trials % if there are more EP trials than expected
        
        EP_trials = Cond_E_R(find(Cond_E_R(:,3)==1),:);
        NumExtraTrials = length(find(Cond_E_R(:,3) == 1)) - n_Effort_Trials;
        rows_per_value = ceil(NumExtraTrials/length(Eff_Proposed));

        unique_values = unique(Cond_E_R(:, 1));
        selected_rows = [];
        for value = unique_values'
            % Find rows with the current unique value
            rows_with_value = EP_trials(EP_trials(:, 1) == value, :);
            
            if size(rows_with_value, 1) <= rows_per_value
                % If less, add the rows directly without shuffling
                selected_rows = [selected_rows; rows_with_value];
            else
                % Randomly shuffle and select rows_per_value rows
                selected_rows = [selected_rows; datasample(rows_with_value, rows_per_value, 'Replace', false)];
            end
        end

        Delete_EPtrial_idx = find(ismember(Cond_E_R, selected_rows, 'rows'));

        Cond_E_R(Delete_EPtrial_idx(randperm(length(Delete_EPtrial_idx), NumExtraTrials)),3) = 0;           
    
    end


end     


% Randomized effort-reward combination 
Cond_E_R = Cond_E_R(randperm(size(Cond_E_R,1)),:); % Shuffle
indx_Effort_Trials = find(Cond_E_R(:,3)==1);

% sort(Cond_E_R(find(Cond_E_R(:,3)==0),:),1)
% sort(Cond_E_R(find(Cond_E_R(:,3)==1),:),1)
% 
% disp(numel(Cond_E_R(find(Cond_E_R(:,3)==1),1)))

end



     

