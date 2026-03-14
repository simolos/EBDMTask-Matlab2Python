# main.py
# Purpose: Run the full EBDM task (decision-making & effort-production), handle timing, saving, and websocket streaming.

from psychopy import core, visual, monitors, parallel

from data import DataRecorder
from dataclasses import asdict
import numpy as np
import os
from screens import Screens
from general_trial import GetTrialCondition
from config import parse_args, get_task_duration, init_trials, Task, Population, Expe, MRI_trigger_key
from decision import decision_phase
from effort import effort_phase, init_cursor_matrix
from ws_utils import trial_row_payload
from keyboard import init_keyboard, poll_keys, clear_events, QuitSignal
from ws_stream import TrialStreamer
import logging
import traceback
import tempfile
import shutil
import sys
from trigger_and_logs_manager import TriggerCodes, init_triggers
from timing import wait_with_escape
from save_utils import save_and_quit
from display import create_window
from compute_total_gain import compute_total_gain


if __name__ == "__main__":
    # --- Configuration and sanity checks ---
    cfg = parse_args(Task.EBDM, Expe.Standard)
    logging.basicConfig(level=logging.getLevelName(cfg.log_level))

    assert cfg.nTrials > 0, "nTrials must be > 0"
    assert 0 <= cfg.nEffortTrials <= cfg.nTrials, "nEffortTrials must be in [0, nTrials]"
    assert cfg.population in Population, "Population group must be in [1, 2, 3]"

    # Pressed-keys mode: 0=simply tap "Ctrl", 1=hold "A/W/E" and tap "F", 2=hold "Ctrl" and tap "Ctrl"
    flag_MultipleKeyPressed = cfg.mode

    # Mapping of "Yes" side
    flag_MapYesAtRight = (cfg.ChangeMappingYes == 'Y')

    # Trials & durations
    dur = get_task_duration(cfg.eyetracker, cfg.population, Task.EBDM, cfg.experiment)
    cond_er, indx_effort_trials = GetTrialCondition(cfg.nTrials, cfg.nEffortTrials, cfg.population)

    trials = init_trials(
        n_trials=cfg.nTrials, 
        task = Task.EBDM,
        expe = cfg.experiment,
        dur=dur,
        cond_e_r=cond_er
        )

    # --- Data log setup ---
    prefix = f"{cfg.subject_id}_{cfg.block_id}"
    rec = DataRecorder(output_dir=cfg.output_dir, prefix=prefix)

    # --- Websocket setup ---
    streamer = None
    if cfg.ws_streaming.lower() == "true":
        # streamer = TrialStreamer("ws://127.0.0.1:8765/trials")
        streamer = TrialStreamer("ws://192.168.2.200:8765/trials")

        streamer.start()


    # Triggers initialization (HERE I WILL NEED TO DEFINE WHICH TRIGGERS ARE SENT!! EYELINK, MRI, WEBSOCKET, ETC.)
    triggers = init_triggers(cfg)

    # --- PsychoPy window ---
    win, gain_screen = create_window(cfg)

    screens = Screens(win, gain_screen=gain_screen, lang=cfg.language)
    kb, io = init_keyboard()
    expClock = core.Clock()

    TaskTimings = []
    MTF = cfg.MTF
    Hz = win.getActualFrameRate(nIdentical=20, nMaxFrames=200, nWarmUpFrames=10, threshold=1)
    if Hz is None : Hz = 60

    CURSOR, nFrames = init_cursor_matrix(dur.Task, Hz, cfg.nTrials)
    keypr = np.full((nFrames, cfg.nTrials), np.nan, dtype=float)


    # Waiting for start (either MRI trigger or manual start, keypress 5)
    for elem in screens.bWaitingStart:
        elem.draw()
    win.flip()

    while True:
        _ = kb.getKeys(clear=False)  # refresh kb.state
        pressed = {k for k, pressed in getattr(kb, "state", {}).items() if pressed}

        if pressed == MRI_trigger_key:
            print('Keypress 5 detected')

            if triggers is not None: # If keypress 5 was detected, send out TI trigger 
                triggers.send(TriggerCodes.TI)
            break

    # --- Start block (fixation) ---
    for elem in screens.bRectCross:
        elem.draw()
    win.flip()
    wait_with_escape(dur.StartBlock / 1000.0, kb, io)


    TotalGain = None


    try:
        for i in range(cfg.nTrials):
        

            # --- Constant durations to server (small JSON) ---
            # if streamer is not None:
            #     streamer.send_event(
            #     "Intertrial interval sent",
            #     {"event_": "ITI", "DurITI": (trials.ITI[i] / 1000)} 
            #     )
   

            # --- Decision phase ---
            decision_phase(streamer, i, win, screens, kb, io, expClock, dur, trials, triggers, flag_MapYesAtRight, cfg)


            # --- Effort phase (only when scheduled and accepted) ---
            if i in indx_effort_trials and trials.loc[i, 'Acceptance'] == 1:
                print("Entered EP phase")
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
                    triggers=triggers,
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
                {"event_": "ITI", "DurITI": (trials.ITI[i] / 1000)}
                )

            if streamer is not None:
                streamer.send_event(
                "End of the trial",
                {"event_": "EndOfTrial"}
                )

            if trials.loc[i, 'Anticipation_EP'] == 0:


                # Extended intertrial interval 
                for elem in screens.bRectCross:
                    elem.draw()
                win.flip()

                ##### Send out triggers
                if triggers is not None:  
                    triggers.send(TriggerCodes.ITI)

                wait_with_escape((trials.ITI[i]+dur.TimeForPupilBaselineBack) / 1000.0, kb, io)

            else:
                for elem in screens.bRectCross:
                    elem.draw()
                win.flip()

                ##### Send out triggers
                if triggers is not None:  
                    triggers.send(TriggerCodes.ITI)

                wait_with_escape(trials.ITI[i] / 1000.0, kb, io)
                

            # --- Record enriched trial row (Hz, MTF) ---
            trial_dict = trials.loc[i].to_dict()
            trial_dict.update({"Hz": Hz, "MTF": MTF, "mode": cfg.mode})
            trial_dict.update({f"dur_{k}": v for k, v in asdict(dur).items()})
            rec.add_trial(trial_dict)

            print("recorded okay")

        # --- Final feedback UI ---
        
        # Implement here final trigger to the websocket 

        # Compute total gain
        TotalGain = compute_total_gain(trials)
    
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

        if triggers is not None:
            triggers.close()
            trigger_log_df = triggers.get_log_dataframe()
            trigger_log_file = os.path.join(cfg.output_dir, f"{prefix}_triggers.csv")
            trigger_log_df.to_csv(trigger_log_file, index=False)

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
