# config.py
import argparse
import numpy as np
import pandas as pd
from datetime import datetime


def parse_args():
    """
    Parse command-line arguments and return a configuration object.
    """
    parser = argparse.ArgumentParser(
        description="Experiment configuration for EBDMTask"
    )
    parser.add_argument('-s', '--subject-id', type=str, required=True,
                        help='Participant identifier (e.g., S01)')
    parser.add_argument('-b', '--block-id', type=str, required=True,
                        help='Block number)')
    parser.add_argument("-o", "--output_dir", default="results",  #/Users/elyesamarimilliti/Desktop/Project/EBDMTask-Matlab2Python/data_log
                    help="Folder where logs/files are written")
    parser.add_argument('-l', '--language', type=str, default='en',
                        choices=['en', 'fr'],
                        help='Experiment language')
    parser.add_argument('-t', '--stimulation', type=str, default='none',
                        help='Type of stimulation (e.g., none, tms)')
    parser.add_argument('-n', '--nTrials', type=int, default=32,
                        help='Number of trials in block (should be multiple of 16)')
    parser.add_argument('-e', '--nEffortTrials', type=int, default=8,
                        help='Number of effort trials in block')
    parser.add_argument('-p', '--population', type=int, default=1,
                        help='Population group (1, 2, or 3) : 1 -> healthy, 2 -> old, 2 -> patient')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug mode (console logs, faster timings)')
    parser.add_argument('--eyetracker', action='store_true',
                        help='Enable eye-tracking data collection')
    parser.add_argument('--test-dev', action='store_true',
                        help='Enable test/dev mode (mock inputs and WS)')
    parser.add_argument('-m', '--mode', type=int, default=0,
                        choices=[0, 1, 2],
                        help='Mode of pressed keys activation (mode 0, 1 or 2)')
    parser.add_argument('-chmap', '--ChangeMappingYes', type=str, default='N',
                        choices=['N', 'Y'],
                        help='Multiple keys pressed activation (Y/N)')
    parser.add_argument('-fullscr', '--fullscreen', type=str, default='N',
                        choices=['N', 'Y'],
                        help='Multiple keys pressed activation (Y/N)')
    args = parser.parse_args()

    # Generate timestamp for session (YYYYMMDD_HHMMSS)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    args.timestamp = timestamp

    # Define output filename prefix
    args.output_prefix = f"{args.subject_id}_{timestamp}"

    return args

### Constants
keys_choice = ['left', 'right'] # [left] -> yes, [right] -> No
combo = {'q', 'z', 'e'} 


# Translations dictionnary
TRANSLATIONS = {
    'fr': {
        'yes': "Oui",
        'no': "Non",
        'success': "Succès !",
        'failure': "Raté !",
        'ready': "Préparez-vous",
        'effort_perceived': "Effort perçu",
        'no_effort': "Pas d'effort",
        'max_effort': "Effort maximum",
        'press': "Pressez",   # ou "Pressez"
        'fingers': "-".join(sorted(combo)).upper(),
        'failed_try': "Raté ! Veuillez essayer à nouveau",
        'anticip': "Anticipé !",
        'rest': "Repos",
        'go': "Go!!!",
        'end_task': "Fin de la tâche",
        'get_effort_note': "Veuillez noter la perception de votre effort...",
        'reward_question': "La récompense en vaut-elle l'effort ?",
        'total': "Total = {val} CHF",
        # --- dynamiques ---
        'reward_for': "Pour {val} cents",    # pendant décision ou Go!!!
        'reward_plus': "+ {val} cents",      # feedback succès
        'reward_minus': "- {val} cents"      # feedback gros échec
    },
    'en': {
        'yes': "Yes",
        'no': "No",
        'success': "Success!",
        'failure': "Failure!",
        'ready': "Get ready",
        'effort_perceived': "Effort perceived",
        'no_effort': "No effort at all",
        'max_effort': "Maximum effort",
        'press': "Press",
        'fingers': "-".join(sorted(combo)).upper(),
        'failed_try': "Failure! Please repeat the trial",
        'anticip': "Anticipated",
        'rest': "Rest",
        'go': "Go!!!",
        'end_task': "End of task",
        'get_effort_note': "Please rate your perceived effort...",
        'reward_question': "Is the reward worth the effort?",
        'total': "Total = {val} CHF",
        # --- dynamics ---
        'reward_for': "For {val} cents",     # during decision or Go!!!
        'reward_plus': "+ {val} cents",      # success feedback
        'reward_minus': "- {val} cents"      # big failure feedback
    }
}



