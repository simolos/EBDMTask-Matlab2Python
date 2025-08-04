# Modules/generation_trial.py
"""
Module for generating trial parameters for the Effort-Based Decision Making (EBDM) task.
Each trial includes: decision options, effort level, timings, trial identifiers, etc.
"""
import random
from typing import Dict, Any, List

# Example variable names from data_tab.pdf
# Assuming fields: trial_number, decision_options, effort_level, reward_amount, durations

class TrialGenerator:
    """
    Generates parameters for each trial according to experimental design.
    """
    def __init__(
        self,
        n_trials: int,
        effort_levels: List[float],
        rewards: List[float],
        durations: Dict[str, float],
        seed: int = None
    ):
        """
        Args:
            n_trials: total number of trials
            effort_levels: possible effort levels (e.g., [0.2, 0.5, 0.8])
            rewards: possible reward amounts associated with effort
            durations: dict of phase durations, e.g. {'fixation':0.5, 'decision':2.0}
            seed: optional random seed for reproducibility
        """
        self.n_trials = n_trials
        self.effort_levels = effort_levels
        self.rewards = rewards
        self.durations = durations
        if seed is not None:
            random.seed(seed)

    def generate_all(self) -> List[Dict[str, Any]]:
        """
        Generate a list of trial parameter dicts.
        """
        trials = []
        for i in range(1, self.n_trials + 1):
            trial = self.generate_single(i)
            trials.append(trial)
        return trials

    def generate_single(self, trial_number: int) -> Dict[str, Any]:
        """
        Generate parameters for a single trial.
        """
        # Randomly sample effort and reward
        effort = random.choice(self.effort_levels)
        reward = random.choice(self.rewards)
        # Define decision options text
        decision_options = {
            'easy': {'effort': min(self.effort_levels), 'reward': min(self.rewards)},
            'hard': {'effort': effort, 'reward': reward}
        }
        trial_params = {
            'trial_number': trial_number,
            'effort_level': effort,
            'reward_amount': reward,
            'decision_options': decision_options,
            # Phase durations from config
            'dur_fixation': self.durations.get('fixation', 0.5),
            'dur_decision': self.durations.get('decision', 2.0),
            'dur_effort': self.durations.get('effort', 5.0),
            'dur_feedback': self.durations.get('feedback', 1.0)
        }
        return trial_params

# Example usage
if __name__ == '__main__':
    gen = TrialGenerator(
        n_trials=10,
        effort_levels=[0.2, 0.5, 0.8],
        rewards=[1, 2, 3],
        durations={'fixation':0.5, 'decision':2.0, 'effort':5.0, 'feedback':1.0},
        seed=42
    )
    trials = gen.generate_all()
    for t in trials:
        print(t)
