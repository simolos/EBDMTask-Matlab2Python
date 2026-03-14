## save_utils.py

from psychopy import core
import logging
import os
from pathlib import Path
from data import DataRecorder


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
    all_fmt="xlsx",
    csv_mode="long",
    mode=None,
    durations=None,
):

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