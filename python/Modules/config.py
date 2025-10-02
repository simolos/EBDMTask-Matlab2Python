# config.py
# Purpose: CLI parsing, task durations per population, and trial table initialization.

import argparse
import numpy as np
import pandas as pd
from datetime import datetime


def parse_args():
    """Parse CLI arguments and return a populated argparse.Namespace."""
    parser = argparse.ArgumentParser(description="Experiment configuration for EBDMTask")

    # --- Core identifiers and I/O ---
    parser.add_argument(
        "-s", "--subject-id", type=str, required=True,
        help="Participant identifier (e.g., S01)"
    )
    parser.add_argument(
        "-b", "--block-id", type=str, required=True,
        help="Block identifier"
    )

    parser.add_argument(
        "-mtf", "--MTF", type=int, required=True,
        help="Participant maximum taping frequency"
    )

    parser.add_argument(
        "-o", "--output_dir", default="results",
        help="Directory where logs/files are written"
    )

    # --- Websocket streaming ---
    parser.add_argument(
        "-ws", "--ws_streaming", type=str,
        choices=["true", "false"],
        default="false",
        help="Enable or disable Websocket streaming (default: false)"
    )

    # --- Localization and stimulation ---
    parser.add_argument(
        "-l", "--language", type=str, default="en", choices=["en", "fr"],
        help="Experiment language"
    )
    parser.add_argument(
        "-t", "--stimulation", type=str, default="none",
        help="Type of stimulation (e.g., none, tms)"
    )

    # --- Design parameters ---
    parser.add_argument(
        "-n", "--nTrials", type=int, default=32,
        help="Number of trials in block (should be a multiple of 16)"
    )
    parser.add_argument(
        "-e", "--nEffortTrials", type=int, default=8,
        help="Number of effort trials in block"
    )
    parser.add_argument(
        "-p", "--population", type=int, default=1,
        help="Population group (1, 2, or 3): 1=healthy, 2=old, 3=patient"
    )

    # --- Flags / modes ---
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--eyetracker", action="store_true", help="Enable eye-tracker")
    parser.add_argument("--test-dev", action="store_true", help="Enable test/dev mode")
    parser.add_argument(
        "-m", "--mode", type=int, default=0, choices=[0, 1, 2],
        help="Pressed-keys mode: 0=simple Ctrl, 1=hold A/W/E + tap F, 2=hold ctrl + tap ctrl"
        # NOTE: '2' kept for backward compatibility; currently unused in Matlab reference.
    )
    parser.add_argument(
        "-chmap", "--ChangeMappingYes", type=str, default="N", choices=["N", "Y"],
        help="Map 'Yes' to the right side (Y) or keep default (N)"
    )
    parser.add_argument(
        "-fullscr", "--fullscreen", type=str, default="N", choices=["N", "Y"],
        help="Fullscreen window (Y) or windowed mode (N)"
    )

    args = parser.parse_args()

    # Attach timestamp and output prefix (used when saving results)
    args.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    args.output_prefix = f"{args.subject_id}_{args.timestamp}"
    return args


# --- UI constants ---
keys_choice = ["left", "right"]  # Selection keys: [left]=Yes, [right]=No
combo = {"q", "z", "e"}          # Finger position combo (display only)


# --- Translations dictionary ---
TRANSLATIONS = {
    "fr": {
        "yes": "Oui",
        "no": "Non",
        "success": "Succès !",
        "failure": "Raté !",
        "ready": "Préparez-vous",
        "effort_perceived": "Effort perçu",
        "no_effort": "Pas d'effort",
        "max_effort": "Effort maximum",
        "press": "Pressez",
        "fingers": "-".join(sorted(combo)).upper(),
        "failed_try": "Raté ! Veuillez essayer à nouveau",
        "anticip": "Anticipé !",
        "rest": "Repos",
        "go": "Go!!!",
        "end_task": "Fin de la tâche",
        "get_effort_note": "Veuillez noter la perception de votre effort...",
        "reward_question": "La récompense en vaut-elle l'effort ?",
        "total": "Total = {val} CHF",
        # --- dynamiques ---
        "reward_for": "Pour {val} cents",
        "reward_plus": "+ {val} cents",
        "reward_minus": "- {val} cents",
    },
    "en": {
        "yes": "Yes",
        "no": "No",
        "success": "Success!",
        "failure": "Failure!",
        "ready": "Get ready",
        "effort_perceived": "Effort perceived",
        "no_effort": "No effort at all",
        "max_effort": "Maximum effort",
        "press": "Press",
        "fingers": "-".join(sorted(combo)).upper(),
        "failed_try": "Failure! Please repeat the trial",
        "anticip": "Anticipated",
        "rest": "Rest",
        "go": "Go!!!",
        "end_task": "End of task",
        "get_effort_note": "Please rate your perceived effort...",
        "reward_question": "Is the reward worth the effort?",
        "total": "Total = {val} CHF",
        # --- dynamics ---
        "reward_for": "For {val} cents",
        "reward_plus": "+ {val} cents",
        "reward_minus": "- {val} cents",
    },
}


