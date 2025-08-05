from psychopy import core, visual, event
from keyboard import init_keyboard, poll_keys, clear_events, wait_for_keys
from screens import Screens
import numpy as np

#=======CONSTANTS========
KEY_PRESS = 22
KEY_RELEASE = 23
#========================

def effort_phase(i, win, screens, kb, io,
                 expClock,
                 durPrep_EP, dur_Task, TimeAfterPositionRight,
                 dur_Blank2, dur_Reward, TimeForPupilBaselineBack,
                 GV, Hz,
                 trials, CURSOR, TaskTimings,
                 flag_MultipleKeyPressed=True,
                 KEYBOARD_MODE=True):
    """
    Execute the effort-production phase for trial i.
    - Logs all key timings and screen transitions to TaskTimings.
    - Records finger-positioning time, anticipation, reaction time, cursor trace, and success.
    """
    # --- 0. Mark that effort production is required ---
    trials['EffortProduction'][i] = 1

    # --- 1. Finger positioning buffer (event only, no IOHub) ---
    if flag_MultipleKeyPressed:
        # Show the 'Position your fingers' screen
        for stim in screens.bPosition_fingers:
            stim.draw()
        win.flip()
        t0 = core.getTime()
        trials['KeyPositionTime'][i] = None

        # combo of keys to check
        combo = {'a', 'z', 'e'}
        held_since = None

        while True:
            events = kb.getKeys() if kb else []
            tnow = core.getTime()

            # Build the set of currently held keys (only for IOHub)
            held = set([key for key, pressed in kb.state.items() if pressed]) if kb else set()

            # ESCAPE handling (works for IOHub and fallback)
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

    # --- 2. Get ready for effort production ---
    for stim in screens.bGetReadyForEP:
        stim.draw()
    win.flip()
    prepEPClock = core.Clock()
    TaskTimings.append((expClock.getTime(), f"T{i} Prep EP"))

    # EP anticipation (keyboard only)
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

    # --- 3. Effort production itself ---
#    nFrames = int(np.floor(dur_Task / (1000.0/Hz)))
#    CURSOR[:, i] = np.nan
    if not anticip:
        clear_events(kb, io)
        # a) 'Go' screen (one frame)
        """
        for stim in screens.bGoEP:
            stim.draw()
        for stim in screens._create_reward_buffer(trials['reward'][i], trials['effort'][i]):
            stim.draw()
        for stim in screens._create_bar_buffer(trials['effort'][i]):
            stim.draw()
        win.flip()
        """
        EPClock = core.Clock()
        TaskTimings.append((expClock.getTime(), f"T{i} Start EP"))
        
        # Prepare keypress history
        key_history = []  # list of (time) stamps when activeKey pressed
        started = False
