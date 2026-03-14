# -*- coding: utf-8 -*-
# Purpose: Effort phase subroutines (positioning, get-ready, EP frames, feedback).
from psychopy import core
from keyboard import poll_keys, clear_events
from config import AWE_KEYS, CTRL_KEY, KEY_PRESS, KEY_RELEASE, parse_args, Task
import numpy as np
from enum import Enum, auto
import sys
from trigger_and_logs_manager import TriggerCodes


# ---------- helpers ----------
def init_cursor_matrix(task_ms, Hz, n_trials):
    """Allocate CURSOR matrix (#frames x #trials) for EP cursor values."""
    n_frames = int(np.floor((task_ms / 1000.0) * round(Hz)))
    CURSOR = np.full((n_frames, n_trials), np.nan, dtype=float)
    return CURSOR, n_frames


def all_keys_pressed(kb, win=None):
    """Return the set of currently held key names (polls kb to refresh state)."""
    _ = kb.getKeys(clear=False)  # refresh kb.state
    held = {k for k, pressed in getattr(kb, "state", {}).items() if pressed}
    return held

def compute_cursor_position(mean_onsets, effort, Hz, MTF, ws_streaming, task):

    if task == Task.EBDM:
        if ws_streaming:
            offset = 1 - effort
            cursor_position = ((mean_onsets * Hz) / MTF) / effort
            cursor_position = (cursor_position - offset) * (1 + offset)
        else:
            cursor_position = (((mean_onsets * Hz) / MTF) - 0.3) / 0.7
   
    elif task == Task.MTF:
            cursor_position = (((mean_onsets * Hz) / MTF) - 0.3) / 1.4 

    return max(0, min(cursor_position, 1)) 

def detect_tap(events, tap_key):

    for ev in events:
        key_name = ev.key if hasattr(ev, "key") else ev

        if key_name == tap_key and ev.type == KEY_PRESS:
            return True

    return False


def draw_ep_frame(task, screens, reward_val, target_effort, cfg):
    
    def draw_buffer(buffer):
        for elem in buffer:
            elem.draw()

    if task == Task.EBDM:
        draw_buffer(screens.bTaskWait)
        draw_buffer(screens._create_reward_buffer(reward_val, target_effort))
        draw_buffer(screens._create_bar_buffer(target_effort))

    elif task == Task.MTF and cfg.block_id == "MTF_PRE":
        draw_buffer(screens.bTaskWaitCross)

    elif task == Task.MTF and cfg.block_id == "MTF_VF":
        draw_buffer(screens.bTaskWait)
        draw_buffer(screens._create_bar_buffer(target_effort))

    draw_buffer(screens.bGoEP)



# ---------- phases ----------
def hand_positioning_phase(
    streamer, i, win, screens, kb, expClock, dur, trials, TaskTimings, triggers,
    flag_MultipleKeyPressed, cfg, io=None, 
):
    """
    STEPS:
    1) Show hand positioning screen
    2) Detect when the required keys are pressed and wait that the keys are held for DUR_HOLD_REQUIRED
    """

    ##### Convert trial durations to seconds
    DUR_HOLD_REQUIRED    = int(dur.TimeAfterPositionRight) / 1000.0

    ##### Select screen and required keys to be held
    if flag_MultipleKeyPressed == 1:
        draw_buffer = screens.bPosition_fingers_1
        REQUIRED_KEYS = AWE_KEYS
    else:
        draw_buffer = screens.bPosition_finger_2
        REQUIRED_KEYS = CTRL_KEY

    ##################################################################################################
    # 1) Show hand positioning screen
    ##################################################################################################
    
    for elem in draw_buffer:
        elem.draw()        
    win.flip()

    ##### Send out triggers
    if triggers is not None:  
        triggers.send(TriggerCodes.REQUIRED_HAND_POSITION)

    ##################################################################################################
    # 2) Detect when the required keys are pressed and wait that the keys are held for DUR_HOLD_REQUIRED
    ##################################################################################################

    start_time = core.getTime()
    hold_start_time = None

    while True:
        _ = poll_keys(kb, io) # Allow ESC detection
        current_time = core.getTime()
        held_keys = {k for k, pressed in getattr(kb, "state", {}).items() if pressed}

        if held_keys == REQUIRED_KEYS:

            if hold_start_time is None:
                hold_start_time = current_time
                trials.at[i, 'KeyPositionTime'] = current_time - start_time

            elif (current_time - hold_start_time) > DUR_HOLD_REQUIRED:

                if cfg.ws_streaming.lower() == "true":
                    streamer.send_event("hand positionning time", {"trial": i + 1, "t": expClock.getTime()})
                break
        else:
            hold_start_time = None

        core.wait(0.001)  # tiny sleep to avoid busy spin


