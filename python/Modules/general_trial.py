# Modules/generation_trial.py
import numpy as np
from config import Population, get_effort_proposed, get_reward_proposed

def _balanced_pick_rows_per_effort(pool, Eff_Proposed, rows_per_value):
    """
    Return a balanced selection across effort levels (first column),
    taking up to rows_per_value per level without replacement.
    pool: (N,3) array [effort, reward, flag]
    """
    selected = []
    for value in np.unique(Eff_Proposed):
        rows = pool[pool[:, 0] == value]
        if len(rows) <= rows_per_value:
            selected.append(rows)
        else:
            idx = np.random.choice(len(rows), rows_per_value, replace=False)
            selected.append(rows[idx])
    if len(selected) == 0:
        return np.empty((0, pool.shape[1]))
    return np.vstack(selected)

def GetTrialCondition(nTrials, n_Effort_Trials, population:Population):
    """
    Strict port of the MATLAB GetTrialCondition.
    Returns:
      Cond_E_R: (nTrials, 3) array [Effort, Reward, EP_flag]
      indx_Effort_Trials: indices where EP_flag==1
    """
    # --- Effort grid (per population) ---
    Eff_Proposed = get_effort_proposed(population)

    Rew_Proposed = get_reward_proposed()

    Effort, Reward = np.meshgrid(Eff_Proposed, Rew_Proposed)

    # All combinations; 3rd col is EP flag (0=DM only, 1=EP)
    all_combinations = np.column_stack([Effort.ravel(), Reward.ravel(),
                                        np.zeros(Effort.size, dtype=int)])
    all_combinations_EP = np.column_stack([Effort.ravel(), Reward.ravel(),
                                           np.ones(Effort.size, dtype=int)])
    N_total_comb = all_combinations.shape[0]
    Cond_E_R = np.empty((0, 3))

    # ---- CASE A: need to repeat all combinations (nTrials >= N_total_comb) ----
    if (nTrials // N_total_comb) > 0:
        reps = nTrials // N_total_comb

        # EP_vector (how many EP flags to set per full block)
        ep_full_blocks = (n_Effort_Trials // N_total_comb)
        ep_remainder   = (n_Effort_Trials %  N_total_comb)
        EP_vector = ([N_total_comb] * ep_full_blocks) + ([ep_remainder] if ep_remainder > 0 else [])
        # pad to reps
        if len(EP_vector) < reps:
            EP_vector += [0] * (reps - len(EP_vector))

        for b in range(reps):
            rows_per_value = int(np.ceil(EP_vector[b] / len(Eff_Proposed))) if len(Eff_Proposed) > 0 else 0
            # fresh zero-flag block
            block = all_combinations.copy()
            # balanced selection to flag as EP=1
            if rows_per_value > 0:
                selected_rows = _balanced_pick_rows_per_effort(block, Eff_Proposed, rows_per_value)
                # set EP flag=1 for selected rows (match on Eff & Rew)
                # (vectorized match)
                if len(selected_rows) > 0:
                    # build boolean mask where rows are in selected_rows
                    sel_mask = (block[:, None, 0] == selected_rows[None, :, 0]) & \
                               (block[:, None, 1] == selected_rows[None, :, 1])
                    sel_mask = sel_mask.any(axis=1)
                    block[sel_mask, 2] = 1
            # append to Cond_E_R
            Cond_E_R = np.vstack([Cond_E_R, block])

        # Adjust EP count to n_Effort_Trials
        ep_idx = np.where(Cond_E_R[:, 2] == 1)[0]
        if len(ep_idx) < n_Effort_Trials:
            need = n_Effort_Trials - len(ep_idx)
            # add from EP pool (random)
            add_idx = np.random.choice(N_total_comb, size=need, replace=False)
            Cond_E_R = np.vstack([Cond_E_R, all_combinations_EP[add_idx]])
        elif len(ep_idx) > n_Effort_Trials:
            extra = len(ep_idx) - n_Effort_Trials
            drop = np.random.choice(ep_idx, size=extra, replace=False)
            Cond_E_R = np.delete(Cond_E_R, drop, axis=0)

        # Add missing DM trials to reach exactly nTrials with balancing
        remaining = nTrials - Cond_E_R.shape[0]
        if remaining > 0:
            rows_per_value = remaining // len(Eff_Proposed) if len(Eff_Proposed) > 0 else 0
            selected_rows = _balanced_pick_rows_per_effort(all_combinations, Eff_Proposed, rows_per_value)
            # if still short (due to integer division), top up randomly
            topup = nTrials - (Cond_E_R.shape[0] + selected_rows.shape[0])
            if topup > 0:
                rnd_idx = np.random.choice(N_total_comb, size=topup, replace=False)
                extra = all_combinations[rnd_idx]
                Cond_E_R = np.vstack([Cond_E_R, selected_rows, extra])
            else:
                Cond_E_R = np.vstack([Cond_E_R, selected_rows])

    # ---- CASE B: fewer than all combinations (nTrials < N_total_comb) ----
    else:
        # Start from all combos; select a balanced DM subset
        single_effort_repetition_num = int(np.ceil(nTrials / len(Eff_Proposed))) if len(Eff_Proposed) > 0 else 0
        selected_combinations = []
        for effort in Eff_Proposed:
            rows_w_effort = all_combinations[all_combinations[:, 0] == effort]
            if len(rows_w_effort) <= single_effort_repetition_num:
                selected_combinations.append(rows_w_effort)
            else:
                idx = np.random.choice(len(rows_w_effort), single_effort_repetition_num, replace=False)
                selected_combinations.append(rows_w_effort[idx])
        selected_combinations = np.vstack(selected_combinations) if len(selected_combinations) else np.empty((0,3))

        # Keep only those rows in Cond_E_R (balanced DM pool)
        # (set membership on Eff & Rew)
        keep_mask = (np.isin(all_combinations[:, 0], selected_combinations[:, 0]) &
                     np.isin(all_combinations[:, 1], selected_combinations[:, 1]))
        Cond_E_R = all_combinations[keep_mask].copy()

        # Adjust DM count to exactly nTrials (balanced additions/removals)
        dm_count = np.sum(Cond_E_R[:, 2] == 0)
        if dm_count < nTrials:
            # add missing DM rows, balanced by effort
            rows_per_value = nTrials - dm_count
            # balanced selection from the full pool (MATLAB note says “probably never”)
            balanced_add = _balanced_pick_rows_per_effort(all_combinations, Eff_Proposed, rows_per_value)
            # If selection overshoots, just truncate later with random top-up
            topup = nTrials - (Cond_E_R.shape[0] + balanced_add.shape[0])
            if topup > 0:
                idx = np.random.choice(N_total_comb, size=topup, replace=False)
                Cond_E_R = np.vstack([Cond_E_R, balanced_add, all_combinations[idx]])
            else:
                Cond_E_R = np.vstack([Cond_E_R, balanced_add])
        elif dm_count > nTrials:
            # delete extra DM rows (balanced)
            NumExtraTrials = dm_count - nTrials
            rows_per_value = int(np.ceil(NumExtraTrials / len(Eff_Proposed))) if len(Eff_Proposed) > 0 else 0
            # pick candidates to remove, balanced over efforts, from Cond_E_R (DM only)
            DM_rows = Cond_E_R[Cond_E_R[:, 2] == 0]
            selected_rows = _balanced_pick_rows_per_effort(DM_rows, Eff_Proposed, rows_per_value)
            # now randomly remove exactly NumExtraTrials from those selected
            # build mask of Cond_E_R rows matching selected_rows
            match_mask = ((Cond_E_R[:, None, 0] == selected_rows[None, :, 0]) &
                          (Cond_E_R[:, None, 1] == selected_rows[None, :, 1]) &
                          (Cond_E_R[:, None, 2] == selected_rows[None, :, 2])).any(axis=1)
            cand_idx = np.where(match_mask)[0]
            drop = np.random.choice(cand_idx, size=NumExtraTrials, replace=False)
            Cond_E_R = np.delete(Cond_E_R, drop, axis=0)

        # --- NOW select EP trials within Cond_E_R (balanced) ---
        rows_per_value = int(np.ceil(n_Effort_Trials / len(Eff_Proposed))) if len(Eff_Proposed) > 0 else 0
        selected_rows = _balanced_pick_rows_per_effort(Cond_E_R, Eff_Proposed, rows_per_value)
        # set EP flag=1 for selected_rows
        if len(selected_rows) > 0:
            sel_mask = ((Cond_E_R[:, None, 0] == selected_rows[None, :, 0]) &
                        (Cond_E_R[:, None, 1] == selected_rows[None, :, 1])).any(axis=1)
            Cond_E_R[sel_mask, 2] = 1

        # Adjust EP count (balanced add/remove)
        ep_count = np.sum(Cond_E_R[:, 2] == 1)
        if ep_count < n_Effort_Trials:
            NumMissingTrials = n_Effort_Trials - ep_count
            DM_trials = Cond_E_R[Cond_E_R[:, 2] == 0]
            rows_per_value = int(np.ceil(NumMissingTrials / len(Eff_Proposed))) if len(Eff_Proposed) > 0 else 0
            balanced_add = _balanced_pick_rows_per_effort(DM_trials, Eff_Proposed, rows_per_value)
            # toggle EP=1 for a random subset of size NumMissingTrials
            # first find their indices in Cond_E_R
            if len(balanced_add) > 0:
                match_mask = ((Cond_E_R[:, None, 0] == balanced_add[None, :, 0]) &
                              (Cond_E_R[:, None, 1] == balanced_add[None, :, 1]) &
                              (Cond_E_R[:, None, 2] == 0)).any(axis=1)
                cand_idx = np.where(match_mask)[0]
                to_set = np.random.choice(cand_idx, size=min(NumMissingTrials, len(cand_idx)), replace=False)
                Cond_E_R[to_set, 2] = 1
        elif ep_count > n_Effort_Trials:
            NumExtraTrials = ep_count - n_Effort_Trials
            EP_trials = Cond_E_R[Cond_E_R[:, 2] == 1]
            rows_per_value = int(np.ceil(NumExtraTrials / len(Eff_Proposed))) if len(Eff_Proposed) > 0 else 0
            balanced_rm = _balanced_pick_rows_per_effort(EP_trials, Eff_Proposed, rows_per_value)
            # find matches in Cond_E_R and toggle EP=0 for NumExtraTrials of them
            match_mask = ((Cond_E_R[:, None, 0] == balanced_rm[None, :, 0]) &
                          (Cond_E_R[:, None, 1] == balanced_rm[None, :, 1]) &
                          (Cond_E_R[:, None, 2] == 1)).any(axis=1)
            cand_idx = np.where(match_mask)[0]
            to_reset = np.random.choice(cand_idx, size=min(NumExtraTrials, len(cand_idx)), replace=False)
            Cond_E_R[to_reset, 2] = 0

    # Final shuffle (row order randomized)
    perm = np.random.permutation(len(Cond_E_R))
    Cond_E_R = Cond_E_R[perm]
    indx_Effort_Trials = np.where(Cond_E_R[:, 2] == 1)[0]
    return Cond_E_R, indx_Effort_Trials


# --- Optional: quick sanity checker (use in tests) ---
def check_balancing(Cond_E_R, Eff_Proposed, nTrials, n_Effort_Trials):
    """
    Print per-effort counts for DM and EP; assert totals are correct.
    """
    assert Cond_E_R.shape[0] == nTrials, f"Expected {nTrials} trials, got {Cond_E_R.shape[0]}"
    ep_idx = Cond_E_R[:, 2] == 1
    dm_idx = Cond_E_R[:, 2] == 0
    assert ep_idx.sum() == n_Effort_Trials, f"Expected {n_Effort_Trials} EP, got {ep_idx.sum()}"

    for eff in Eff_Proposed:
        dm_cnt = np.sum((Cond_E_R[:, 0] == eff) & dm_idx)
        ep_cnt = np.sum((Cond_E_R[:, 0] == eff) & ep_idx)
        print(f"Effort {eff:>4}: DM={dm_cnt:>3} | EP={ep_cnt:>3}")


#### test 
"""
if __name__ == "__main__":
    # --- Parameters for quick test ---
    n_trials = 32
    n_effort_trials = 14
    flag_population = 1  # 1=healthy, 2=old, 3=patient

    cond_er, indx_effort_trials = GetTrialCondition(
        n_trials, n_effort_trials, flag_population
    )

    print(cond_er)

    print("=== Trial Generation Test ===")
    print(f"Total trials: {cond_er.shape[0]} (expected {n_trials})")
    print(f"Effort trials (EP=1): {len(indx_effort_trials)} (expected {n_effort_trials})")

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
    """