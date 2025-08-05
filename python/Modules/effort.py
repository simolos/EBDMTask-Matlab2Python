from psychopy import core, visual, event
from keyboard import init_keyboard, poll_keys, clear_events, wait_for_keys
from screens import Screens
import numpy as np

#=======CONSTANTS========
KEY_PRESS = 22
KEY_RELEASE = 23
#========================

def hand_positioning_phase(i, win, screens, kb, expClock, TimeAfterPositionRight, trials, TaskTimings):
    """
    Handles the finger positioning buffer and waits until all keys are pressed for required duration.
    """
    for stim in screens.bPosition_fingers:
        stim.draw()
    win.flip()
    t0 = core.getTime()
    trials['KeyPositionTime'][i] = None

    combo = {'a', 'z', 'e'}
    held_since = None

    while True:
        events = kb.getKeys() if kb else []
        tnow = core.getTime()
        held = set([key for key, pressed in kb.state.items() if pressed]) if kb else set()
        # ESCAPE handling
        if kb and 'escape' in held:
            win.close()
            core.quit()
            break

        if combo.issubset(held):
            if held_since is None:
                held_since = tnow
                trials['KeyPositionTime'][i] = tnow - t0
            elif (tnow - held_since) > TimeAfterPositionRight / 1000.0:
                break
        else:
            held_since = None
            trials['KeyPositionTime'][i] = None

        core.wait(0.001)
    TaskTimings.append((expClock.getTime(), f"T{i} Start Hand Position"))

def all_keys_pressed(combo, kb, win=None):
    """
    Constantly verify if the keys are pressed. 
    """
    if kb:
        held = set([key for key, pressed in kb.state.items() if pressed])
    else:
        held = set()
    if 'escape' in held:
        if win:
            win.close()
        core.quit()
        return False
    return combo.issubset(held)



def get_ready_phase(i, win, screens, kb, io, expClock, durPrep_EP, flag_MultipleKeyPressed, KEYBOARD_MODE, trials, TaskTimings):
    """
    Display 'get ready' screen and detect anticipation.
    """
    for stim in screens.bGetReadyForEP:
        stim.draw()
    win.flip()
    prepEPClock = core.Clock()
    TaskTimings.append((expClock.getTime(), f"T{i} Prep EP"))

    activeKey = 'f' if flag_MultipleKeyPressed else 'ctrl'
    anticip = False
    if KEYBOARD_MODE:
        while prepEPClock.getTime() < durPrep_EP / 1000.0:
            events = poll_keys(kb, io)
            if any((ev.key if hasattr(ev, 'key') else ev) == activeKey for ev in events):
                anticip = True
                break
            core.wait(0.001)
    trials['Anticipation_EP'][i] = int(anticip)
    return anticip


def effort_production_phase(keys, i, win, screens, kb, io, expClock, dur_Task, GV, Hz, trials, CURSOR, TaskTimings, anticip, flag_MultipleKeyPressed):
    """
    Effort production: handle Go signal, keypress detection, bar update, and store cursor trace.
    """
    if anticip:
        return  # Skip effort phase if anticipation

    flag = True 
    
    clear_events(kb, io)
    EPClock = core.Clock()
    TaskTimings.append((expClock.getTime(), f"T{i} Start EP"))
    key_history = []
    started = False
    bar_level = trials['effort'][i]

    clock = core.Clock()
    end_time = clock.getTime() + dur_Task / Hz

    while clock.getTime() < end_time and flag:
        # Draw screens
        for stim in screens.bGoEP:
            stim.draw()
        for stim in screens.bTaskWait:
            stim.draw()
        for stim in screens._create_reward_buffer(trials['reward'][i], trials['effort'][i]):
            stim.draw()
        for stim in screens._create_bar_buffer(trials['effort'][i]):
            stim.draw()
        t_rel = EPClock.getTime()
        for ev in kb.getEvents():
            if ev.key == 'escape' and ev.type == KEY_PRESS:
                win.close()
                core.quit()
            if ev.key in keys and ev.type == KEY_PRESS:
                if not started:
                    trials['ReactionTimeEP'][i] = t_rel
                    started = True
            if ev.key in keys and ev.type == KEY_RELEASE:
                key_history.append(t_rel)

        freq = len([t for t in key_history if t_rel - t <= 1.0])
        cursor_pos = float(min(max((freq/GV-0.3)/0.7, 0.0), 1.0))

        for stim in screens._create_cursor_dynamic_buffer(cursor_pos):
            stim.draw()

        CURSOR.append([cursor_pos, i])

        if flag_MultipleKeyPressed:
            flag = all_keys_pressed({'a', 'z', 'e'}, kb, win)
        elif flag==False:
            CURSOR = [0.8*trials['effort'][i], i]

        win.flip()
        core.wait(0.001)


def blank_phase(win, screens, dur_Blank2, expClock, TaskTimings, i):
    """
    Display blank cross between effort and feedback.
    """
    for stim in screens.bTaskWaitCross:
        stim.draw()
    win.flip()
    core.wait(dur_Blank2 / 1000.0)
    TaskTimings.append((expClock.getTime(), f"T{i} WaitingFeedback"))


