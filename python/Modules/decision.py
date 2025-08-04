from psychopy import core, visual
from keyboard import init_keyboard, poll_keys, clear_events
from screens import Screens


def decision_phase(i, win, screens, kb, io,
                   expClock,
                   durPrep_DM, dur_DM, TimeAfterDMade,
                   reward_t, eff_t,
                   trials, TaskTimings):
    """
    Execute the decision phase for trial i using the dynamic buffer builder.
    """

    # --- 0. Reset variables ---
    resp = -1
    posi = 0
    DecisionMadeFlag = False
    TriggerFlag = False
    choice = None
    trials['Anticipation_DM'][i] = 0

    # --- 1. Preparation (bDMcross) ---
    for stim in screens.bDMcross:
        stim.draw()
    win.flip()
    prepClock = core.Clock()

    # continuous anticipation detection
    while prepClock.getTime() < durPrep_DM / 1000.0:
        events = poll_keys(kb, io)
        for ev in events:
            key_name = ev.key if hasattr(ev, 'key') else ev
            if key_name in ['left', 'right'] and trials['Anticipation_DM'][i] == 0:
                trials['Anticipation_DM'][i] = 1
                TaskTimings.append((expClock.getTime(), f"T{i} Anticipation DM"))
        core.wait(0.001)
    TaskTimings.append((expClock.getTime(), f"T{i} Prep DM"))


    # --- 2. Decision making (frame-by-frame) ---
    clear_events(kb, io)
    decClock = core.Clock()
    tt2 = decClock.getTime()

    while decClock.getTime() - tt2 < dur_DM / 1000.0:
        # draw dynamic decision buffer
        elems = screens._create_decision_dynamic_buffer(
            effort_level=eff_t,
            rew_t=reward_t,
            choice=choice
        )
        for stim in elems:
            stim.draw()
        win.flip()

        # log Start DM once
        if not TriggerFlag:
            TaskTimings.append((expClock.getTime(), f"T{i} Start DM"))
            TriggerFlag = True

        # poll for key press
        events = poll_keys(kb, io)
        for ev in events:
            key_name = ev.key if hasattr(ev, 'key') else ev
            if not DecisionMadeFlag and key_name in ['left', 'right', 'q']:
                if key_name == 'left':
                    resp = 1
                    ttresp = decClock.getTime()
                    choice = "yes"
                    TaskTimings.append((expClock.getTime(), f"T{i} Decided Yes"))
                    DecisionMadeFlag = True
                elif key_name == 'right':
                    resp = 0
                    ttresp = decClock.getTime()
                    choice = "no"
                    TaskTimings.append((expClock.getTime(), f"T{i} Decided No"))
                    DecisionMadeFlag = True
                elif key_name == 'q':
                    # full cleanup if needed:
                    # stoppsych(); stopcosy(); EyeLink_Close()
                    win.close()
                    core.quit()

        # break 1s after response
        if DecisionMadeFlag and (decClock.getTime() - ttresp) > TimeAfterDMade / 1000.0:
            break

        core.wait(0.001)

    # --- 3. Record results ---
    if resp == -1:
        trials['DecisionTime'][i] = float('nan')
        trials['Acceptance'][i]   = -1
    else:
        trials['DecisionTime'][i] = ttresp - tt2
        trials['Acceptance'][i]   = resp

# --- 4. Test main ---
if __name__ == "__main__":
    # Setup for testing
    win = visual.Window(size=(1280,720), fullscr=False, color=(0.8,0.8,0.8), units='pix')
    screens = Screens(win, gain_screen=1.0)
    kb, io = init_keyboard(use_iohub=True)
    expClock = core.Clock()

    # Prepare minimal trials structure for one trial
    trials = {
        'Anticipation_DM': [0],
        'DecisionTime': [None],
        'Acceptance': [None]
    }
    TaskTimings = []

    # Example parameters
    durPrep_DM     = 1000  # ms
    dur_DM         = 4000  # ms
    TimeAfterDMade = 1000  # ms
    rew_t          = 20    # cents
    eff_t          = 0.8   # 0-1 scale

    # Run the decision phase for trial 0
    decision_phase(
        0, win, screens, kb, io,
        expClock,
        durPrep_DM, dur_DM, TimeAfterDMade,
        rew_t, eff_t,
        trials, TaskTimings
    )

    # Output results
    print("Trials:", trials)
    print("TaskTimings:", TaskTimings)

    # Clean up
    win.close()
    core.quit()
