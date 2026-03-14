# Modules/generation_trial.py
import numpy as np
from config import Population, get_effort_proposed, get_reward_proposed
from itertools import product


def GetTrialCondition(nTrials, n_Effort_Trials, population):

    Eff_Proposed = get_effort_proposed(population)
    Rew_Proposed = get_reward_proposed()

    combos = list(product(Eff_Proposed, Rew_Proposed))

    trials_per_combo = nTrials // len(combos)
    ep_per_combo = n_Effort_Trials // len(combos)

    rows = []

    for eff, rew in combos:

        # EP trials
        for _ in range(ep_per_combo):
            rows.append([eff, rew, 1])

        # DM trials
        for _ in range(trials_per_combo - ep_per_combo):
            rows.append([eff, rew, 0])

    Cond_E_R = np.array(rows)

    # shuffle
    perm = np.random.permutation(len(Cond_E_R))
    Cond_E_R = Cond_E_R[perm]

    indx_Effort_Trials = np.where(Cond_E_R[:,2] == 1)[0]

    return Cond_E_R, indx_Effort_Trials


'''
#### test 

if __name__ == "__main__":
    # --- Parameters for quick test ---
    n_trials = 80
    n_effort_trials = 16
    flag_population = 1  # 1=healthy, 2=old, 3=patient

    cond_er, indx_effort_trials = GetTrialCondition(
        n_trials, n_effort_trials, flag_population
    )

    print(cond_er)

    print("=== Trial Generation Test ===")
    print(f"Total trials: {cond_er.shape[0]} (expected {n_trials})")
    print(f"Effort trials (EP=1): {len(indx_effort_trials)} (expected {n_effort_trials})")

    # --- Breakdown per (effort, reward) combination ---
    Eff_Proposed = get_effort_proposed(flag_population)
    Rew_Proposed = get_reward_proposed()

    combos = list(product(Eff_Proposed, Rew_Proposed))

    print("\n=== Combination Counts ===")

    for eff, rew in combos:

        dm_count = np.sum(
            (cond_er[:, 0] == eff) &
            (cond_er[:, 1] == rew) &
            (cond_er[:, 2] == 0)
        )

        ep_count = np.sum(
            (cond_er[:, 0] == eff) &
            (cond_er[:, 1] == rew) &
            (cond_er[:, 2] == 1)
        )

        total = dm_count + ep_count

        print(f"(Effort={eff}, Reward={rew}) → Total={total} | DM={dm_count} | EP={ep_count}")

    # Breakdown per effort level
    eff_levels = np.unique(cond_er[:, 0])
    for eff in eff_levels:
        dm_count = np.sum((cond_er[:, 0] == eff) & (cond_er[:, 2] == 0))
        ep_count = np.sum((cond_er[:, 0] == eff) & (cond_er[:, 2] == 1))
        print(f"Effort {eff:.2f}: DM={dm_count}, EP={ep_count}")

    # Integrity check
    assert cond_er.shape[0] == n_trials, "❌ Wrong total number of trials"
    assert len(indx_effort_trials) == n_effort_trials, "❌ Wrong number of EP trials"
    print("✅ Balancing test passed")
'''