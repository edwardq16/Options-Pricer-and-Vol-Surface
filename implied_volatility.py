from black_scholes import bs_euro_call, bs_euro_put, vega
import numpy as np

def implied_vol_call(S, K, T, r, vol_0, C_mkt, tol=1e-6, max_iter=500, vfloor=1e-6):
    vcheck = vega(S, K, T, r, vol_0)
    if vcheck < vfloor:
        return np.nan
    else:
        vol_old = vol_0
        count = 0
        BS_vol_n = bs_euro_call(S, K, T, r, vol_old)
        while abs(BS_vol_n  - C_mkt) > tol and count < max_iter:
            vol_impl = vol_old - (BS_vol_n - C_mkt)/vega(S, K, T, r, vol_old)
            vcheck = vega(S, K, T, r, vol_impl)
            if vcheck < vfloor or vol_impl < 0:
                return np.nan
            else:
                vol_old = vol_impl
                count += 1
                BS_vol_n = bs_euro_call(S, K, T, r, vol_old)

        vol_impl = vol_old
        return vol_impl

def implied_vol_put(S, K, T, r, vol_0, P_mkt, tol=1e-6, max_iter=500, vfloor=1e-6):
    vcheck = vega(S, K, T, r, vol_0)
    if vcheck < vfloor:
        return np.nan
    else:
        vol_old = vol_0
        count = 0
        BS_vol_n = bs_euro_put(S, K, T, r, vol_old)
        while abs(BS_vol_n  - P_mkt) > tol and count < max_iter:
            vol_impl = vol_old - (BS_vol_n - P_mkt)/vega(S, K, T, r, vol_old)
            vcheck = vega(S, K, T, r, vol_impl)
            if vcheck < vfloor or vol_impl < 0:
                return np.nan
            else:
                vol_old = vol_impl
                count += 1
                BS_vol_n = bs_euro_put(S, K, T, r, vol_old)

        vol_impl = vol_old
        return vol_impl