# get_task_duration.py

def get_task_duration(flag_eyetracker: int, flag_population: int) -> dict:
    """
    Define the duration (in ms) of each phase of the task depending on the population and eyetracker flag.
    Args:
        flag_eyetracker (int): 1 if eyetracker is used, else 0
        flag_population (int): 1 = Healthy, 2 = Old, 3 = DBS implanted
    Returns:
        dict: dictionary of durations in milliseconds
    """

    dur = {}

    if flag_population == 1:  # Healthy
        dur["Blank1"] = 2000  # intertrial interval
        dur["DM_Preparation"] = [1000, 1400]  # between cross and "For x cents"
        dur["DM"] = 4000  # decision-making phase
        dur["TimeAfterDMade"] = 1000  # time after decision
        dur["TimeAfterPositionRight"] = 1000  # time after correct finger position
        dur["GetReadyForEP"] = 1000
        dur["EP_Preparation"] = [1000, 1400]  # preparation for effort phase
        dur["Task"] = 8000  # effort production duration
        dur["Blank2"] = 500  # between EP and reward
        dur["Reward"] = 1000  # Feedback screen duration
        # pupil baseline recovery
        dur["TimeForPupilBaselineBack"] = 2000 if flag_eyetracker == 1 else 2000
        dur["FinalFeedback"] = 4000  # Final Feedback screen duration
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
        dur["FinalFeedback"] = 4000  # Final Feedback
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
        dur["FinalFeedback"] = 4000  # Final Feedback
        dur["StartBlock"] = 500  

    return dur


def init_trials(n_trials, cond_e_r, dur_prep_dm, dur_prep_ep):
    """
    Reproduit la structure 'trials' du code Matlab dans un DataFrame pandas.
    
    Args:
        n_trials (int): nombre total de trials
        cond_e_r (ndarray): tableau (n_trials x 2) effort / reward
        dur_prep_dm (tuple): (min_ms, max_ms) durée préparation DM
        dur_prep_ep (tuple): (min_ms, max_ms) durée préparation EP
    """
    trials = pd.DataFrame({
        "trial": np.arange(1, n_trials + 1),                       # Trial index
        "effort": cond_e_r[:, 0],                                  # Effort nominal
        "efftested": cond_e_r[:, 0].copy(),                        # Effort présenté
        "rewtested": cond_e_r[:, 1].copy(),                        # Récompense présentée
        "reward": cond_e_r[:, 1],                                  # Récompense nominale
        "DecisionTime": np.full(n_trials, np.nan),                 # Temps décision
        "ReactionTimeEP": np.full(n_trials, np.nan),               # Temps réaction EP
        "Acceptance": np.full(n_trials, np.nan),                   # 1/0/-1
        "EffortProduction": np.full(n_trials, np.nan),             # 1 si produit
        "durPrep_DM": np.random.randint(                           # Durée préparation DM (ms)
            low=int(dur_prep_dm[0]), 
            high=int(dur_prep_dm[1]) + 1, 
            size=n_trials
        ),
        "durPrep_EP": np.random.randint(                           # Durée préparation EP (ms)
            low=int(dur_prep_ep[0]), 
            high=int(dur_prep_ep[1]) + 1, 
            size=n_trials
        ),
        "success": np.full(n_trials, np.nan),                      # 1/0/-1
        "Anticipation_EP": np.full(n_trials, np.nan),              # Bool ou NaN
        "Anticipation_DM": np.zeros(n_trials),                     # Bool
        "KeyPositionTime": np.full(n_trials, np.nan),              # Temps posture
    })
    return trials


"""
if __name__ == '__main__':
    cfg = parse_args()
    print(f"Loaded configuration: {cfg}")
"""