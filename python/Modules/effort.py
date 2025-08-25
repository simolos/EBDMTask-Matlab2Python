# -*- coding: utf-8 -*-
# comments in English
from psychopy import core
from keyboard import init_keyboard, poll_keys, clear_events, wait_for_keys
from screens import Screens
from websocket_client import WebSocketClient
import numpy as np

# ======= CONSTANTS ========
KEY_PRESS = 22
KEY_RELEASE = 23
# ==========================


def hand_positioning_phase(i, win, screens, kb, expClock, dur, trials, TaskTimings):
    """
    Display finger-positioning buffer and wait until combo is held long enough.
    Uses dur["TimeAfterPositionRight"] and writes trials.at[i,'KeyPositionTime'].
    """
    for stim in screens.bPosition_fingers:
        stim.draw()
    win.flip()

    t0 = core.getTime()
    trials.at[i, 'KeyPositionTime'] = np.nan  # scalar write in-place

    combo = {'q', 'z', 'e'}
    held_since = None

    while True:
        # English: current time + held keys snapshot (support kb=None)
        tnow = core.getTime()
        held = set()
        if kb and hasattr(kb, "state"):
            held = {key for key, pressed in kb.state.items() if pressed}

        # English: ESC handling
        if 'escape' in held:
            win.close()
            core.quit()
            break

        # English: check posture combo
        if combo.issubset(held):
            if held_since is None:
                held_since = tnow
                trials.at[i, 'KeyPositionTime'] = tnow - t0
            elif (tnow - held_since) > (dur["TimeAfterPositionRight"] / 1000.0):
                TaskTimings.append((tnow - dur["TimeAfterPositionRight"], f"T{i} Hand in Position"))
                break
        else:
            held_since = None
            trials.at[i, 'KeyPositionTime'] = np.nan

        core.wait(0.001)



def all_keys_pressed(combo, kb, win=None):
    """
    English: Check continuously if all keys in combo are currently pressed.
    Returns True if 'combo' subset is held, handles escape.
    """
    held = set()
    if kb and hasattr(kb, "state"):
        held = {key for key, pressed in kb.state.items() if pressed}

    if 'escape' in held:
        if win:
            win.close()
        core.quit()
        return False

    return combo.issubset(held)


def get_ready_phase(i, win, screens, kb, io, expClock, trials,
                    flag_MultipleKeyPressed, KEYBOARD_MODE, TaskTimings):
    """
    Show 'Get ready' screen and detect anticipation during per-trial jitter.
    Reads trials.loc[i,'durPrep_EP'] (ms).
    Writes trials.at[i,'Anticipation_EP'] (0/1).
    Returns bool anticip.
    """

    TaskTimings.append((expClock.getTime(), f"T{i} Get ready"))


    for stim in screens.bGetReadyForEP:
        stim.draw()
    win.flip()

    prepEPClock = core.Clock()
    TaskTimings.append((expClock.getTime(), f"T{i} Prep EP"))

    activeKey = ['f'] if flag_MultipleKeyPressed else ['ctrl']
    anticip = False

    if KEYBOARD_MODE:
        # English: per-trial jitter read from the DF
        row = trials.loc[i]
        dur_prep_ms = int(row.get('durPrep_EP', 1000))

        while prepEPClock.getTime() < (dur_prep_ms / 1000.0):
            events = poll_keys(kb, io)
            # English: if any active key is pressed, it's an anticipation
            if any((getattr(ev, 'key', ev)) in activeKey for ev in events):
                anticip = True
                break
            core.wait(0.001)

    trials.at[i, 'Anticipation_EP'] = int(anticip)
    return anticip


def effort_production_phase(i, win, screens, kb, io, expClock,
                            dur, GV, Hz, trials, CURSOR, TaskTimings,
                            anticip, flag_MultipleKeyPressed):
    """
    Handle Go, key press detection, dynamic bar, and cursor trace storage.
    Uses dur["Task"] and trials.loc[i,'effort']/['reward'].
    Writes trials.at[i,'ReactionTimeEP'] when first valid key press occurs.
    Appends [cursor_pos, i] to CURSOR every frame.
    """
    if anticip:
        return  #  Skip effort phase if anticipation occurred

    flag = True
    clear_events(kb, io)
    EPClock = core.Clock()
    TaskTimings.append((expClock.getTime(), f"T{i} Start EP"))

    key_history = []   # English: release timestamps (s) within last second
    started = False

    clock = core.Clock()
    end_time = clock.getTime() + (dur["Task"] / 1000.0)

    row = trials.loc[i]
    target_effort = float(row['effort'])
    reward_val = float(row['reward'])

    # ensure writable column exists
    if 'ReactionTimeEP' not in trials.columns:
        trials['ReactionTimeEP'] = np.nan

    while clock.getTime() < end_time and flag:
        # draw static layers
        for stim in screens.bGoEP:
            stim.draw()
        for stim in screens.bTaskWait:
            stim.draw()
        #  dynamic overlays
        for stim in screens._create_reward_buffer(reward_val, target_effort):
            stim.draw()
        for stim in screens._create_bar_buffer(target_effort):
            stim.draw()

        t_rel = EPClock.getTime()

        # English: process key events (iohub Keyboard events)
        if kb and hasattr(kb, "getEvents"):
            for ev in kb.getEvents():
                if ev.key == 'escape' and ev.type == KEY_PRESS:
                    win.close()
                    core.quit()
                if ev.key in keys and ev.type == KEY_PRESS:
                    if not started:
                        trials.at[i, 'ReactionTimeEP'] = t_rel
                        started = True
                if ev.key in keys and ev.type == KEY_RELEASE:
                    key_history.append(t_rel)

        #  compute frequency (#releases within last 1 s) and map to [0..1]
        freq = len([t for t in key_history if t_rel - t <= 1.0])
        # (freq/GV - 0.3)/0.7 clamped to [0,1]
        cursor_pos = float(min(max((freq / GV - 0.3) / 0.7, 0.0), 1.0))

        # draw cursor
        for stim in screens._create_cursor_dynamic_buffer(cursor_pos):
            stim.draw()

        # store frame trace (append, do not overwrite CURSOR)
        CURSOR.append([cursor_pos, i])

        #  If multi-key posture must be maintained
        if flag_MultipleKeyPressed:
            flag = all_keys_pressed({'a', 'z', 'e'}, kb, win)
        elif flag is False:
            # if posture broke, still log a fallback sample instead of overwriting CURSOR
            CURSOR.append([0.8 * target_effort, i])

        win.flip()
        core.wait(0.001)


