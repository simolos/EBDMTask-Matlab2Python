# -*- coding: utf-8 -*-
# Purpose: Effort phase subroutines (positioning, get-ready, EP frames, feedback).
from psychopy import core
from keyboard import poll_keys, clear_events
from config import combo, parse_args, Task
import numpy as np
from enum import Enum, auto



# ======= CONSTANTS ========
KEY_PRESS = 22
KEY_RELEASE = 23
# ==========================


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


# ---------- phases ----------
def hand_positioning_phase(
    streamer, i, win, screens, kb, expClock, dur, trials, TaskTimings,
    flag_MultipleKeyPressed, cfg, io=None, 
):
    """
    Show the finger-positioning buffer and wait until the required combo is held
    continuously for dur['TimeAfterPositionRight'] ms.
    Writes trials.at[i,'KeyPositionTime'] (time until first correct pose).
    """

    # --- Configuration
    # cfg = parse_args("main")

    if flag_MultipleKeyPressed == 1:
        for elem in screens.bPosition_fingers_1:
            elem.draw()
    else:
        for elem in screens.bPosition_finger_2:
            elem.draw()
    win.flip()

    t0 = core.getTime()
    trials.at[i, 'KeyPositionTime'] = np.nan
    held_since = None

    while True:
        # Always poll to catch ESC through poll_keys
        _ = poll_keys(kb, io)
        tnow = core.getTime()
        held = {k for k, pressed in getattr(kb, "state", {}).items() if pressed}

        if flag_MultipleKeyPressed == 1:
            if held == combo:
                if held_since is None:
                    held_since = tnow
                    trials.at[i, 'KeyPositionTime'] = tnow - t0
                elif (tnow - held_since) > (dur.TimeAfterPositionRight / 1000.0):
                    TaskTimings.append((expClock.getTime(), f"T{i} Hand in Position"))
                    if cfg.ws_streaming.lower() == "true":
                        streamer.send_event("hand positionning time", {"trial": i + 1, "t": expClock.getTime()})
                    break
            else:
                held_since = None
                trials.at[i, 'KeyPositionTime'] = np.nan

        elif flag_MultipleKeyPressed == 2:
            tap_key = {'lctrl'}
            if held == tap_key:
                if held_since is None:
                    held_since = tnow
                    trials.at[i, 'KeyPositionTime'] = tnow - t0
                elif (tnow - held_since) > (dur.TimeAfterPositionRight / 1000.0):
                    TaskTimings.append((expClock.getTime(), f"T{i} Hand in Position"))
                    if cfg.ws_streaming.lower() == "true":
                        streamer.send_event("hand positionning time", {"trial": i + 1, "t": expClock.getTime()})
                    break
            else:
                held_since = None
                trials.at[i, 'KeyPositionTime'] = np.nan

        core.wait(0.001)  # tiny sleep to avoid busy spin


