def compute_total_gain(trials):

    mask = (
        ((trials['Acceptance'] == 1) & (trials['EffortProduction'].fillna(0) == 0))
        | (
            (trials['Acceptance'] == 1)
            & (trials['EffortProduction'].fillna(0) == 1)
            & (trials['success'].fillna(0) == 1)
        )
    )

    total_gain = trials.loc[mask, "reward"].sum() / 100

    return total_gain