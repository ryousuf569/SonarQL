import numpy as np

def monte_carlo_sim(df, indicator, threshold, n_sims, 
                    horizon=100, band=None, min_samples=50, 
                    p_hack=True, band_multipliers=(0.5, 1.0, 1.5, 2.0)):
    df = df.copy()

    df["Target"] = np.log(df["Adj_Close"].shift(-5) / df["Adj_Close"])
    df = df.dropna()

    # latest indicator value
    try:
        baseline_value = df[indicator].iloc[-1]
    except KeyError:
        return None

    shocked_value = baseline_value + threshold

    band = max(0.25 * df[indicator].std(), 1e-6)

    def sim(band):

        # match historical periods where indicator ~ shocked value
        mask = (
            (df[indicator] >= shocked_value - band) &
            (df[indicator] <= shocked_value + band)
        )

        # returns future returns following similar indicator levels
        cond_returns = df.loc[mask, "Target"]

        if len(cond_returns) < min_samples:
            return None, None, cond_returns

        simulated_returns = np.zeros(n_sims)

        for i in range(n_sims):
            sampled = np.random.choice(cond_returns, size=horizon, replace=True)
            simulated_returns[i] = sampled.sum()

        # convert log-returns to % price change
        simulated_pct_change = np.exp(simulated_returns) - 1

        p_val = 2 * min(np.mean(simulated_pct_change <= 0), np.mean(simulated_pct_change >= 0))

        return simulated_pct_change, p_val, cond_returns
    
    simulated_pct_change, p, cond_returns = sim(band=band)

    if simulated_pct_change is None:
        raise ValueError(f"Not enough samples for simulation "
                         f"(got {len(cond_returns)}, need {min_samples})."
                         "Try widening the band or extending the date range.")
    
    p_hack = p
    p_hack_band = band

    # p-hacking sim
    # runs sim on multiple band values and returns a p_hack result
    # modified or unmodified
    if p_hack:
        for m in band_multipliers:
            pct, p, cond_returns = sim(band * m)
            if pct is None:
                continue
            if p < p_hack:
                p_hack = p
                p_hack_band = band * m

    # “this looks significant but only after searching”
    dangerous = (p_hack and p_hack < 0.05 and len(band_multipliers) > 1)
    
    return {
        "mean_pct_change": float(simulated_pct_change.mean()),
        "median_pct_change": float(np.median(simulated_pct_change)),
        "p5": float(np.percentile(simulated_pct_change, 5)),
        "p95": float(np.percentile(simulated_pct_change, 95)),
        "n_sims": n_sims,
        "sample_size": int(len(cond_returns)),
        "baseline_indicator": float(baseline_value),
        "shocked_indicator": float(shocked_value),
        "band_used": float(band),
        "p_value": float(p),
        "p_hacked_p_value": float(p_hack),
        "p_hacked_band": float(p_hack_band),
        "dangerous": bool(dangerous)
    }