# main.py
# Purpose: Run the full EBDM-like task (decision + effort), handle timing, saving, and websocket streaming.

from psychopy import core, visual, monitors

from data import DataRecorder
from dataclasses import asdict
import numpy as np
import os
from screens import Screens
from general_trial import GetTrialCondition
from config import parse_args, get_task_duration, init_trials, Task, Population
from decision import decision_phase
from effort import effort_phase, init_cursor_matrix
from ws_utils import trial_row_payload
from keyboard import init_keyboard, poll_keys, clear_events, QuitSignal
from ws_stream import TrialStreamer
import logging
import traceback
import tempfile
import shutil

# --- Helper: wait while still catching ESC (polling) ---
def wait_with_escape(seconds, kb, io):
    """Busy-wait while polling keys so ESC/QuitSignal is honored during waits."""
    end_t = core.getTime() + float(seconds)
    while core.getTime() < end_t:
        _ = poll_keys(kb, io)  # ensures QuitSignal can propagate
        core.wait(0.001)

def save_and_quit(
    win,
    rec,
    outdir,
    prefix,
    CURSOR,
    keypr,
    TaskTimings,
    Hz,
    MTF,
    trials=None,
    TotalGain=None,
    all_fmt="xlsx",   # choose: "csv" | "xlsx" | "mat"
    csv_mode="long",  # currently only "long" is implemented
    mode=None,        
    durations=None,    
):
    """
    Centralized save & shutdown.
    - Tries to save in `outdir`.
    - If it fails (permissions, invalid path, etc.), fallback to a safe temp dir.
    - Always closes the window and quits PsychoPy.
    """
    save_path = None
    try:
        try:
            os.makedirs(outdir, exist_ok=True)
            save_path = rec.save_all(
                fmt=all_fmt,
                trials_df=trials,
                cursor=CURSOR,
                keypr=keypr,
                tasktimings=TaskTimings,
                Hz=Hz,
                MTF=MTF,
                TotalGain=TotalGain,
                csv_mode=csv_mode,
                mode=mode,                
                durations=durations, 
            )
        except Exception as e:
            logging.error(f"❌ Failed to save in {outdir}: {e}")
            fallback_dir = Path("./session_data_fallback")
            try:
                fallback_dir.mkdir(parents=True, exist_ok=True)
                logging.warning(f"⚠️ Falling back to {fallback_dir}")
                # Create a temporary recorder in fallback dir
                fb_rec = DataRecorder(output_dir=str(fallback_dir), prefix=prefix)
                save_path = fb_rec.save_all(
                    fmt=all_fmt,
                    trials_df=trials,
                    cursor=CURSOR,
                    keypr=keypr,
                    tasktimings=TaskTimings,
                    Hz=Hz,
                    MTF=MTF,
                    TotalGain=TotalGain,
                    csv_mode=csv_mode,
                )
            except Exception as e2:
                logging.critical(f"🚨 Failed to save even in fallback dir: {e2}")
    finally:
        try:
            if win:
                win.close()
        finally:
            core.quit()
    return save_path