def get_ready_phase(
    streamer, i, win, screens, kb, io, expClock, trials,
    flag_MultipleKeyPressed, KEYBOARD_MODE, TaskTimings, triggers, cfg, dur
):
    """
    STEPS:
    1) Show get_ready screen
    2) Detect anticipation events within dur_prep_EP

    LOGIC:
    - If hold CTRL mode --> anticipation if key released
    - If hold AWE mode --> anticipation if key pressed
    """

    ##################################################################################################
    # 1) Show get_ready screen
    ##################################################################################################
  
    for elem in screens.bGetReadyForEP:
        elem.draw()
    win.flip()

    ##### Send out triggers
    if triggers is not None:  
        triggers.send(TriggerCodes.PREP_EP)

    preparationClock = core.Clock()
    TaskTimings.append((expClock.getTime(), f"T{i} Prep EP"))

    clear_events(kb, io)  # drop any buffered events
    active_key = 'f' if flag_MultipleKeyPressed == 1 else 'lctrl'
    anticipation_event = KEY_RELEASE if flag_MultipleKeyPressed == 2 else KEY_PRESS
    trials.at[i, 'Anticipation_EP'] = 0

    dur_prep_EP = int(trials.loc[i].get('durPrep_EP', 1000))
    if cfg.ws_streaming.lower() == "true":
        streamer.send_event(
        "Preparation EP start",
        {"event_": "PrepEP", "dur_Prep_EP": round((dur_prep_EP / 1000),2)} 
        ) 
        

    while preparationClock.getTime() < (dur_prep_EP / 1000.0):
        events = poll_keys(kb, io)  # also catches ESC
        if events:
            for ev in events:
                key_name = ev.key if hasattr(ev, 'key') else ev
                if key_name == active_key and ev.type == anticipation_event:
                    trials.at[i, 'Anticipation_EP'] = 1
                    # if cfg.ws_streaming.lower() == "true":
                    #     streamer.send_event(
                    #     "Preparation to the EPFeedback phase",
                    #     {"event_": "EPFeedback", "EPFeedback": -1, "dur_EPFeedback": dur.Feedback}
                    #     )
                    break
                
        core.wait(0.001)


