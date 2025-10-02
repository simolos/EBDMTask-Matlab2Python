# mtf_task.py
# Purpose: Compute the MTF, handle timing and log of behavioral data.

from psychopy import core, visual, monitors

from data import DataRecorder
import numpy as np
import os
from screens import Screens
from general_trial import GetTrialCondition
from config import parse_args, get_task_duration, init_trials


def run_mtf_task():
    pass




if __name__ == "__main__":
    # --- Configuration and sanity checks ---
    cfg = parse_args()

# Pressed-keys mode: 0=simply tap "Ctrl", 1=hold "A/W/E" and tap "F", 2=hold "Ctrl" and tap "Ctrl"
    flag_MultipleKeyPressed = cfg.mode

# Trials & Durations
    dur = get_task_duration(cfg.eyetracker, cfg.population)
    


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
