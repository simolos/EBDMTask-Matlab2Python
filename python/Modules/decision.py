from psychopy import core
from keyboard import poll_keys, clear_events
from config import keys_choice, parse_args, get_reward_proposed
import numpy as np

def decision_phase(streamer, i, win, screens, kb, io, expClock, dur, trials, TaskTimings, flag_MapYesAtRight, cfg):
    """
    Decision phase with strict post-response display:
    - Response must occur before DM_S (decision window).
    - After a valid response, keep drawing the 'tick' for AFTER_S seconds, then exit loop.
    - Writes results back in-place to `trials`.
    """
    # --- Configuration
    # cfg = parse_args("main")

    # --- 0) Resolve per-trial inputs & durations ---
    row = trials.loc[i]
    dur_prep_ms  = int(row.get('durPrep_DM', 1000))
    dur_dm_ms    = int(dur.DM)
    after_dm_ms  = int(dur.TimeAfterDMade)

    # Convert once to seconds
    PREP_S   = dur_prep_ms / 1000.0
    DM_S     = dur_dm_ms   / 1000.0
    AFTER_S  = after_dm_ms / 1000.0

    # --- 1) Reset per-trial writable vars ---
    trials.at[i, 'Anticipation_DM'] = 0
    resp = -1
    decision_made = False
    choice = None
    t_resp = None
    start_trigger_sent = False

    # --- 2) Preparation (bDMcross) ---
    for elem in screens._create_dmcross_buffer(flag_MapYesAtRight=flag_MapYesAtRight):
        elem.draw()
    win.flip()

    if cfg.ws_streaming.lower() == "true":
        streamer.send_event(
            "Preparation DM start",
            {"event_": "PrepDM", "dur_Prep_DM": round(PREP_S,2)}
        )

    prepClock = core.Clock()  # zero at prep start
    while prepClock.getTime() < PREP_S:
        events = poll_keys(kb, io)  # keep to detect escape
        if events and trials.at[i, 'Anticipation_DM'] == 0:
            for ev in events:
                key_name = ev.key if hasattr(ev, 'key') else ev
                if key_name in keys_choice:
                    trials.at[i, 'Anticipation_DM'] = 1
                    TaskTimings.append((expClock.getTime(), f"T{i} Anticipation DM"))
                    break
        core.wait(0.001)
    TaskTimings.append((expClock.getTime(), f"T{i} Prep DM"))

    # --- 3) Decision making window ---
    clear_events(kb, io)
    decClock = core.Clock()  # zero at DM start
    decision_window_end = DM_S        # absolute (relative to decClock)
    post_resp_end = None              # set after first valid response

    while True:
        now = decClock.getTime()

        # --- Always poll once per loop to catch 'escape' even if no input needed ---
        _ = poll_keys(kb, io)  # no-op; poll to ensure escape is processed

        # Exit condition: before response -> bounded by DM_S; after response -> bounded by t_resp + AFTER_S
        current_end = post_resp_end if post_resp_end is not None else decision_window_end
        if now >= current_end:
            break

        # Draw dynamic decision buffer with tick when 'choice' is set
        eff_norm = (float(row['effort']) - 0.3) / 0.7
        eff_norm = max(0.0, min(1.0, eff_norm))

        elems = screens._create_decision_dynamic_buffer(
            effort_level=eff_norm,
            rew_t=float(row['reward']),
            choice=choice,                       # when not None, buffer shows the tick
            flag_MapYesAtRight=flag_MapYesAtRight
        )
        for elem in elems:
            elem.draw()
        win.flip()

        # Send "Start DM" once right after first flip
        if not start_trigger_sent:
            TaskTimings.append((expClock.getTime(), f"T{i} Start DM"))
            if cfg.ws_streaming.lower() == "true":
                allRewards = get_reward_proposed()
                currentReward = float(row['reward'])
                RewardLevel = int(np.where(allRewards == currentReward)[0][0]) + 1
                streamer.send_event(
                    "DM phase (offer presentation)",
                    {"event_": "DMphase", "dur_DMphase": 6, "Effort": float(row['effort']), "Reward": RewardLevel}
                    )     # round(DM_S,2)           
            start_trigger_sent = True

        # Poll keys only if response not yet made and still inside DM window
        if not decision_made and now < decision_window_end:
            events = poll_keys(kb, io)
            if events:
                for ev in events:
                    key_name = ev.key if hasattr(ev, 'key') else ev
                    if key_name in keys_choice:
                        # Map keys -> yes/no depending on layout
                        if flag_MapYesAtRight:
                            if key_name == keys_choice[1]:
                                resp, choice = 1, "yes"
                            elif key_name == keys_choice[0]:
                                resp, choice = 0, "no"
                            else:
                                continue
                        else:
                            if key_name == keys_choice[0]:
                                resp, choice = 1, "yes"
                            elif key_name == keys_choice[1]:
                                resp, choice = 0, "no"
                            else:
                                continue

                        decision_made = True
                        t_resp = now  # seconds since DM start
                        TaskTimings.append((expClock.getTime(), f"T{i} Decided {'Yes' if resp==1 else 'No'}"))
                        if cfg.ws_streaming.lower() == "true":
                            streamer.send_event(
                            "Decision Feedback",
                            {"event_": "DecisionFeedback", "DMFeedback": resp, "dur_DecisionFeedback": dur.Feedback / 1000}
                            )                 


                        # Strict post-response period: display tick for AFTER_S seconds, then exit loop
                        post_resp_end = t_resp + AFTER_S
                        break

        core.wait(0.001)

    # --- 4) Record results ---
    if decision_made:
        # DecisionTime = time from DM onset to keypress (seconds)
        trials.at[i, 'DecisionTime'] = t_resp
        trials.at[i, 'Acceptance']   = resp
    else:
        trials.at[i, 'DecisionTime'] = np.nan
        trials.at[i, 'Acceptance']   = -1