def effort_production_phase(
    streamer, keys, i, win, screens, kb, io, expClock,
    dur, MTF, Hz, trials, CURSOR, triggers, keypr,
    flag_MultipleKeyPressed, cfg, task
):
    """
    Effort-production phase

    LOGIC:
    1) Compute the target effort level to display
    2) Display the initial effort production screen and send out trigger
    3) Initialize variables and clear any residual keyboard events
    4) Run the frame loop for the duration of the effort phase
    5) On each frame, detect tap onsets and validate them depending on the key mode
    6) Record the reaction time of the first valid tap
    7) Compute the cursor position and draw it 
    8) Enforce frame pacing to maintain the target refresh rate
    """

    ##### Triggers initialization
    ws_streaming = cfg.ws_streaming.lower() == "true"

    ##################################################################################################
    # 1) Compute the target effort level to display
    ##################################################################################################
 
    ##### Initialization of effort and reward values
    effort = float(trials.loc[i, "effort"])
    reward = float(trials.loc[i, "reward"]) if task == Task.EBDM else None

    ##### Compute target effort to display depending on the task
    if task == Task.EBDM:

        if ws_streaming:
            target_effort = 1 - effort
        else:
            target_effort = (effort - 0.3) / (1 - 0.3)

    elif task == Task.MTF and cfg.block_id == "MTF_VF":

        target_effort = 0.5

    ##################################################################################################
    # 2) Display the initial effort production screen and send out trigger
    ##################################################################################################

    ##### Display first EP screen (to avoid discontinuity)
    elem = draw_ep_frame(task, screens, reward, target_effort, cfg)
    win.flip()

    ##### Send out triggers
    if triggers is not None:  
        triggers.send(TriggerCodes.START_EP)

    ##################################################################################################
    # 3) Initialize variables and clear any residual keyboard events
    ##################################################################################################
    tap_key = 'f' if flag_MultipleKeyPressed == 1 else 'lctrl'
    EPClock = core.Clock()
    oneframe = 1.0 / float(Hz)
    nFrames = CURSOR.shape[0]
    started = False
    t0 = EPClock.getTime()
    clear_events(kb, io)
    tap_sum = 0
    cursor_position = 0

    ##################################################################################################
    # 4) Run the frame loop for the duration of the effort phase
    ##################################################################################################
    for f in range(nFrames):

        frame_start = EPClock.getTime()

        elem = draw_ep_frame(task, screens, reward, target_effort, cfg)

        ##################################################################################################
        # 5) On each frame, detect tap onsets and validate them depending on the key mode
        ##################################################################################################

        events = poll_keys(kb, io) 

        tap_happened = events and detect_tap(events, tap_key) \

        accept = tap_happened

        if tap_happened and flag_MultipleKeyPressed:
            keys_pressed = all_keys_pressed(kb, win) 
            accept = keys_pressed == (AWE_KEYS | {tap_key}) or keys_pressed == AWE_KEYS

        keypr[f, i] = int(bool(accept))

        ##################################################################################################
        # 6) Record the reaction time of the first valid tap
        ##################################################################################################

        if accept and not started:
            ##### Record the reaction time
            trials.at[i, 'ReactionTimeEP'] = EPClock.getTime() - t0
            started = True

        ##################################################################################################
        # 7) Compute the cursor position and draw it 
        ##################################################################################################        

        ##### Update the tap rate
        tap_sum += keypr[f, i]
        mean_onsets = tap_sum / (f + 1)

        if task in (Task.EBDM, Task.MTF) and (task != Task.MTF or cfg.block_id == 'MTF_VF'):

            if task == Task.EBDM:

                cursor_position = compute_cursor_position(
                    mean_onsets, effort, Hz, MTF, ws_streaming, task
                )

                if ws_streaming:
                    streamer.send_event(
                        "EP phase",
                        {
                            "event_": "EPphase",
                            "dur_EPphase": 6,
                            "cursor_pos": round(cursor_position, 2)
                        }
                    )

            CURSOR[f, i] = cursor_position

            for elem in screens._create_cursor_dynamic_buffer(cursor_position):
                elem.draw()

 
        win.flip()

        ##################################################################################################
        # 8) Enforce frame pacing to maintain the target refresh rate
        #################################################################################################
      
        elapsed = EPClock.getTime() - frame_start
        remain = oneframe - elapsed
        
        if remain > 0:
            core.wait(remain)



def waiting_for_feedback_phase(streamer, win, screens, dur, expClock, TaskTimings, i, cfg, triggers):
    """Cross between EP and feedback. Uses dur['Blank2'] (ms).
        streamer: is a dict with so and so
        win: is the Windows object from foo

    """

    for elem in screens.bTaskWaitCross:
        elem.draw()
    win.flip()

    ##### Send out triggers
    if triggers is not None:  
        triggers.send(TriggerCodes.WAITING_FEEDBACK_EP)

    core.wait(dur.Blank2 / 1000.0)


    if cfg.ws_streaming.lower() == "true":
        streamer.send_event(
            "Preparation to the EPFeedback phase",
            {"event_": "PreEPFeedback", "dur_Prep_EPFeedback": dur.Blank2 / 1000}
            )


