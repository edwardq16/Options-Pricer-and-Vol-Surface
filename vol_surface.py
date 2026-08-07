import numpy as np
from scipy.interpolate import CubicSpline
from scipy.optimize import curve_fit
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from market_data import get_option_chain, get_expiries, solve_iv_smile, get_rfr

def svi(k, a, b, rho, m, sigma):
    return a + b * (rho * (k - m) + np.sqrt((k - m)**2 + sigma**2))

@st.cache_resource
def fit_smile(strikes, ivs, S, T):
    k = np.log(strikes / S)
    w = (ivs ** 2) * T
    bounds = ([-np.inf, 0, -0.999, -np.inf, 1e-6], [np.inf, np.inf, 0.999, np.inf, np.inf])
    params, _ = curve_fit(svi, k, w, p0=[np.mean(w), 0.1, 0.0, 0.0, 0.1], bounds=bounds, maxfev=10000)
    def smile(K):
        k = np.log(K/S)
        a, b, rho, m, sigma = params
        w = svi(k, a, b, rho, m, sigma)
        iv = np.sqrt(w/T)
        return iv
    return smile

@st.cache_data
def build_vol_surface(symbol, r, option_type, n_expiries=10):
    expiries = get_expiries(symbol)
    all_dfs = []
    for n in range(n_expiries):
        calls, puts, S, T = get_option_chain(symbol, expiries[n])
        clean_call_data, clean_put_data = solve_iv_smile(calls, puts, S, T, r)
        if len(clean_call_data) < 2 or len(clean_put_data) < 2:
            continue
        if option_type == 'Call':
            strikes = np.array(list(clean_call_data.keys()))
            ivs = np.array(list(clean_call_data.values()))
        else:
            strikes = np.array(list(clean_put_data.keys()))
            ivs = np.array(list(clean_put_data.values()))
        df = pd.DataFrame({
            'K': strikes,
            'IV': ivs,
            'T': T
        })
        all_dfs.append(df)
    return pd.concat(all_dfs)