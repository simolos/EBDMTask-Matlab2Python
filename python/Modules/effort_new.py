# -*- coding: utf-8 -*-
# Purpose: Effort phase subroutines (positioning, get-ready, EP frames, feedback).
from psychopy import core
from keyboard import poll_keys, clear_events
from config import combo
import numpy as np

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
    flag_MultipleKeyPressed, io=None
):
    """
    Show the finger-positioning buffer and wait until the required combo is held
    continuously for dur['TimeAfterPositionRight'] ms.
    Writes trials.at[i,'KeyPositionTime'] (time until first correct pose).
    """
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
                elif (tnow - held_since) > (dur["TimeAfterPositionRight"] / 1000.0):
                    TaskTimings.append((expClock.getTime(), f"T{i} Hand in Position"))
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
                elif (tnow - held_since) > (dur["TimeAfterPositionRight"] / 1000.0):
                    TaskTimings.append((expClock.getTime(), f"T{i} Hand in Position"))
                    streamer.send_event("hand positionning time", {"trial": i + 1, "t": expClock.getTime()})
                    break
            else:
                held_since = None
                trials.at[i, 'KeyPositionTime'] = np.nan

        core.wait(0.001)  # tiny sleep to avoid busy spin


def get_ready_phase(
    streamer, i, win, screens, kb, io, expClock, trials,
    flag_MultipleKeyPressed, KEYBOARD_MODE, TaskTimings
):
    """
    Display 'Get ready' and detect anticipation within the per-trial EP jitter.
    Reads trials.loc[i,'durPrep_EP'] (ms) and writes trials.at[i,'Anticipation_EP'].
    Anticipation logic:
      - mode 2: anticipation on KEY_RELEASE of active key
      - else:   anticipation on KEY_PRESS of active key
    """
    TaskTimings.append((expClock.getTime(), f"T{i} Get ready"))
    for stim in screens.bGetReadyForEP:
        stim.draw()
    win.flip()

    prepEPClock = core.Clock()
    TaskTimings.append((expClock.getTime(), f"T{i} Prep EP"))

    clear_events(kb, io)  # drop any buffered events
    activeKey = 'f' if flag_MultipleKeyPressed == 1 else 'lctrl'
    trials.at[i, 'Anticipation_EP'] = 0

    dur_prep_ms = int(trials.loc[i].get('durPrep_EP', 1000))
    streamer.send_event(
        "Preparation EP start",
        {"trial": i + 1, "durPrepEP [ms]": dur_prep_ms, "t": expClock.getTime()}
    )

    while prepEPClock.getTime() < (dur_prep_ms / 1000.0):
        events = poll_keys(kb, io)  # also catches ESC
        if events:
            for ev in events:
                key_name = ev.key if hasattr(ev, 'key') else ev
                if flag_MultipleKeyPressed == 2:
                    if key_name == activeKey and ev.type == KEY_RELEASE:
                        trials.at[i, 'Anticipation_EP'] = 1
                        streamer.send_event("Anticipation -> True", {"trial": i + 1, "t": expClock.getTime()})
                        break
                else:
                    if key_name == activeKey and ev.type == KEY_PRESS:
                        trials.at[i, 'Anticipation_EP'] = 1
                        streamer.send_event("Anticipation -> True", {"trial": i + 1, "t": expClock.getTime()})
                        break
        core.wait(0.001)


def effort_production_phase(
    streamer, keys, i, win, screens, kb, io, expClock,
    dur, GV, Hz, trials, CURSOR, TaskTimings, keypr, flag_MultipleKeyPressed
):
    """
    EP frame loop:
      - On each frame, set keypr[f,i]=1 if tap onset is detected, else 0.
      - First onset defines ReactionTimeEP.
      - Compute normalized cursor from mean onset rate.
      - Draw EP layers and flip at Hz pace until nFrames.
    """
    # Initial 'Go' frame (time zero)
    target_effort = (float(trials.loc[i, 'effort']) - 0.3) / 0.7
    reward_val = float(trials.loc[i, 'reward'])
    for stim in screens.bTaskWait:
        stim.draw()
    for stim in screens._create_reward_buffer(reward_val, target_effort):
        stim.draw()
    for stim in screens._create_bar_buffer(target_effort):
        stim.draw()
    win.flip()

    EPClock = core.Clock()
    TaskTimings.append((expClock.getTime(), f"T{i} Start EP"))
    streamer.send_event("effort production phase start", {"trial": i + 1, "t": expClock.getTime()})

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
        for stim in screens.bTaskWait:
            stim.draw()
        for stim in screens.bGoEP:
            stim.draw()
        for stim in screens._create_reward_buffer(reward_val, target_effort):
            stim.draw()
        for stim in screens._create_bar_buffer(target_effort):
            stim.draw()

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
        mean_onsets = np.mean(keypr[: f + 1, i]) if f >= 0 else 0.0
        cursor_pos = (((mean_onsets * Hz) / GV) - 0.3) / 0.7
        if cursor_pos < 0:
            cursor_pos = 0
        elif cursor_pos > 1:
            cursor_pos = 1

        CURSOR[f, i] = cursor_pos
        streamer.send_event("effort production phase", {"trial": i + 1, "advancement": cursor_pos})

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