#       frame = 0
        bar_level = trials['effort'][i]
        # Loop frames

        """
        while frame < nFrames:
            # draw base task wait buffer
            for stim in screens.bTaskWait:
                stim.draw()
            # overlay reward+target bar
            for stim in screens._create_reward_buffer(trials['reward'][i], trials['effort'][i]):
                stim.draw()
            for stim in screens._create_bar_dynamic_buffer(trials['effort'][i]):
                stim.draw()

            # poll for key
            events = wait_for_keys(['space', 'left', 'right'], 0.1, kb, io)
            t_rel = EPClock.getTime()
            if events[0] is not None:
                key_history.append(t_rel)
                if not started:
                    trials['ReactionTimeEP'][i] = t_rel
                    started = True

            # compute cursor_pos = (keypress_count_per_sec - 0.3)/0.7 / GV
            # here approximate frequency
            freq = len([t for t in key_history if t_rel - t <= 1.0])  # taps in last sec
            #cursor_pos = max((freq/GV-0.3)/(6.0/GV-0.3), 0.0)
            cursor_pos = float(np.clip(freq / 6.0, 0.0, 1.0))
            print(f'freq =  {freq}')
            if cursor_pos < trials['effort'][i]: bar_level -= trials['effort'][i] - cursor_pos
            else : bar_level += cursor_pos - trials['effort'][i]
            print(f'bar =  {bar_level}')
            # draw moving bar        
            if bar_level >=1: bar_level = 1
            elif bar_level <=0 : bar_level = 0

            for stim in screens._create_bar_dynamic_buffer(bar_level):
                stim.draw()
            
            # flip
            win.flip()
            # store
            CURSOR[frame, i] = cursor_pos
            frame += 1
            core.wait(1.0/Hz)
        """

    clock = core.Clock()
    end_time = clock.getTime() + dur_Task/Hz
    print(f'end : {end_time}')
    start_time = clock.getTime()
    started = False
    keys = ['left', 'right', 'space']
    # Use IOHub keyboard events if available
    if io and kb:
        press_time = None
        while clock.getTime() < end_time:  
            print(f'time : {clock.getTime()}')
            # draw Go!!!
            for stim in screens.bGoEP:
                stim.draw()
            # draw base task wait buffer
            for stim in screens.bTaskWait:
                stim.draw()
            # overlay reward+target bar
            for stim in screens._create_reward_buffer(trials['reward'][i], trials['effort'][i]):
                stim.draw()
            for stim in screens._create_bar_buffer(trials['effort'][i]):
                stim.draw()      
            t_rel = EPClock.getTime()
            for ev in kb.getEvents():
                if ev.key == 'escape' and ev.type == KEY_PRESS:
                    win.close()
                    core.quit()
                if ev.key in keys and ev.type == KEY_PRESS and press_time is None:
                    press_time = clock.getTime() 
                    if not started:
                        trials['ReactionTimeEP'][i] = t_rel
                        started = True
                elif ev.key in keys and ev.type == KEY_RELEASE and press_time is not None:
                    key_history.append(t_rel)

            freq = len([t for t in key_history if t_rel - t <= 1.0]) # taps in last sec
            cursor_pos = float(min(max((freq/GV-0.3)/0.7, 0.0), 1.0))
            #cursor_pos = float(np.clip(freq / 10.0, 0.0, 1.0))
            print(f'freq =  {freq}')
            """
            if cursor_pos < trials['effort'][i]: bar_level -= trials['effort'][i] - cursor_pos
            else : bar_level += cursor_pos - trials['effort'][i]
            print(f'bar =  {bar_level}')
            # draw moving bar        
            if bar_level >=1: bar_level = 1
            elif bar_level <=0 : bar_level = 0
            """
            for stim in screens._create_cursor_dynamic_buffer(cursor_pos):
                stim.draw()

            # flip
            win.flip()
            # store
            CURSOR.append([cursor_pos, i])
            core.wait(0.001)

    # --- 4. Inter-phase blank ---
    for stim in screens.bTaskWaitCross:
        stim.draw()
    win.flip()
    core.wait(dur_Blank2 / 1000.0)
    TaskTimings.append((expClock.getTime(), f"T{i} WaitingFeedback"))

    # --- 5. Feedback ---
    if not anticip:
        col_i = [row[i] for row in CURSOR if len(row) > i]  
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

    # --- 6. Pupil baseline recovery ---
    for stim in screens.bRectCross:
        stim.draw()
    win.flip()
    core.wait(TimeForPupilBaselineBack / 1000.0)
    for stim in screens.bRectCross:
        stim.draw()
    win.flip()

    # --- 7. Store outcome ---
    trials['success'][i] = (mean_effort >= trials['effort'][i]) and not anticip

# Note: analog input branch omitted (commented out)

# --- Test main for effort_phase ---
if __name__ == "__main__":
    # Setup window and components
    win = visual.Window(size=(1280,720), fullscr=False, color=(0.8,0.8,0.8), units='pix')
    screens = Screens(win, gain_screen=1.0)
    kb, io = init_keyboard(use_iohub=False, use_hub=True)
    expClock = core.Clock()

    # Define parameters
    nTrials = 2
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
