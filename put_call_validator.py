import numpy as np
from black_scholes import bs_euro_call, bs_euro_put
from market_data import get_option_chain, get_rfr, get_div_yield, clean_chain

def pc_parity(n=10_000, seed=0):
    rng = np.random.default_rng(seed)
    S   = rng.uniform(50, 200, n)
    K   = rng.uniform(50, 200, n)
    T   = rng.uniform(0.01, 2.0, n)
    r   = rng.uniform(0.0, 0.08, n)
    q = rng.uniform(0, 0.05, n)
    vol = rng.uniform(0.05, 1.0, n)
    lhs = bs_euro_call(S, K, T, r, vol, q) - bs_euro_put(S, K, T, r, vol, q)
    rhs = S * np.exp(-q * T) - K * np.exp(-r * T)
    abs_error = np.abs(lhs - rhs)
    return abs_error.max(), (abs_error / S).max()

def market_parity(symbol, expiry):
    calls, puts, S, T = get_option_chain(symbol, expiry)
    r = get_rfr()
    c = clean_chain(calls)[["strike", "mid"]]
    c["C_mid"] = c["mid"]
    p = clean_chain(puts)[["strike", "mid"]]
    p["P_mid"] = p["mid"]
    grouped_strikes = c.merge(p, on="strike")

    grouped_strikes["deviation"] = (grouped_strikes["C_mid"] - grouped_strikes["P_mid"]) - (S - grouped_strikes["strike"] * np.exp(-r * T))
    return grouped_strikes

grouped_strikes = market_parity("AAPL", "2026-09-18")
print(pc_parity())
print(f"Market parity: {len(grouped_strikes)} strike pairs")
print(f"Median deviation: {np.median(grouped_strikes["deviation"])}")
print(f"Mean absolute deviation: {np.mean(grouped_strikes["deviation"].abs())}")
print(get_div_yield("AAPL"))
