#main.py
from psychopy import core, visual
from data import DataRecorder
import numpy as np
import pandas as pd
import os 
from screens import Screens
from general_trial import GetTrialCondition
from config import parse_args, get_task_duration, init_trials
from decision import decision_phase
from effort_new  import effort_phase, init_cursor_matrix
from keyboard import init_keyboard, poll_keys, clear_events, QuitSignal
from ws_utils import WSRunner
import logging

def calibration(win, screens, kb, io, expClock):

    clock = core.Clock()
    t0 = clock.getTime()
    t1 = 0
    endTime = 3000
    tap_key = 'lctrl'
    count = 0

    while clock.getTime() - t0 < endTime/1000:
        for elem in screens.bCalib:
            elem.draw()
        win.flip()

        events=poll_keys(kb, io)
        for ev in events:
            key_name = ev.key if hasattr(ev, 'key') else ev
            if key_name == tap_key and t1 == 0:
                count +=1
                t1 = clock.getTime()
            elif  key_name == tap_key and t1 != 0:
                count += 1
            elif key_name == 'escape' :
                win.close()
                core.quit()
    
    GV = count/(endTime/1000-t1) * 0.95
    print(f' GV : {GV}')

    return GV

def save_and_quit(
    win,
    rec,
    outdir,
    prefix,
    CURSOR,
    keypr,
    TaskTimings,
    Hz,
    GV,
    trials=None,
    all_fmt="xlsx",         # <-- choose: "csv" | "xlsx" | "mat"
    csv_mode="long",        # currently only "long" is implemented
):
    """Save everything into ONE file then quit cleanly."""
    try:
        os.makedirs(outdir, exist_ok=True)
        # One-file export (choose fmt here or pass via cfg)
        rec.save_all(
            fmt=all_fmt,
            trials_df=trials,
            cursor=CURSOR,
            keypr=keypr,
            tasktimings=TaskTimings,
            Hz=Hz,
            GV=GV,
            csv_mode=csv_mode,
        )
    finally:
        try:
            if win:
                win.close()
        finally:
            core.quit()


if __name__ == "__main__":

    # Variables configuration
    cfg = parse_args()            
        
    assert cfg.nTrials > 0, "nTrials must be > 0"
    assert 0 <= cfg.nEffortTrials <= cfg.nTrials, "nEffortTrials must be in [0, nTrials]"  
    assert cfg.population in [1, 2, 3], "Population group must be in [1, 2, 3]"

    flag_MultipleKeyPressed = False
    flag_InvYesNo = False
    if cfg.multiplekeyspressed == 'Y': flag_MultipleKeyPressed = True
    dur = get_task_duration(cfg.eyetracker, cfg.population)
    cond_er, indx_effort_trials = GetTrialCondition(cfg.nTrials, cfg.nEffortTrials, cfg.population)
    trials = init_trials(cfg.nTrials, cond_er, dur["DM_Preparation"], dur["EP_Preparation"])

    # Data recorder initialisation
    prefix = f"{cfg.subject_id}_{cfg.block_id}"
    rec = DataRecorder(output_dir=cfg.output_dir, prefix=prefix)

    """
    # Websocket initialisation 

    ws_uri = getattr(cfg, "ws_uri", "ws://localhost:8765")

    def on_ws_msg(msg: dict):
        # Optional: react to server messages (debug/log/state updates)
        logging.info(f"[WS<-] {msg}")

    ws = WSRunner(ws_uri, on_message=on_ws_msg)
    ws.start()
    """

    # Window psychopy configuration
    win = visual.Window(size=(1280,720), fullscr=False, color=(0.8,0.8,0.8), units='pix')
    screens = Screens(win, gain_screen=1.0,lang=cfg.language)
    kb, io = init_keyboard(use_iohub=True)
    expClock = core.Clock()
    TotalGain=0
    i=1
    TaskTimings = []
    GV = 11     #calibration(win, screens, kb, io, expClock)
    Hz = 60
    CURSOR, nFrames = init_cursor_matrix(dur["Task"], Hz, cfg.nTrials)
    keypr = np.full((nFrames, cfg.nTrials), np.nan, dtype=float)

    """
    # Send experiment configuration
    ws.send("session_started", {
        "subject": getattr(cfg, "subject", "SXX"),
        "n_trials": int(cfg.nTrials),
        "n_effort_trials": int(cfg.nEffortTrials),
        "population": int(cfg.population),
        "language": cfg.language,
    })
    """

    for elem in screens.bRectCross:
        elem.draw()
    win.flip()
    core.wait(int(dur.get('StartBlock', 500) / 1000))
    
    try:
        for i in range(cfg.nTrials):
            # --- Inter-trial cross ---
            for elem in screens.bRectCross:
                elem.draw()
            win.flip()
            core.wait(int(dur.get('Blank1', 2000) / 1000))

            # --- Decision ---
            decision_phase(i, win, screens, kb, io, expClock, dur, trials, TaskTimings, flag_InvYesNo)

            # --- Effort (if needed) ---
            if i in indx_effort_trials and trials.loc[i, 'Acceptance'] == 1:
                effort_phase(
                    i, win, screens, kb, io, expClock, dur, GV, Hz,
                    trials, CURSOR, TaskTimings, keypr,
                    flag_MultipleKeyPressed, KEYBOARD_MODE=True
                )
                if trials.loc[i, 'Anticipation_EP'] == 0:
                    TotalGain += trials.loc[i, 'reward'] * trials.loc[i, 'success']

            # --- Record current trial row ---
            trial_dict = trials.loc[i].to_dict()
            trial_dict.update({"Hz": Hz, "GV": GV})
            rec.add_trial(trial_dict)

        # --- Final feedback (optional UI before saving) ---
        for elem in screens.bRectCross:
            elem.draw()
        win.flip()
        for elem in screens._create_ffeedback_buffer(float(TotalGain / 100)):
            elem.draw()
        win.flip()
        core.wait(int(dur.get('FinalFeedback', 4000) / 1000))

    except QuitSignal:
        logging.info("Quit requested by user (ESC/Q). Saving and exiting...")
    except SystemExit:
        # ESC or core.quit() raises SystemExit; we still want to save
        logging.info("Early termination (SystemExit). Saving data...")
    except Exception as e:
        logging.exception(f"Unhandled error; saving data anyway: {e}")
    finally:
        # Centralized save & close (always runs)
        save_and_quit(
            win=win,
            rec=rec,
            outdir=cfg.output_dir,
            prefix=prefix,
            CURSOR=CURSOR,
            keypr=keypr,
            TaskTimings=TaskTimings,
            Hz=Hz,
            GV=GV,
            trials=trials,
            all_fmt="xlsx",     # or "mat" or "csv"
        )