def get_ready_phase(
    streamer, i, win, screens, kb, io, expClock, trials,
    flag_MultipleKeyPressed, KEYBOARD_MODE, TaskTimings, cfg, dur
):
    """
    Display 'Get ready' and detect anticipation within the per-trial EP jitter.
    Reads trials.loc[i,'durPrep_EP'] (ms) and writes trials.at[i,'Anticipation_EP'].
    Anticipation logic:
      - mode 2: anticipation on KEY_RELEASE of active key
      - else:   anticipation on KEY_PRESS of active key
    """

    print("Entered get_ready_phase")

    TaskTimings.append((expClock.getTime(), f"T{i} Get ready"))
    for elem in screens.bGetReadyForEP:
        elem.draw()
    win.flip()

    prepEPClock = core.Clock()
    TaskTimings.append((expClock.getTime(), f"T{i} Prep EP"))

    clear_events(kb, io)  # drop any buffered events
    activeKey = 'f' if flag_MultipleKeyPressed == 1 else 'lctrl'
    trials.at[i, 'Anticipation_EP'] = 0

    dur_prep_ms = int(trials.loc[i].get('durPrep_EP', 1000))
    if cfg.ws_streaming.lower() == "true":
        streamer.send_event(
        "Preparation EP start",
        {"event_": "PrepEP", "dur_Prep_EP": 1.28} 
        ) # round((dur_prep_ms / 1000),2)
        

    while prepEPClock.getTime() < (dur_prep_ms / 1000.0):
        events = poll_keys(kb, io)  # also catches ESC
        if events:
            for ev in events:
                key_name = ev.key if hasattr(ev, 'key') else ev
                if flag_MultipleKeyPressed == 2:
                    if key_name == activeKey and ev.type == KEY_RELEASE:
                        trials.at[i, 'Anticipation_EP'] = 1
                        # if cfg.ws_streaming.lower() == "true":
                        #     streamer.send_event(
                        #     "Preparation to the EPFeedback phase",
                        #     {"event_": "EPFeedback", "EPFeedback": -1, "dur_EPFeedback": dur.Feedback}
                        #     )
                        break
                else:
                    if key_name == activeKey and ev.type == KEY_PRESS:
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
    dur, MTF, Hz, trials, CURSOR, TaskTimings, keypr, flag_MultipleKeyPressed, cfg, task
):
    """
    EP frame loop:
      - On each frame, set keypr[f,i]=1 if tap onset is detected, else 0.
      - First onset defines ReactionTimeEP.
      - Compute normalized cursor from mean onset rate.
      - Draw EP layers and flip at Hz pace until nFrames.
    """

    # --- Configuration
    # cfg = parse_args("main")

    # Initial 'Go' frame (time zero)
        
    for elem in screens.bTaskWait:
        elem.draw()
    if task==Task.EBDM:
        if cfg.ws_streaming.lower() == "true": # If streaming to VR, different effort rescaling!
            target_effort = 1 - float(trials.loc[i, 'effort'])

        else:
            target_effort = (float(trials.loc[i, 'effort']) - 0.3) / (1-0.3) # 0.7 replaced by 1-0.3
        reward_val = float(trials.loc[i, 'reward']) 
        for elem in screens._create_reward_buffer(reward_val, target_effort):
            elem.draw()
        for elem in screens._create_bar_buffer(target_effort):
            elem.draw()
    win.flip()



    EPClock = core.Clock()
    TaskTimings.append((expClock.getTime(), f"T{i} Start EP"))
    if cfg.ws_streaming.lower() == "true":
        opening_percentage = 1 - float(trials.loc[i, 'effort'])
        streamer.send_event(
            "EP start",
            {"event_": "EPphase", "dur_EPphase": dur.Task / 1000, "cursor_pos": opening_percentage}
            )

    # Setup
    oneframe = 1.0 / float(Hz)
    nFrames = CURSOR.shape[0]
    started = False
    t0 = EPClock.getTime()
    clear_events(kb, io)
    tap_key = 'f' if flag_MultipleKeyPressed == 1 else 'lctrl'

    # Frame loop
    f = 0
    while f < nFrames:
        frame_t0 = EPClock.getTime()


        # Draw static layers
        if task==Task.EBDM:
            for elem in screens.bTaskWait:
                elem.draw()
            for elem in screens._create_reward_buffer(reward_val, target_effort):
                elem.draw()
            for elem in screens._create_bar_buffer(target_effort):
                elem.draw()
        elif task==Task.MTF:
            for elem in screens.bTaskWaitCross:
                elem.draw()

        for elem in screens.bGoEP:
            elem.draw()


        # Onset detection per mode
        if flag_MultipleKeyPressed == 1:
            events = poll_keys(kb, io)
            if not events:
                keypr[f, i] = 0
            else:
                for ev in events:
                    key_name = ev.key if hasattr(ev, 'key') else ev
                    if key_name == tap_key and ev.type == KEY_PRESS:
                        keys = all_keys_pressed(kb, win)
                        # Accept if combo is held, with or without the tap key co-held
                        if keys == (combo | {tap_key}) or keys == combo:
                            keypr[f, i] = 1
                            if not started:
                                trials.at[i, 'ReactionTimeEP'] = EPClock.getTime() - t0
                                started = True
                        else:
                            keypr[f, i] = 0
                    else:
                        keypr[f, i] = 0
        else:
            events = poll_keys(kb, io)
            if not events:
                keypr[f, i] = 0
            else:
                for ev in events:
                    key_name = ev.key if hasattr(ev, 'key') else ev
                    if key_name == tap_key and ev.type == KEY_PRESS:
                        keypr[f, i] = 1
                        if not started:
                            trials.at[i, 'ReactionTimeEP'] = EPClock.getTime() - t0
                            started = True
                    else:
                        keypr[f, i] = 0

        # Cursor from mean onset rate
        if task==Task.EBDM:
            mean_onsets = np.mean(keypr[: f + 1, i]) if f >= 0 else 0.0
            if cfg.ws_streaming.lower() == "true": # If streaming to VR, different effort rescaling!
                tap_rate = ((mean_onsets * Hz) / MTF) # I need to make it a fractional progress relative to target effort!! 
                cursor_pos = (1 - float(trials.loc[i, 'effort'])) + (min(tap_rate / float(trials.loc[i, 'effort']), 1)  * float(trials.loc[i, 'effort']) )
                if cursor_pos < 0:
                    cursor_pos = 0
                elif cursor_pos > 1:
                    cursor_pos = 1
            else:
                cursor_pos = (((mean_onsets * Hz) / MTF) - 0.3) / 0.7
                if cursor_pos < 0:
                    cursor_pos = 0
                elif cursor_pos > 1:
                    cursor_pos = 1

            CURSOR[f, i] = cursor_pos
            if cfg.ws_streaming.lower() == "true":
                streamer.send_event(
                    "EP phase",
                    {"event_": "EPphase", "dur_EPphase": 6, "cursor_pos": round(cursor_pos, 2)}
                    )

            # Dynamic cursor
            for elem in screens._create_cursor_dynamic_buffer(CURSOR[f, i]):
                elem.draw()
        win.flip()

        f += 1
        # Pace to Hz
        elapsed = EPClock.getTime() - frame_t0
        remain = oneframe - elapsed
        if remain > 0:
            core.wait(remain)