def blank_phase(win, screens, dur, expClock, TaskTimings, i):
    """
    Display cross between EP and feedback. Uses dur["Blank2"].
    """
    for stim in screens.bTaskWaitCross:
        stim.draw()
    win.flip()
    core.wait(dur["Blank2"] / 1000.0)
    TaskTimings.append((expClock.getTime(), f"T{i} WaitingFeedback"))


def feedback_phase(i, win, screens, CURSOR, trials, TaskTimings, expClock, anticip, dur):
    """
    Display feedback according to performance and anticipation.
    Uses dur["Reward"]. Writes trials.at[i,'success'] and respects anticipation.
    """
    #ensure writable columns
    for col in ('success', 'Anticipation_EP'):
        if col not in trials.columns:
            trials[col] = np.nan

    mean_effort = 0.0
    row = trials.loc[i]
    target_effort = float(row['effort'])

    if not anticip:
        #collect this-trial cursor samples
        col_i = [val for (val, idx) in CURSOR if idx == i]
        mean_effort = float(np.nanmean(col_i)) if len(col_i) else 0.0

        if mean_effort >= target_effort:
            trials.at[i, 'success'] = 1
            for stim in screens.bSuccess:
                stim.draw()
            TaskTimings.append((expClock.getTime(), f"T{i} FeedbackSuccess"))

        elif mean_effort < 0.7 * target_effort:
            trials.at[i, 'success'] = -1
            for stim in screens.bFailure:
                stim.draw()
            TaskTimings.append((expClock.getTime(), f"T{i} FeedbackBigFailure"))
        else:
            trials.at[i, 'success'] = 0
            for stim in screens.bFailure:
                stim.draw()
            TaskTimings.append((expClock.getTime(), f"T{i} FeedbackFailure"))

    else:
        trials.at[i, 'Anticipation_EP'] = 1
        trials.at[i, 'success'] = 0  # English: conservative assignment when anticipated
        for stim in screens.bAnticip:
            stim.draw()
        TaskTimings.append((expClock.getTime(), f"T{i} FeedbackAnticip"))

    win.flip()
    core.wait(dur["Reward"] / 1000.0)


def pupil_baseline_phase(win, screens, dur):
    """
    Cross for pupil baseline recovery. Uses dur["TimeForPupilBaselineBack"].
    """
    for stim in screens.bRectCross:
        stim.draw()
    win.flip()
    core.wait(dur["TimeForPupilBaselineBack"] / 1000.0)
    for stim in screens.bRectCross:
        stim.draw()
    win.flip()


def effort_phase(i, win, screens, kb, io,
                 expClock, dur, GV, Hz,
                 trials, CURSOR, TaskTimings,
                 flag_MultipleKeyPressed=False,
                 KEYBOARD_MODE=True):
    """
    Wrapper that runs the effort phase sub-steps for trial i.
    Reads all global durations from 'dur' and per-trial jitter from trials.loc[i,'durPrep_EP'].
    Writes directly into the original 'trials' DataFrame.
    """
    # ensure writable columns exist before writing
    for col in ('EffortProduction', 'KeyPositionTime', 'Anticipation_EP',
                'ReactionTimeEP', 'success'):
        if col not in trials.columns:
            trials[col] = np.nan

    trials.at[i, 'EffortProduction'] = 1

    if flag_MultipleKeyPressed:
        hand_positioning_phase(i, win, screens, kb, expClock, dur, trials, TaskTimings)
        anticip = get_ready_phase(i, win, screens, kb, io, expClock, trials,
                                  flag_MultipleKeyPressed, KEYBOARD_MODE, TaskTimings)
        effort_production_phase([i, win, screens, kb, io, expClock,
                                dur, GV, Hz, trials, CURSOR, TaskTimings,
                                anticip, flag_MultipleKeyPressed)
        blank_phase(win, screens, dur, expClock, TaskTimings, i)
        feedback_phase(i, win, screens, CURSOR, trials, TaskTimings, expClock, anticip, dur)
        pupil_baseline_phase(win, screens, dur)

    else:
        anticip = get_ready_phase(i, win, screens, kb, io, expClock, trials,
                                  flag_MultipleKeyPressed, KEYBOARD_MODE, TaskTimings)
        effort_production_phase(i, win, screens, kb, io, expClock,
                                dur, GV, Hz, trials, CURSOR, TaskTimings,
                                anticip, flag_MultipleKeyPressed)
        blank_phase(win, screens, dur, expClock, TaskTimings, i)
        feedback_phase(i, win, screens, CURSOR, trials, TaskTimings, expClock, anticip, dur)
        pupil_baseline_phase(win, screens, dur)