def feedback_phase(i, win, screens, CURSOR, trials, TaskTimings, expClock, anticip, dur_Reward):
    """
    Display feedback depending on performance and anticipation.
    """
    mean_effort = 0
    if not anticip:
        col_i = [row[0] for row in CURSOR if row[1] == i]
        mean_effort = np.nanmean(col_i)
        if mean_effort >= trials['effort'][i]:
            for stim in screens.bSuccess:
                stim.draw()
            TaskTimings.append((expClock.getTime(), f"T{i} FeedbackSuccess"))
        elif mean_effort < 0.7 * trials['effort'][i]:
            for stim in screens.bFailure:
                stim.draw()
            TaskTimings.append((expClock.getTime(), f"T{i} FeedbackBigFailure"))
        else:
            for stim in screens.bFailure:
                stim.draw()
            TaskTimings.append((expClock.getTime(), f"T{i} FeedbackFailure"))
    else:
        for stim in screens.bAnticip:
            stim.draw()
        TaskTimings.append((expClock.getTime(), f"T{i} FeedbackAnticip"))

    win.flip()
    core.wait(dur_Reward / 1000.0)
    # Store outcome
    trials['success'][i] = (mean_effort >= trials['effort'][i]) and not anticip


def pupil_baseline_phase(win, screens, TimeForPupilBaselineBack):
    """
    Display cross for pupil baseline recovery.
    """
    for stim in screens.bRectCross:
        stim.draw()
    win.flip()
    core.wait(TimeForPupilBaselineBack / 1000.0)
    for stim in screens.bRectCross:
        stim.draw()
    win.flip()


def effort_phase(i, win, screens, kb, io,
                 expClock,
                 durPrep_EP, dur_Task, TimeAfterPositionRight,
                 dur_Blank2, dur_Reward, TimeForPupilBaselineBack,
                 GV, Hz,
                 trials, CURSOR, TaskTimings,
                 flag_MultipleKeyPressed=False,
                 KEYBOARD_MODE=True):
    """
    Main wrapper to run the effort phase, calling each sub-phase.
    """
    clock = core.Clock()
    trials['EffortProduction'][i] = 1

    if flag_MultipleKeyPressed:
        hand_positioning_phase(i, win, screens, kb, expClock, TimeAfterPositionRight, trials, TaskTimings)
        anticip = get_ready_phase(i, win, screens, kb, io, expClock, durPrep_EP, flag_MultipleKeyPressed, KEYBOARD_MODE, trials, TaskTimings)
        effort_production_phase(['f'], i, win, screens, kb, io, expClock, dur_Task, GV, Hz, trials, CURSOR, TaskTimings, anticip, flag_MultipleKeyPressed)
        blank_phase(win, screens, dur_Blank2, expClock, TaskTimings, i)
        feedback_phase(i, win, screens, CURSOR, trials, TaskTimings, expClock, anticip, dur_Reward)
        pupil_baseline_phase(win, screens, TimeForPupilBaselineBack)

    else :
        anticip = get_ready_phase(i, win, screens, kb, io, expClock, durPrep_EP, flag_MultipleKeyPressed, KEYBOARD_MODE, trials, TaskTimings)
        effort_production_phase(['left', 'right'], i, win, screens, kb, io, expClock, dur_Task, GV, Hz, trials, CURSOR, TaskTimings, anticip, flag_MultipleKeyPressed)
        blank_phase(win, screens, dur_Blank2, expClock, TaskTimings, i)
        feedback_phase(i, win, screens, CURSOR, trials, TaskTimings, expClock, anticip, dur_Reward)
        pupil_baseline_phase(win, screens, TimeForPupilBaselineBack)


# --- Test main for effort_phase ---
if __name__ == "__main__":
    # Setup window and components
    win = visual.Window(size=(1280,720), fullscr=False, color=(0.8,0.8,0.8), units='pix')
    screens = Screens(win, gain_screen=1.0)
    kb, io = init_keyboard(use_iohub=False, use_hub=True)
    expClock = core.Clock()

    # Define parameters
    nTrials = 1
    trials = {
        'effort': [0.6] * nTrials,
        'reward': ['20']  * nTrials,
        'EffortProduction': [0] * nTrials,
        'KeyPositionTime': [0] * nTrials,
        'Anticipation_EP': [0] * nTrials,
        'ReactionTimeEP': [0] * nTrials,
        'success': [0] * nTrials
    }

    TaskTimings = []

    # Random durations
    durPrep_EP = 1000
    dur_Task = 5000
    TimeAfterPositionRight = 1000
    dur_Blank2 = 500
    dur_Reward = 2000
    TimeForPupilBaselineBack = 500
    GV = 8.0
    Hz = 1000

    CURSOR = []
    # Run for each trial
    i=0
    effort_phase(
        i, win, screens, kb, io,
        expClock,
        durPrep_EP, dur_Task, TimeAfterPositionRight,
        dur_Blank2, dur_Reward, TimeForPupilBaselineBack,
        GV, Hz,
        trials, CURSOR, TaskTimings
    )

    print("Trials data:", trials)
    print("TaskTimings:", TaskTimings)

    win.close()
    core.quit()