if __name__ == "__main__":
    # --- Configuration and sanity checks ---
    cfg = parse_args(Task.EBDM)
    logging.basicConfig(level=logging.getLevelName(cfg.log_level))

    assert cfg.nTrials > 0, "nTrials must be > 0"
    assert 0 <= cfg.nEffortTrials <= cfg.nTrials, "nEffortTrials must be in [0, nTrials]"
    assert cfg.population in Population, "Population group must be in [1, 2, 3]"

    # Pressed-keys mode: 0=simply tap "Ctrl", 1=hold "A/W/E" and tap "F", 2=hold "Ctrl" and tap "Ctrl"
    flag_MultipleKeyPressed = cfg.mode

    # Mapping of "Yes" side
    flag_MapYesAtRight = (cfg.ChangeMappingYes == 'Y')

    # Trials & durations
    dur = get_task_duration(cfg.eyetracker, cfg.population, Task.EBDM)
    cond_er, indx_effort_trials = GetTrialCondition(cfg.nTrials, cfg.nEffortTrials, cfg.population)
    trials = init_trials(
        n_trials=cfg.nTrials, 
        cond_e_r=cond_er, 
        dur_prep_dm=dur.DM_Preparation, 
        dur_prep_ep=dur.EP_Preparation, 
        task = Task.EBDM)

    # --- Data log setup ---
    prefix = f"{cfg.subject_id}_{cfg.block_id}"
    rec = DataRecorder(output_dir=cfg.output_dir, prefix=prefix)

    # --- Websocket setup ---
    streamer = None
    if cfg.ws_streaming.lower() == "true":
        # streamer = TrialStreamer("ws://127.0.0.1:8765/trials")
        streamer = TrialStreamer("ws://192.168.2.200:8765/trials")

        streamer.start()

    # --- PsychoPy window ---
    mon = monitors.Monitor('MyMonitor')
    if cfg.fullscreen == 'Y':
        win = visual.Window(monitor=mon, fullscr=True, color=(0.8, 0.8, 0.8), units='pix')
        gain_screen = 2
    else:
        win = visual.Window(size=(1280, 720), monitor=mon, fullscr=False, color=(0.8, 0.8, 0.8), units='pix')
        gain_screen = 1

    screens = Screens(win, gain_screen=gain_screen, lang=cfg.language)
    kb, io = init_keyboard()
    expClock = core.Clock()

    TaskTimings = []
    MTF = cfg.MTF
    Hz = win.getActualFrameRate(nIdentical=20, nMaxFrames=200, nWarmUpFrames=10, threshold=1)
    if Hz is None : Hz = 60

    CURSOR, nFrames = init_cursor_matrix(dur.Task, Hz, cfg.nTrials)
    keypr = np.full((nFrames, cfg.nTrials), np.nan, dtype=float)

    # --- Start block (fixation) ---
    for elem in screens.bRectCross:
        elem.draw()
    win.flip()
    wait_with_escape(dur.StartBlock / 1000.0, kb, io)


    try:
        for i in range(cfg.nTrials):
            # --- Send current trial subset (compact payload) ---
            trial_dict = trials.loc[i].to_dict()
            rec.add_trial(trial_dict)
            # include = ["trial", "efftested", "rewtested"]
            # payload = trial_row_payload(trials, i, include, drop_none=True)

            # if streamer is not None:
            #     print("streamer is not None!!!")
            #     streamer.send_event("trial_record", payload)


            # --- Inter-trial cross ---
            for elem in screens.bRectCross:
                elem.draw()
            win.flip()

            # --- Constant durations to server (small JSON) ---
            if streamer is not None:
                streamer.send_event(
                "Intertrial interval sent",
                {"event_": "ITI", "DurITI": (dur.Blank1 / 1000)} 
                )

            wait_with_escape(dur.Blank1 / 1000.0, kb, io)



            # --- Decision phase ---
            print("Entering decision phase")
            decision_phase(streamer, i, win, screens, kb, io, expClock, dur, trials, TaskTimings, flag_MapYesAtRight, cfg)
            print("Exiting decision phase")

            # --- Effort phase (only when scheduled and accepted) ---
            if i in indx_effort_trials and trials.loc[i, 'Acceptance'] == 1:
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
                    task = Task.EBDM,
                    flag_MultipleKeyPressed=flag_MultipleKeyPressed,
                    KEYBOARD_MODE=True,
                )

            # --- Constant durations to server (small JSON) ---
            if streamer is not None:
                streamer.send_event(
                "Intertrial interval sent",
                {"event_": "ITI", "DurITI": (dur.Blank1 / 1000)}
                )

            if streamer is not None:
                streamer.send_event(
                "End of the trial",
                {"event_": "EndOfTrial"}
                )
                

            # --- Record enriched trial row (Hz, MTF) ---
            trial_dict = trials.loc[i].to_dict()
            trial_dict.update({"Hz": Hz, "MTF": MTF, "mode": cfg.mode})
            print("before potential error")
            trial_dict.update({f"dur_{k}": v for k, v in asdict(dur).items()})
            rec.add_trial(trial_dict)

            print("recorded okay")

        # --- Final feedback UI ---
        
        # Implement here final trigger to the websocket 

        # Compute total gain
        mask = (
            ((trials['Acceptance'] == 1) & (trials['EffortProduction'].fillna(0) == 0))
            | ((trials['Acceptance'] == 1) & (trials['EffortProduction'].fillna(0) == 1) & (trials['success'].fillna(0) == 1))
        )
        TotalGain = trials.loc[mask, 'reward'].sum() / 100
    
        for elem in screens.bRectCross:
            elem.draw()
        win.flip()
        for elem in screens._create_ffeedback_buffer(float(TotalGain)):
            elem.draw()
        win.flip()
        wait_with_escape(dur.FinalFeedback / 1000.0, kb, io)

    except QuitSignal:
        print("Exit by 'ESC'")
        logging.info("Quit requested by user (ESC/Q). Saving and exiting...")
    except SystemExit as e:
        # ESC or core.quit() raises SystemExit; still save
        print(f"[SystemExit] code={getattr(e, 'code', None)}")
        logging.info("Early termination (SystemExit). Saving data...")
    except Exception as e:
        tb = traceback.format_exc()
        print("[Exception] Unhandled error:\n", tb)
        logging.exception(f"Unhandled error; saving data anyway: {e}")
    finally:
        # Always close streamer and save data
        if streamer is not None:
            streamer.close()
        save_and_quit(
            win=win,
            rec=rec,
            outdir=cfg.output_dir,
            prefix=prefix,
            CURSOR=CURSOR,
            keypr=keypr,
            TaskTimings=TaskTimings,
            Hz=Hz,
            MTF=MTF,
            trials=trials,
            TotalGain=TotalGain,
            all_fmt="mat",  # or "mat" or "csv"
            mode=cfg.mode,     
            durations=asdict(dur),      
        )
