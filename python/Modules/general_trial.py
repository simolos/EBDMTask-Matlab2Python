# Modules/generation_trial.py
import numpy as np
from config import Population, get_effort_proposed, get_reward_proposed
from itertools import product

import numpy as np
from itertools import product
from config import get_effort_proposed, get_reward_proposed


import numpy as np
from itertools import product
from config import get_effort_proposed, get_reward_proposed


import numpy as np
from config import get_effort_proposed, get_reward_proposed


def GetTrialCondition(nTrials, n_Effort_Trials, population):

    Eff = get_effort_proposed(population)
    Rew = get_reward_proposed()

    n_eff = len(Eff)
    n_rew = len(Rew)
    n_combos = n_eff * n_rew

    # -------------------------------------------------
    # 1) CREATE BALANCED ORDER OF COMBINATIONS
    # (Latin-style traversal of effort×reward grid)
    # -------------------------------------------------

    combos = []
    for k in range(n_combos):
        e = Eff[k % n_eff]
        r = Rew[(k // n_eff + k % n_eff) % n_rew]
        combos.append((e, r))

    # -------------------------------------------------
    # 2) DISTRIBUTE TOTAL TRIALS
    # -------------------------------------------------

    base = nTrials // n_combos
    remainder = nTrials % n_combos

    rows = []

    for i, (eff, rew) in enumerate(combos):

        n = base + (i < remainder)

        for _ in range(n):
            rows.append([eff, rew, 0])   # start as DM

    Cond = np.array(rows)

    # -------------------------------------------------
    # 3) ASSIGN EP (priority: effort → combo)
    # -------------------------------------------------

    ep_per_eff_base = n_Effort_Trials // n_eff
    ep_per_eff_rem = n_Effort_Trials % n_eff

    ep_target_eff = {
        Eff[i]: ep_per_eff_base + (i < ep_per_eff_rem)
        for i in range(n_eff)
    }

    ep_eff_count = {e: 0 for e in Eff}
    ep_combo_count = {(e, r): 0 for e in Eff for r in Rew}

    total_ep = 0

    while total_ep < n_Effort_Trials:

        best_idx = None
        best_score = None

        for i, (eff, rew, flag) in enumerate(Cond):

            if flag == 1:
                continue

            combo = (eff, rew)

            if ep_eff_count[eff] >= ep_target_eff[eff]:
                continue

            score = ep_combo_count[combo]

            if best_score is None or score < best_score:
                best_score = score
                best_idx = i

        # assign EP
        eff, rew, _ = Cond[best_idx]

        Cond[best_idx, 2] = 1

        ep_eff_count[eff] += 1
        ep_combo_count[(eff, rew)] += 1

        total_ep += 1

    # -------------------------------------------------
    # 4) RANDOMIZE TRIAL ORDER
    # -------------------------------------------------

    perm = np.random.permutation(len(Cond))
    Cond = Cond[perm]

    indx_Effort_Trials = np.where(Cond[:, 2] == 1)[0]

    return Cond, indx_Effort_Trials

#### test 

if __name__ == "__main__":
    # --- Parameters for quick test ---
    n_trials = 80
    n_effort_trials = 16
    flag_population = 1  # 1=healthy, 2=old, 3=patient

    cond_er, indx_effort_trials = GetTrialCondition(
        n_trials, n_effort_trials, flag_population
    )

    print("=== Trial Generation Test ===")
    print(f"Total trials: {cond_er.shape[0]} (expected {n_trials})")
    print(f"Effort trials (EP=1): {len(indx_effort_trials)} (expected {n_effort_trials})")




    # Breakdown per effort level
    eff_levels = np.unique(cond_er[:, 0])
    for eff in eff_levels:
        dm_count = np.sum((cond_er[:, 0] == eff) & (cond_er[:, 2] == 0))
        ep_count = np.sum((cond_er[:, 0] == eff) & (cond_er[:, 2] == 1))
        print(f"Effort {eff:.2f}: DM={dm_count}, EP={ep_count}")

    # Breakdown per effort-reward combination
    print("\n=== Combination Counts ===")

    eff_levels = np.unique(cond_er[:, 0])
    rew_levels = np.unique(cond_er[:, 1])

    for eff in eff_levels:
        for rew in rew_levels:

            mask = (cond_er[:,0] == eff) & (cond_er[:,1] == rew)

            total = np.sum(mask)
            dm = np.sum(mask & (cond_er[:,2] == 0))
            ep = np.sum(mask & (cond_er[:,2] == 1))

            print(f"(Effort={eff:.2f}, Reward={rew}) → Total={total} | DM={dm} | EP={ep}")

    # Integrity check
    assert cond_er.shape[0] == n_trials, "❌ Wrong total number of trials"
    assert len(indx_effort_trials) == n_effort_trials, "❌ Wrong number of EP trials"
    print("✅ Balancing test passed")
    