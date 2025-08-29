# coding: utf-8
# French: Decision phase that writes directly into the original DataFrame
from psychopy import core  # visual not needed here unless you draw off-screens
from keyboard import poll_keys, clear_events, QuitSignal # <-- import the helpers you use
from config import keys_choice
from ws_stream import TrialStreamer
import numpy as np

def decision_phase(streamer, i, win, screens, kb, io, expClock, dur, trials, TaskTimings, flag_MapYesAtRight):
    """
    Execute the decision phase for trial i, reading inputs from 'trials' and
    writing results back in-place using .at/.loc (no chained assignment).
    """

    # --- 0) Resolve per-trial inputs & durations ---
    # English: snapshot row for safe reads; all writes use trials.at[...] below
    row = trials.loc[i]

    # English: per-trial prep duration from DF; fall back to 1000ms if missing
    dur_prep_ms = int(row.get('durPrep_DM', 1000))

    # English: DM & after-DM durations from the 'dur' dict; use safe defaults
    dur_dm_ms   = int(dur.get('DM', 3000))
    after_dm_ms = int(dur.get('TimeAfterDMade', 500))

    # --- 1) Reset per-trial writable vars (in-place, no chained assignment) ---
    trials.at[i, 'Anticipation_DM'] = 0
    resp = -1
    decision_made = False
    choice = None
    t_resp = None
    trigger_logged = False

    # --- 2) Preparation (bDMcross) ---

    # English: draw the static cross buffer once during the prep window
    for elem in screens._create_dmcross_buffer(flag_MapYesAtRight=flag_MapYesAtRight):
        elem.draw()
    win.flip()
    streamer.send_event("Preparation DM start", {"trial": i+1, "durPrepDM [ms]": dur_prep_ms, "t": expClock.getTime()})
    prepClock = core.Clock() # Initialisation of psychopy clock
    # English: continuous anticipation detection during prep period
 
    while prepClock.getTime() < (dur_prep_ms / 1000.0):
        events = poll_keys(kb, io)
        for ev in events:
            key_name = ev.key if hasattr(ev, 'key') else ev
            if key_name in keys_choice and trials.at[i, 'Anticipation_DM'] == 0:
                trials.at[i, 'Anticipation_DM'] = 1
                TaskTimings.append((expClock.getTime(), f"T{i} Anticipation DM"))
        core.wait(0.001)  # English: small sleep to avoid busy-wait
    TaskTimings.append((expClock.getTime(), f"T{i} Prep DM"))

    # --- 3) Decision making (frame-by-frame) ---
    clear_events(kb, io)
    decClock = core.Clock()
    t_start = decClock.getTime()

    while (decClock.getTime() - t_start) < (dur_dm_ms / 1000.0):
        # English: draw dynamic decision buffer using current choice (highlight)
        elems = screens._create_decision_dynamic_buffer(
            effort_level=(float(row['effort'])-0.3)/0.7,  
            rew_t=float(row['reward']),
            choice=choice,
            flag_MapYesAtRight=flag_MapYesAtRight
        )
        for stim in elems:
            stim.draw()
        win.flip()
        # English: log "Start DM" once
        if not trigger_logged:
            TaskTimings.append((expClock.getTime(), f"T{i} Start DM"))
            streamer.send_event("Start DM", {"trial": i+1, "t": expClock.getTime()})
            trigger_logged = True

        # English: poll for decision keys
        t0 = expClock.getTime()
        events = poll_keys(kb, io)
        for ev in events:
            key_name = ev.key if hasattr(ev, 'key') else ev
            if not decision_made and key_name in keys_choice:
                if flag_MapYesAtRight:
                    if key_name == keys_choice[1]:
                        resp = 1
                        choice = "yes"
                        decision_made = True
                        t_resp = decClock.getTime()
                        TaskTimings.append((expClock.getTime(), f"T{i} Decided Yes"))
                    elif key_name == keys_choice[0]:
                        resp = 0
                        choice = "no"
                        decision_made = True
                        t_resp = decClock.getTime()
                        TaskTimings.append((expClock.getTime(), f"T{i} Decided No"))
                else:
                    if key_name == keys_choice[0]:
                        resp = 1
                        choice = "yes"
                        decision_made = True
                        t_resp = decClock.getTime()
                        TaskTimings.append((expClock.getTime(), f"T{i} Decided Yes"))
                    elif key_name == keys_choice[1]:
                        resp = 0
                        choice = "no"
                        decision_made = True
                        t_resp = decClock.getTime()
                        TaskTimings.append((expClock.getTime(), f"T{i} Decided No"))
                t1 = expClock.getTime() - t0
                print(f"duration : {t1}")
                streamer.send_event("Decision", {"trial": i+1, "choice": resp, "t":expClock.getTime()})
                t_start = decClock.getTime() - dur_dm_ms + after_dm_ms

"""
        # English: keep displaying ~after_dm_ms after response, then break
        if decision_made and (decClock.getTime() - t_resp) > (after_dm_ms / 1000.0):
            break
"""
        core.wait(0.001)

    # --- 4) Record results (in-place) ---
    if decision_made:
        trials.at[i, 'DecisionTime'] = t_resp - t_start
        trials.at[i, 'Acceptance']   = resp
    else:
        trials.at[i, 'DecisionTime'] = np.nan
        trials.at[i, 'Acceptance']   = -1
