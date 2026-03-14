from psychopy import core
from keyboard import poll_keys, clear_events
from config import keys_choice, parse_args, get_reward_proposed
import numpy as np
from trigger_and_logs_manager import TriggerCodes

def decision_phase(streamer, i, win, screens, kb, io, expClock, dur, trials, triggers, flag_MapYesAtRight, cfg):
    """
    STEPS:
    1) Preparation to the decision-making phase
    2) Beginning of the decision-making phase (offer presentation)
    3) Response detection, if expressed within the decision window (DUR_DM); Response displayed for DUR_DM_FEEDB
    4) Log response (and response time if the decision was actually expressed, NaN instead)
    """

    ##### Convert trial durations to seconds
    current_trial = trials.loc[i]
    
    DUR_PREP_DM  = int(current_trial['durPrep_DM']) / 1000.0
    DUR_DM    = int(dur.DM) / 1000.0
    DUR_DM_FEEDB  = int(dur.TimeAfterDMade) / 1000.0

    ##### Variables/flags initialization
    response = -1
    decision_made = False
    choice = None
    decision_time = None
    start_trigger_sent = False

    ##### Initialization of effort and reward
    effort_tested = float(current_trial['effort'])
    rew_tested = float(current_trial['reward'])

    if cfg.ws_streaming.lower() == "true": # If streaming to VR, different effort rescaling!
        eff_norm = 1 - effort_tested                
    else:
        eff_norm = (effort_tested - 0.3) / 0.7
        eff_norm = max(0.0, min(1.0, eff_norm))


    ##################################################################################################
    # 1) Preparation to the decision-making phase
    ##################################################################################################

    ##### Display screen for preparation of the decision-making phase
    for elem in screens._create_dmcross_buffer(flag_MapYesAtRight=flag_MapYesAtRight):
        elem.draw()
    win.flip()

    ##### Send out triggers
    if triggers is not None:  
        triggers.send(TriggerCodes.PREP_DM)

    if cfg.ws_streaming.lower() == "true":
        streamer.send_event(
            "Preparation DM start",
            {"event_": "PrepDM", "dur_Prep_DM": round(DUR_PREP_DM,2)}
        )

    ##### Checking for anticipation
    preparationClock = core.Clock()
    while preparationClock.getTime() < DUR_PREP_DM:
        events = poll_keys(kb, io)
        if events and trials.at[i, 'Anticipation_DM'] == 0:
            for ev in events:
                key_name = ev.key if hasattr(ev, 'key') else ev
                if key_name in keys_choice:
                    trials.at[i, 'Anticipation_DM'] = 1
                    break
        core.wait(0.001) # check if really needed!


    ##################################################################################################
    # 2) Beginning of the decision-making phase
    ##################################################################################################

    clear_events(kb, io)
    decisionClock = core.Clock()  

    while True:
        current_time = decisionClock.getTime()

        _ = poll_keys(kb, io) # Always poll once per loop to catch 'escape' even if no input needed 


        ##### Check exit condition: before response -> bounded by DUR_DM; after response -> bounded by decision_time + DUR_DM_FEEDB
        time_exit_condition = decision_time+DUR_DM_FEEDB if decision_made else DUR_DM
        if current_time >= time_exit_condition:
            break

        ##### Display screen for offer presentation
        elems = screens._create_decision_dynamic_buffer(
            effort_level=eff_norm,
            rew_t=rew_tested,
            choice=choice,                       
            flag_MapYesAtRight=flag_MapYesAtRight
        )
        for elem in elems:
            elem.draw()
        win.flip()

        ##### Send out triggers
        if not start_trigger_sent:
            if triggers is not None:  
                triggers.send(TriggerCodes.START_DM)
            start_trigger_sent = True


        # Send "Start DM" once right after first flip
        # if not start_trigger_sent:
        #     #TaskTimings.append((expClock.getTime(), f"T{i} Start DM"))
        #     if cfg.ws_streaming.lower() == "true":
        #         allRewards = get_reward_proposed()
        #         currentReward = float(current_trial['reward'])
        #         RewardLevel = int(np.where(allRewards == currentReward)[0][0]) + 1

        #         streamer.send_event(
        #             "DM phase (offer presentation)",
        #             {"event_": "DMphase", "dur_DMphase": 6, "Effort": 1 - eff_norm, "Reward": RewardLevel} # this 1-eff_norm is already done in the VR, here it only compensates for line 78 and it's for lab-based coherent visualization during VR
        #             )     # round(DUR_DM,2)           
        #     start_trigger_sent = True

    ##################################################################################################
    # 3) Response detection
    ##################################################################################################

        # Poll keys only if response not yet made and time-out not reached yet
        if not decision_made and current_time < DUR_DM:
            events = poll_keys(kb, io)
            if events:
                for ev in events:
                    key_name = ev.key if hasattr(ev, 'key') else ev
                    if key_name in keys_choice:
                        # Map keys -> yes/no depending on layout (see config.py)
                        if flag_MapYesAtRight:
                            if key_name == keys_choice[1]:
                                response, choice = 1, "yes"
                            elif key_name == keys_choice[0]:
                                response, choice = 0, "no"
                            else:
                                continue
                        else:
                            if key_name == keys_choice[0]:
                                response, choice = 1, "yes"
                            elif key_name == keys_choice[1]:
                                response, choice = 0, "no"
                            else:
                                continue

                        decision_time = current_time  
                        decision_made = True
                        # The tick will be displayed at the next (and last) iteration of the while loop

                        ##### Send out triggers
                        if triggers is not None:  
                            triggers.send(TriggerCodes.DECISION_MADE)

                        if cfg.ws_streaming.lower() == "true":
                            streamer.send_event(
                            "Decision Feedback",
                            {"event_": "DecisionFeedback", "DMFeedback": response, "dur_DecisionFeedback": dur.Feedback / 1000}
                            )                 

                        break

        core.wait(0.001)

    ##################################################################################################
    # 4) Log response (and response time if response was expressed)
    ##################################################################################################
    if decision_made:
        trials.at[i, 'DecisionTime'] = decision_time
        trials.at[i, 'Acceptance']   = response
    else:
        trials.at[i, 'DecisionTime'] = np.nan
        trials.at[i, 'Acceptance']   = -1
