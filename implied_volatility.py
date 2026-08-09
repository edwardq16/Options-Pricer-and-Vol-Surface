from black_scholes import bs_euro_call, bs_euro_put, vega
import numpy as np

from black_scholes import bs_euro_call, bs_euro_put, vega
import numpy as np

def implied_vol(S, K, T, r, vol_0, price_mkt, flag, tol=1e-6, max_iter=500, vfloor=1e-6, q=0.0):
    if flag == "call":
        pricer = bs_euro_call
    else:
        pricer = bs_euro_put
    vcheck = vega(S, K, T, r, vol_0, q)
    if vcheck < vfloor:
        return np.nan
    else:
        vol_old = vol_0
        count = 0
        BS_vol_n = pricer(S, K, T, r, vol_old, q)
        while abs(BS_vol_n - price_mkt) > tol and count < max_iter:
            vol_impl = vol_old - (BS_vol_n - price_mkt)/vega(S, K, T, r, vol_old, q)
            vcheck = vega(S, K, T, r, vol_impl, q)
            if vcheck < vfloor or vol_impl < 0:
                return np.nan
            else:
                vol_old = vol_impl
                count += 1
                BS_vol_n = pricer(S, K, T, r, vol_old, q)

        vol_impl = vol_old
        return vol_impl