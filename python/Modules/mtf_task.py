# mtf_task.py
# Purpose: Compute the MTF, handle timing and log of behavioral data.

from psychopy import core, visual, monitors

from data import DataRecorder
import numpy as np
import os
from screens import Screens
from general_trial import GetTrialCondition
from config import parse_args, get_task_duration, init_trials
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
    cfg = parse_args("MTF")
    assert cfg.nTrials > 0, "nTrials must be > 0"
    assert cfg.nEffortTrials == cfg.nTrials, "nEffortTrials must be equal to nTrials"
    assert cfg.population in [1, 2, 3], "Population group must be in [1, 2, 3]"

# Pressed-keys mode: 0=simply tap "Ctrl", 1=hold "A/W/E" and tap "F", 2=hold "Ctrl" and tap "Ctrl"
    flag_MultipleKeyPressed = cfg.mode

# Trials & Durations
    dur = get_task_duration(cfg.eyetracker, cfg.population, "MTF")
    trials = init_trials(
        n_trials=cfg.nTrials, 
        dur_prep_ep=dur["EP_Preparation"], 
        task="MTF")

# --- Data log setup ---
    prefix = f"{cfg.subject_id}_{cfg.block_id}"
    rec = DataRecorder(output_dir=cfg.output_dir, prefix=prefix)

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

TotalGain = 0
TaskTimings = []
Hz = win.getActualFrameRate(nIdentical=20, nMaxFrames=200, nWarmUpFrames=10, threshold=1)
if Hz is None : Hz = 60


CURSOR, nFrames = init_cursor_matrix(dur["Task"], Hz, cfg.nTrials)
keypr = np.full((nFrames, cfg.nTrials), np.nan, dtype=float)

# --- Start block (fixation) ---
for elem in screens.bRectCross:
    elem.draw()
win.flip()
wait_with_escape(dur.get('StartBlock', 500) / 1000.0, kb, io)

print("so far so good")