# Modules/generation_trial.py

import numpy as np

def GetTrialCondition(n_trials, n_effort_trials, flag_population):
    # Define effort levels based on population
    if flag_population == 1:
        eff_proposed = np.array([0.5, 0.65, 0.8, 0.95])
    else:
        eff_proposed = np.array([0.45, 0.6, 0.75, 0.9])

    # Define reward levels
    rew_proposed = np.array([1, 5, 10, 20])
    n_total_comb = len(eff_proposed) * len(rew_proposed)

    # Generate all Effort × Reward combinations with integer flags
    Eff, Rew = np.meshgrid(eff_proposed, rew_proposed)
    all_comb = np.column_stack((Eff.ravel(), Rew.ravel(),
                                np.zeros(n_total_comb, dtype=int)))
    all_comb_ep = np.column_stack((Eff.ravel(), Rew.ravel(),
                                   np.ones(n_total_comb, dtype=int)))

    cond_er_blocks = []

    # CASE 1: at least one full pass over all combinations
    repetitions = n_trials // n_total_comb
    if repetitions > 0:
        # Build the EP counts vector
        full_blocks = n_effort_trials // n_total_comb
        remainder = n_effort_trials % n_total_comb
        ep_counts = [n_total_comb] * full_blocks + [remainder]
        # pad with zeros if needed
        ep_counts += [0] * (repetitions - len(ep_counts))

        for b in range(repetitions):
            # how many EP trials per effort level this block
            rows_per_effort = int(np.ceil(ep_counts[b] / len(eff_proposed)))
            selected_rows = []

            # select balanced by effort level
            for level in eff_proposed:
                mask = all_comb[:, 0] == level
                candidates = all_comb[mask]
                if len(candidates) <= rows_per_effort:
                    sel = candidates
                else:
                    sel = candidates[np.random.choice(len(candidates),
                                                     rows_per_effort,
                                                     replace=False)]
                selected_rows.append(sel)

            sel = np.vstack(selected_rows)
            # mark selected rows as EP
            for r in sel:
                match = np.all(all_comb[:, :2] == r[:2], axis=1)
                all_comb[match, 2] = 1

            cond_er_blocks.append(all_comb.copy())
            # reset flags for next block
            all_comb[:, 2] = 0

        cond_er = np.vstack(cond_er_blocks)
        # adjust to exactly n_effort_trials
        current_ep = int((cond_er[:, 2] == 1).sum())
        if current_ep < n_effort_trials:
            add_count = n_effort_trials - current_ep
            replace_flag = add_count > n_total_comb
            to_add = all_comb_ep[np.random.choice(n_total_comb,
                                                  add_count,
                                                  replace=replace_flag)]
            cond_er = np.vstack((cond_er, to_add))
        elif current_ep > n_effort_trials:
            ep_idx = np.where(cond_er[:, 2] == 1)[0]
            remove_idx = np.random.choice(ep_idx,
                                          current_ep - n_effort_trials,
                                          replace=False)
            cond_er = np.delete(cond_er, remove_idx, axis=0)

        # complete with decision trials to reach n_trials
        remaining = n_trials - len(cond_er)
        rows_per_effort_dm = remaining // len(eff_proposed)
        dm_blocks = []
        for level in eff_proposed:
            mask = all_comb[:, 0] == level
            candidates = all_comb[mask]
            if len(candidates) <= rows_per_effort_dm:
                sel = candidates
            else:
                sel = candidates[np.random.choice(len(candidates),
                                                 rows_per_effort_dm,
                                                 replace=False)]
            dm_blocks.append(sel)
        dm_block = np.vstack(dm_blocks)

        extra_needed = remaining - len(dm_block)
        replace_flag = extra_needed > n_total_comb
        extra = all_comb[np.random.choice(n_total_comb,
                                           max(0, extra_needed),
                                           replace=replace_flag)]
        cond_er = np.vstack((cond_er, dm_block, extra))

    else:
        # CASE 2: fewer total trials than all combinations
        cond_er = all_comb.copy()
        # balanced selection for decision trials
        rep_per_effort = int(np.ceil(n_trials / len(eff_proposed)))
        dm_selected = []
        for level in eff_proposed:
            mask = cond_er[:, 0] == level
            candidates = cond_er[mask]
            if len(candidates) <= rep_per_effort:
                sel = candidates
            else:
                sel = candidates[np.random.choice(len(candidates),
                                                 rep_per_effort,
                                                 replace=False)]
            dm_selected.append(sel)
        cond_er = np.vstack(dm_selected)

        # adjust exact decision trial count
        current_dm = int((cond_er[:, 2] == 0).sum())
        if current_dm < n_trials:
            add_count = n_trials - current_dm
            replace_flag = add_count > n_total_comb
            add = all_comb[np.random.choice(n_total_comb,
                                            add_count,
                                            replace=replace_flag)]
            cond_er = np.vstack((cond_er, add))
        elif current_dm > n_trials:
            dm_idx = np.where(cond_er[:, 2] == 0)[0]
            remove_idx = np.random.choice(dm_idx,
                                          current_dm - n_trials,
                                          replace=False)
            cond_er = np.delete(cond_er, remove_idx, axis=0)

        # select EP within cond_er
        rep_per_effort_ep = int(np.ceil(n_effort_trials / len(eff_proposed)))
        ep_selected = []
        for level in eff_proposed:
            mask = cond_er[:, 0] == level
            candidates = cond_er[mask]
            if len(candidates) <= rep_per_effort_ep:
                sel = candidates
            else:
                sel = candidates[np.random.choice(len(candidates),
                                                 rep_per_effort_ep,
                                                 replace=False)]
            ep_selected.append(sel)
        sel_ep = np.vstack(ep_selected)
        # mark EP flags
        for r in sel_ep:
            match = np.all(cond_er[:, :2] == r[:2], axis=1)
            cond_er[match, 2] = 1

        # adjust exact EP count
        current_ep = int((cond_er[:, 2] == 1).sum())
        if current_ep < n_effort_trials:
            need = n_effort_trials - current_ep
            zeros_idx = np.where(cond_er[:, 2] == 0)[0]
            switch_idx = np.random.choice(zeros_idx,
                                          need,
                                          replace=False)
            cond_er[switch_idx, 2] = 1
        elif current_ep > n_effort_trials:
            ones_idx = np.where(cond_er[:, 2] == 1)[0]
            switch_idx = np.random.choice(ones_idx,
                                          current_ep - n_effort_trials,
                                          replace=False)
            cond_er[switch_idx, 2] = 0

    # Final shuffle and indices extraction
    np.random.shuffle(cond_er)
    indx_effort_trials = np.where(cond_er[:, 2] == 1)[0]

    # Integrity checks
    assert len(indx_effort_trials) == n_effort_trials, \
        f"Expected {n_effort_trials} EP trials, got {len(indx_effort_trials)}"
    assert cond_er.shape[0] == n_trials, \
        f"Expected total {n_trials} trials, got {cond_er.shape[0]}"

    return cond_er, indx_effort_trials