def blank_phase(streamer, win, screens, dur, expClock, TaskTimings, i, cfg):
    """Cross between EP and feedback. Uses dur['Blank2'] (ms).
        streamer: is a dict with so and so
        win: is the Windows object from foo

    """

    for elem in screens.bTaskWaitCross:
        elem.draw()
    win.flip()
    core.wait(dur.Blank2 / 1000.0)
    TaskTimings.append((expClock.getTime(), f"T{i} WaitingFeedback"))
    if cfg.ws_streaming.lower() == "true":
        streamer.send_event(
            "Preparation to the EPFeedback phase",
            {"event_": "PreEPFeedback", "dur_Prep_EPFeedback": dur.Blank2 / 1000}
            )


def feedback_phase(streamer, i, win, screens, CURSOR, keypr, trials, TaskTimings, expClock, dur, cfg, task=Task, MTF=None, Hz=None):
    """
    Feedback based on mean onset frequency:
      success if (mean(keypr)*Hz)/MTF >= eff_t
      big failure if < 0.7*eff_t, else failure.
    """

    # --- Configuration
    # cfg = parse_args("main")
    
    if trials.loc[i, 'Anticipation_EP'] == 1:
        trials.at[i, 'success'] = -1
        for elem in screens.bAnticip:
            elem.draw()
        TaskTimings.append((expClock.getTime(), f"T{i} FeedbackAnticip"))
        if cfg.ws_streaming.lower() == "true":
            streamer.send_event(
            "EPFeedback",
            {"event_": "EPFeedback", "EPFeedback": int(trials.at[i, 'success']), "dur_EPFeedback": dur.Feedback / 1000}
            )
        win.flip()
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
        core.wait(dur.Feedback / 1000.0)


def pupil_baseline_phase(streamer, win, screens, dur):
    """Cross for pupil baseline recovery. Uses dur['TimeForPupilBaselineBack'] (ms)."""
    for elem in screens.bRectCross:
        elem.draw()
    win.flip()
    core.wait(dur.TimeForPupilBaselineBack / 1000.0)
    for elem in screens.bRectCross:
        elem.draw()
    win.flip()

# class EffortParameters:
#    def __init__(self):
#        self.streamer = some_default_streamer

def effort_phase(
    streamer, i, win, screens, kb, io,
    expClock, dur, MTF, Hz,
    trials, CURSOR, TaskTimings, keypr, cfg, task:Task,
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

    print(f"Trial {i}")
    
    if flag_MultipleKeyPressed != 0:
        hand_positioning_phase(
            streamer, i, win, screens, kb, expClock, dur, trials, TaskTimings,
            flag_MultipleKeyPressed, cfg, io=io
        )

    get_ready_phase(
        streamer, i, win, screens, kb, io, expClock, trials,
        flag_MultipleKeyPressed, KEYBOARD_MODE, TaskTimings, cfg, dur
    )

    if trials.loc[i, 'Anticipation_EP'] == 0:
        effort_production_phase(
            streamer, ['f'], i, win, screens, kb, io, expClock,
            dur, MTF, Hz, trials, CURSOR, TaskTimings, keypr, flag_MultipleKeyPressed, cfg, task
        )

    blank_phase(streamer, win, screens, dur, expClock, TaskTimings, i, cfg)
    
    feedback_phase(streamer, i, win, screens, CURSOR, keypr, trials, TaskTimings, expClock, dur, cfg, task, MTF=MTF, Hz=Hz)       

    pupil_baseline_phase(streamer, win, screens, dur)

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
