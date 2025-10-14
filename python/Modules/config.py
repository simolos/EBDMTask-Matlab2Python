# config.py
# Purpose: CLI parsing, task durations per population, and trial table initialization.

import argparse
import numpy as np
import pandas as pd
from datetime import datetime
import sys

from dataclasses import dataclass

from enum import Enum, auto

class Task(Enum):
    EBDM = auto()
    MTF = auto()


class Population(Enum):
    Healthy = "Healthy"
    Old = "Old"
    DBS = "DBS"


@dataclass
class Duration:
    Blank1 = None
    DM_Preparation = None
    DM = None
    TimeAfterDMade = None
    TimeAfterPositionRight = None
    GetReadyForEP = None
    EP_Preparation = None
    Task = None
    Blank2 = None
    Feedback = None
    TimeForPupilBaselineBack = None 
    FinalFeedback = None
    StartBlock = None


def parse_args(task:Task):
    """Parse CLI arguments and return a populated argparse.Namespace."""
    parser = argparse.ArgumentParser(description="Experiment configuration for EBDMTask")

    # --- Core identifiers---
    parser.add_argument(
        "-s", "--subject-id", type=str, required=True,
        help="Participant identifier (e.g., S01)"
    )

    # --- Language ---
    parser.add_argument(
        "-l", "--language", type=str, default="en", choices=["en", "fr"],
        help="Experiment language"
    )

    # --- Population ---
    parser.add_argument(
        "-p", "--population", type=Population, choices=list(Population), default="Healthy",
        help=f"Population group {[f'{p.value}' for p in Population]}"
    )

    # --- Directory behavioral log
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
    
    # --- Eyelink ---
    parser.add_argument("--eyetracker", action="store_true", help="Enable eye-tracker")

    # --- TI triggers ---
    parser.add_argument(
        "-t", "--stimulation", type=str, default="none",
        help="Type of stimulation (e.g., none, tms)"
    )

    # --- Full Screen ---
    parser.add_argument(
        "-fullscr", "--fullscreen", type=str, default="N", choices=["N", "Y"],
        help="Fullscreen window (Y) or windowed mode (N)"
    )

     # --- Flags / modes ---
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
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

    if task == Task.EBDM:

        # --- Block name ---
        parser.add_argument(
            "-b", "--block_id", type=str, required=True,
            help="Block identifier"
        )  

        # --- Maximum tapping frequency ---
        parser.add_argument(
            "-mtf", "--MTF", type=float, required=True,
            help="Participant maximum taping frequency"
        )

        # --- Design parameters ---
        parser.add_argument(
            "-n", "--nTrials", type=int, default=64,
            help="Number of trials in block (should be a multiple of 16)"
        )
        parser.add_argument(
            "-e", "--nEffortTrials", type=int, default=16,
            help="Number of effort trials in block (should be one fourth of total number of trials)"
        )

    elif task == Task.MTF:

        # --- Block name ---
        parser.add_argument(
            "-b", "--block_id", type=str, required=True, choices=["MTF_PRE", "MTF_VF"],
            help="Block identifier"
        )  

        if "-b" in sys.argv:
            b_index = sys.argv.index("-b") + 1
            block_choice = sys.argv[b_index]

        if block_choice == "MTF_PRE":
            # --- Design parameters ---
            parser.add_argument(
                "-n", "--nTrials", type=int, default=4,
                help="Number of trials in the maximum tapping frequency task (typ 4)"
            )     
            parser.add_argument(
            "-e", "--nEffortTrials", type=int, default=4,
            help="Number of effort trials in the maximum tapping frequency task w/o visual feedback (typ 4)"
            )

        elif block_choice == "MTF_VF":
            print('sono entrato')

            # --- Design parameters ---
            parser.add_argument(
                "-n", "--nTrials", type=int, default=3,
                help="Number of trials in the maximum tapping frequency task w visual feedback (typ 3)"
            )     
            parser.add_argument(
                "-e", "--nEffortTrials", type=int, default=3,
                help="Number of effort trials in the maximum tapping frequency task w visual feedback (typ 3)"
            )
            parser.add_argument(
                "-mtf", "--MTF", type=float, required=True,
                help="mtf computed in the first step of calibration"
            )


    parser.add_argument(
        "--log-level", type=str, choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO"
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
def get_task_duration(flag_eyetracker:int, population:Population, task:Task) -> Duration:
    """Return a dict of per-phase durations (ms) based on population and eyetracker flag."""
    dur = Duration()

    if population == Population.Healthy:  # I AM FORCING IT TO BE LIKE OLD!!!

        if task == Task.EBDM:

            dur.Blank1 = 2000
            dur.DM_Preparation = [1000, 1400]
            dur.DM = 6000
            dur.TimeAfterDMade = 1000
            dur.TimeAfterPositionRight = 1000
            dur.GetReadyForEP = 2000
            dur.EP_Preparation = [1800, 2200]
            dur.Task = 6000
            dur.Blank2 = 500
            dur.Feedback = 1000
            dur.TimeForPupilBaselineBack = 2000 if flag_eyetracker == 1 else 2000
            dur.FinalFeedback = 4000
            dur.StartBlock = 500
            
        elif task == Task.MTF:
            dur.Blank1 = 2000
            dur.TimeAfterPositionRight = 1000
            dur.GetReadyForEP = 1000
            dur.EP_Preparation = [1000, 1400]
            dur.Task = 6000
            dur.Blank2 = 500
            dur.Feedback = 1000
            dur.TimeForPupilBaselineBack = 3000 
            dur.StartBlock = 500


    elif Population == Population.Old: 


        if task == Task.EBDM: 

            dur.Blank1 = 2000
            dur.DM_Preparation = [1000, 1400]
            dur.DM = 6000
            dur.TimeAfterDMade = 1000
            dur.TimeAfterPositionRight = 1000
            dur.GetReadyForEP = 1000
            dur.EP_Preparation = [1800, 2200]
            dur.Task = 6000
            dur.Blank2 = 500
            dur.Feedback = 1000
            dur.TimeForPupilBaselineBack = 2000 if flag_eyetracker == 1 else 2000
            dur.FinalFeedback = 4000
            dur.StartBlock = 500

        elif task ==Task.MTF:
            dur.Blank1 = 2000
            dur.TimeAfterPositionRight = 1000
            dur.GetReadyForEP = 1000
            dur.EP_Preparation = [1800, 2200]
            dur.Task = 6000
            dur.Blank2 = 500
            dur.Feedback = 1000
            dur.TimeForPupilBaselineBack = 30000
            dur.StartBlock = 500



    elif population == Population.DBS:  
        dur.Blank1 = 2000
        dur.DM_Preparation = [1000, 1400]
        dur.DM = 6000
        dur.TimeAfterDMade = 1000
        dur.TimeAfterPositionRight = 1000
        dur.GetReadyForEP = 1000
        dur.EP_Preparation = [1800, 2200]
        dur.Task = 6000
        dur.Blank2 = 500
        dur.Feedback = 1000
        dur.TimeForPupilBaselineBack = 2000 if flag_eyetracker == 1 else 2000
        dur.FinalFeedback = 4000
        dur.StartBlock = 500

    return dur

def get_effort_proposed(population:Population):
    if population == Population.Healthy:
        return np.array([0.5, 0.65, 0.8, 0.95])

    else:
        return np.array([0.45, 0.6, 0.75, 0.9])
    

def get_reward_proposed():
    return np.array([1, 5, 10, 20])

def init_trials(n_trials, task:Task, dur_prep_ep, cond_e_r=None, dur_prep_dm=None):
    """Create the trial table (pandas.DataFrame) mirroring the Matlab structure."""

    if task == Task.EBDM:
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

    elif task == Task.MTF:
        trials = pd.DataFrame({
            "trial": np.arange(1, n_trials + 1),                       # Trial index
            "ReactionTimeEP": np.full(n_trials, np.nan),               # Reaction time (EP)
            "EffortProduction": np.full(n_trials, np.nan),             # 1 if produced
            "durPrep_EP": np.random.randint(                           # Prep EP duration (ms)
                low=int(dur_prep_ep[0]),
                high=int(dur_prep_ep[1]) + 1,
                size=n_trials
            ),
            "Anticipation_EP": np.full(n_trials, np.nan),              # Bool or NaN
            "KeyPositionTime": np.full(n_trials, np.nan),              # Posture time
        })


    return trials