def blank_phase(streamer, win, screens, dur, expClock, TaskTimings, i):
    """Cross between EP and feedback. Uses dur['Blank2'] (ms)."""
    for stim in screens.bTaskWaitCross:
        stim.draw()
    win.flip()
    core.wait(dur["Blank2"] / 1000.0)
    TaskTimings.append((expClock.getTime(), f"T{i} WaitingFeedback"))
    streamer.send_event("Waiting feedback", {"trial": i + 1, "t": expClock.getTime()})


def feedback_phase(streamer, i, win, screens, CURSOR, keypr, trials, TaskTimings, expClock, dur, GV=None, Hz=None):
    """
    Feedback based on mean onset frequency:
      success if (mean(keypr)*Hz)/GV >= eff_t
      big failure if < 0.7*eff_t, else failure.
    """
    if trials.loc[i, 'Anticipation_EP'] == 1:
        trials.at[i, 'success'] = 0
        for stim in screens.bAnticip:
            stim.draw()
        TaskTimings.append((expClock.getTime(), f"T{i} FeedbackAnticip"))
        streamer.send_event("FeedbackAnticip", {"trial": i + 1, "t": expClock.getTime()})
        win.flip()
        core.wait(dur["Reward"] / 1000.0)
        return

    eff_t = float(trials.loc[i, 'effort'])
    mean_onsets = float(np.nanmean(keypr[:, i]))
    tap_rate_norm = ((mean_onsets * Hz) / GV)
    success = 1 if tap_rate_norm >= eff_t else (-1 if tap_rate_norm < 0.7 * eff_t else 0)

    trials.at[i, 'success'] = success
    streamer.send_event("Feedback", {"trial": i + 1, "Result": success, "t": expClock.getTime()})

    if success == 1:
        for stim in screens.bSuccess:
            stim.draw()
        TaskTimings.append((expClock.getTime(), f"T{i} FeedbackSuccess"))
    elif success == -1:
        for stim in screens.bFailure:
            stim.draw()
        TaskTimings.append((expClock.getTime(), f"T{i} FeedbackBigFailure"))
    else:
        for stim in screens.bFailure:
            stim.draw()
        TaskTimings.append((expClock.getTime(), f"T{i} FeedbackFailure"))

    win.flip()
    core.wait(dur["Reward"] / 1000.0)


def pupil_baseline_phase(streamer, win, screens, dur):
    """Cross for pupil baseline recovery. Uses dur['TimeForPupilBaselineBack'] (ms)."""
    for stim in screens.bRectCross:
        stim.draw()
    win.flip()
    core.wait(dur["TimeForPupilBaselineBack"] / 1000.0)
    for stim in screens.bRectCross:
        stim.draw()
    win.flip()


def effort_phase(
    streamer, i, win, screens, kb, io,
    expClock, dur, GV, Hz,
    trials, CURSOR, TaskTimings, keypr,
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
            flag_MultipleKeyPressed, io=io
        )
        get_ready_phase(
            streamer, i, win, screens, kb, io, expClock, trials,
            flag_MultipleKeyPressed, KEYBOARD_MODE, TaskTimings
        )
        if trials.loc[i, 'Anticipation_EP'] == 0:
            effort_production_phase(
                streamer, ['f'], i, win, screens, kb, io, expClock,
                dur, GV, Hz, trials, CURSOR, TaskTimings, keypr, flag_MultipleKeyPressed
            )
    else:
        get_ready_phase(
            streamer, i, win, screens, kb, io, expClock, trials,
            flag_MultipleKeyPressed, KEYBOARD_MODE, TaskTimings
        )
        if trials.loc[i, 'Anticipation_EP'] == 0:
            effort_production_phase(
                streamer, ['f'], i, win, screens, kb, io, expClock,
                dur, GV, Hz, trials, CURSOR, TaskTimings, keypr, flag_MultipleKeyPressed
            )

    blank_phase(streamer, win, screens, dur, expClock, TaskTimings, i)
    feedback_phase(streamer, i, win, screens, CURSOR, keypr, trials, TaskTimings, expClock, dur, GV=GV, Hz=Hz)
    pupil_baseline_phase(streamer, win, screens, dur)