# get_task_duration.py
def get_task_duration(flag_eyetracker: int, flag_population: int) -> dict:
    """Return a dict of per-phase durations (ms) based on population and eyetracker flag."""
    dur = {}

    if flag_population == 1:  # Healthy
        dur["Blank1"] = 2000
        dur["DM_Preparation"] = [1000, 1400]
        dur["DM"] = 4000
        dur["TimeAfterDMade"] = 1000
        dur["TimeAfterPositionRight"] = 1000
        dur["GetReadyForEP"] = 1000
        dur["EP_Preparation"] = [1000, 1400]
        dur["Task"] = 8000
        dur["Blank2"] = 500
        dur["Reward"] = 1000
        dur["TimeForPupilBaselineBack"] = 2000 if flag_eyetracker == 1 else 2000
        dur["FinalFeedback"] = 4000
        dur["StartBlock"] = 500

    elif flag_population == 2:  # Old
        dur["Blank1"] = 2000
        dur["DM_Preparation"] = [1000, 1400]
        dur["DM"] = 6000
        dur["TimeAfterDMade"] = 1000
        dur["TimeAfterPositionRight"] = 1000
        dur["GetReadyForEP"] = 1000
        dur["EP_Preparation"] = [1800, 2200]
        dur["Task"] = 6000
        dur["Blank2"] = 500
        dur["Reward"] = 1000
        dur["TimeForPupilBaselineBack"] = 2000 if flag_eyetracker == 1 else 2000
        dur["FinalFeedback"] = 4000
        dur["StartBlock"] = 500

    elif flag_population == 3:  # DBS implanted
        dur["Blank1"] = 2000
        dur["DM_Preparation"] = [1000, 1400]
        dur["DM"] = 6000
        dur["TimeAfterDMade"] = 1000
        dur["TimeAfterPositionRight"] = 1000
        dur["GetReadyForEP"] = 1000
        dur["EP_Preparation"] = [1800, 2200]
        dur["Task"] = 6000
        dur["Blank2"] = 500
        dur["Reward"] = 1000
        dur["TimeForPupilBaselineBack"] = 2000 if flag_eyetracker == 1 else 2000
        dur["FinalFeedback"] = 4000
        dur["StartBlock"] = 500

    return dur


def init_trials(n_trials, cond_e_r, dur_prep_dm, dur_prep_ep):
    """Create the trial table (pandas.DataFrame) mirroring the Matlab structure."""
    trials = pd.DataFrame({
        "trial": np.arange(1, n_trials + 1),                       # Trial index
        "effort": cond_e_r[:, 0],                                  # Nominal effort
        "efftested": cond_e_r[:, 0].copy(),                        # Presented effort
        "rewtested": cond_e_r[:, 1].copy(),                        # Presented reward
        "reward": cond_e_r[:, 1],                                  # Nominal reward
        "DecisionTime": np.full(n_trials, np.nan),                 # Decision time
        "ReactionTimeEP": np.full(n_trials, np.nan),               # Reaction time (EP)
        "Acceptance": np.full(n_trials, np.nan),                   # 1/0/-1
        "EffortProduction": np.full(n_trials, np.nan),             # 1 if produced
        "durPrep_DM": np.random.randint(                           # Prep DM duration (ms)
            low=int(dur_prep_dm[0]),
            high=int(dur_prep_dm[1]) + 1,
            size=n_trials
        ),
        "durPrep_EP": np.random.randint(                           # Prep EP duration (ms)
            low=int(dur_prep_ep[0]),
            high=int(dur_prep_ep[1]) + 1,
            size=n_trials
        ),
        "success": np.full(n_trials, np.nan),                      # 1/0/-1
        "Anticipation_EP": np.full(n_trials, np.nan),              # Bool or NaN
        "Anticipation_DM": np.zeros(n_trials),                     # Bool (0/1)
        "KeyPositionTime": np.full(n_trials, np.nan),              # Posture time
    })
    return trials