def feedback_phase(streamer, i, win, screens, CURSOR, keypr, trials, TaskTimings, triggers, expClock, dur, cfg, task=Task, MTF=None, Hz=None):
    """
    Feedback based on mean onset frequency:
      success if (mean(keypr)*Hz)/MTF >= eff_t
      big failure if < 0.7*eff_t, else failure.
    """
    
    if trials.loc[i, 'Anticipation_EP'] == 1:
        print("ANTICIPATION!")
        trials.at[i, 'success'] = -1
        for elem in screens.bAnticip:
            elem.draw()
        # if cfg.ws_streaming.lower() == "true":
        #     streamer.send_event(
        #     "EPFeedback",
        #     {"event_": "EPFeedback", "EPFeedback": int(trials.at[i, 'success']), "dur_EPFeedback": dur.Feedback / 1000}
        #     )
        win.flip()

        ##### Send out triggers
        if triggers is not None:  
            triggers.send(TriggerCodes.FEEDBACK_EP)

        core.wait(dur.Feedback / 1000.0)
        return
    
    if task==Task.EBDM:
        eff_t = float(trials.loc[i, 'effort'])
        mean_onsets = float(np.nanmean(keypr[:, i]))
        tap_rate_norm = ((mean_onsets * Hz) / MTF)
        success = 1 if tap_rate_norm >= eff_t else 0 
        trials.at[i, 'success'] = success
        if cfg.ws_streaming.lower() == "true":

            streamer.send_event(
            "EPFeedback",
            {"event_": "EPFeedback", "EPFeedback": success, "dur_EPFeedback": dur.Feedback / 1000}
            )

        if success == 1:
            for elem in screens.bSuccess:
                elem.draw()
            TaskTimings.append((expClock.getTime(), f"T{i} FeedbackSuccess"))
        elif success == 0:
            for elem in screens.bFailure:
                elem.draw()
            TaskTimings.append((expClock.getTime(), f"T{i} FeedbackFailure"))
        

        win.flip()

        ##### Send out triggers
        if triggers is not None:  
            triggers.send(TriggerCodes.FEEDBACK_EP)

        core.wait(dur.Feedback / 1000.0)


def effort_phase(
    streamer, i, win, screens, kb, io,
    expClock, dur, MTF, Hz,
    trials, CURSOR, TaskTimings, triggers, keypr, cfg, task:Task,
    flag_MultipleKeyPressed=0, KEYBOARD_MODE=True
):
    """
    Wrapper for the EP pipeline of trial i:
      - Ensure columns exist
      - (Multi-key) posture -> get-ready -> EP OR (single-key) get-ready -> EP
      - Then Blank, Feedback, and Pupil baseline
    """
    for col in ("EffortProduction", "KeyPositionTime", "Anticipation_EP", "ReactionTimeEP", "success"):
        if col not in trials.columns:
            trials[col] = np.nan
    trials.at[i, 'EffortProduction'] = 1
    
    if flag_MultipleKeyPressed != 0:
        hand_positioning_phase(
            streamer, i, win, screens, kb, expClock, dur, trials, TaskTimings,
            flag_MultipleKeyPressed, cfg, io=io,
        )

    get_ready_phase(
        streamer, i, win, screens, kb, io, expClock, trials,
        flag_MultipleKeyPressed, KEYBOARD_MODE, TaskTimings, triggers, cfg, dur
    )

    if trials.loc[i, 'Anticipation_EP'] == 0:
        effort_production_phase(
            streamer, ['f'], i, win, screens, kb, io, expClock,
            dur, MTF, Hz, trials, CURSOR, triggers, keypr, flag_MultipleKeyPressed, cfg, task
        )

    waiting_for_feedback_phase(streamer, win, screens, dur, expClock, TaskTimings, i, cfg, triggers)
    
    feedback_phase(streamer, i, win, screens, CURSOR, keypr, trials, TaskTimings, triggers, expClock, dur, cfg, task, MTF=MTF, Hz=Hz)       

    if trials.loc[i, 'Anticipation_EP'] == 1 and task == Task.MTF:
        if not getattr(effort_phase, "_repeated", False):
            effort_phase._repeated = True
            print(f"Repeating trial {i} (first repeat only)")
            effort_phase(
                streamer=streamer,
                i=i,
                win=win,
                screens=screens,
                kb=kb,
                io=io,
                expClock=expClock,
                dur=dur,
                MTF=MTF,
                Hz=Hz,
                trials=trials,
                CURSOR=CURSOR,
                TaskTimings=TaskTimings,
                keypr=keypr,
                cfg=cfg,  # <-- explicitly pass cfg here
                flag_MultipleKeyPressed=flag_MultipleKeyPressed,
                KEYBOARD_MODE=True,
                task=Task.MTF)
            effort_phase._repeated = False
