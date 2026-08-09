import numpy as np
from scipy.interpolate import CubicSpline
from scipy.optimize import curve_fit
from datetime import date
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from market_data import get_option_chain, get_expiries, solve_iv_smile, get_rfr
from black_scholes import vega

def svi(k, a, b, rho, m, sigma):
    return a + b * (rho * (k - m) + np.sqrt((k - m)**2 + sigma**2))

@st.cache_resource
def fit_smile(strikes, ivs, S, T, r, q=0.0):
    k = np.log(strikes / S)
    w = (ivs ** 2) * T
    vegas = vega(S, strikes, T, r, ivs, q)
    bounds = ([-np.inf, 0, -0.999, -np.inf, 1e-6], [np.inf, np.inf, 0.999, np.inf, np.inf])
    params, _ = curve_fit(svi, k, w, p0=[np.mean(w), 0.1, 0.0, 0.0, 0.1], bounds=bounds, sigma=1/np.maximum(vegas/(2*ivs*T), 1e-8), maxfev=10000)
    iv_fit = np.sqrt(svi(k, *params) / T)
    resid = iv_fit - ivs
    rmse = np.sqrt(np.mean(resid ** 2)) * 100
    wrmse = np.sqrt(np.sum(vegas * resid ** 2) / np.sum(vegas)) * 100
    print(f"T={T:.3f}  n={len(k)}  rmse={rmse:.2f}  wrmse={wrmse:.2f}  vol pts")
    print(vegas.min(), vegas.max(), vegas.min()/vegas.max())
    def smile(K):
        k = np.log(K/S)
        a, b, rho, m, sigma = params
        w = svi(k, a, b, rho, m, sigma)
        iv = np.sqrt(w/T)
        return iv
    return smile

@st.cache_data
def build_vol_surface(symbol, r, n_expiries=10, q=0.0):
    expiries = get_expiries(symbol)
    expiries = [e for e in expiries if (date.fromisoformat(e) - date.today()).days > 7]
    all_dfs = []
    for expiry in expiries[:n_expiries]:
        calls, puts, S, T = get_option_chain(symbol, expiry)
        clean_iv_data, _ = solve_iv_smile(calls, puts, S, T, r, q=q)
        if len(clean_iv_data) < 8:
            continue
        strikes = np.array(list(clean_iv_data.keys()))
        ivs = np.array(list(clean_iv_data.values()))
        df = pd.DataFrame({
            'K': strikes,
            'IV': ivs,
            'T': T
        })
        all_dfs.append(df)
    return pd.concat(all_dfs)