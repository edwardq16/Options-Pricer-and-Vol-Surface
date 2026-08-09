import yfinance as yf
import numpy as np
from datetime import date
import streamlit as st
from implied_volatility import implied_vol

@st.cache_data
def get_option_chain(symbol, expiry):
    ticker = yf.Ticker(symbol)
    chain = ticker.option_chain(expiry)
    S = ticker.fast_info['lastPrice']
    T = (date.fromisoformat(expiry) - date.today()).days / 365
    return chain.calls, chain.puts, S, T

@st.cache_data
def get_expiries(symbol):
    ticker = yf.Ticker(symbol)
    return ticker.options

@st.cache_data
def get_rfr():
    irx = yf.Ticker("^IRX")
    r = irx.fast_info['lastPrice'] / 100
    return r

@st.cache_data
def get_div_yield(symbol):
    ticker = yf.Ticker(symbol)
    q = (ticker.info.get("dividendYield", 0.0))/100
    if q == None:
        return 0.0
    else:
        return q

def clean_chain(df, max_rel_spread=0.25):
    df = df[(df["bid"] > 0) & (df["ask"] > 0) & (df["ask"] >= df["bid"])]
    df["mid"] = (df["bid"] + df["ask"]) / 2
    df = df[(df["ask"] - df["bid"]) / df["mid"] <= max_rel_spread]
    df = df[(df["volume"].fillna(0) > 0) & (df["openInterest"].fillna(0) > 0)]
    return df

@st.cache_data
def solve_iv_smile(calls, puts, S, T, r, vol_0=0.2, q=0.0):
    filtered_calls = clean_chain(calls)
    filtered_calls = filtered_calls[filtered_calls["strike"] > S]
    filtered_puts = clean_chain(puts)
    filtered_puts = filtered_puts[filtered_puts["strike"] < S]
    iv_data = {}
    mid_data = {}

    for index, row in filtered_calls.iterrows():
        K = row["strike"]
        C_mkt = row["mid"]
        iv_data[K] = implied_vol(S, K, T, r, vol_0, C_mkt, "call", q=q)
        mid_data[K] = C_mkt

    for index, row in filtered_puts.iterrows():
        K = row["strike"]
        P_mkt = row["mid"]
        iv_data[K] = implied_vol(S, K, T, r, vol_0, P_mkt, "put", q=q)
        mid_data[K] = P_mkt

    solved = {K: iv for K, iv in iv_data.items() if not np.isnan(iv)}
    K_atm = min(solved, key=lambda K: abs(K - S))
    iv_atm = solved[K_atm]
    z = 3.0
    half_width = z * iv_atm * np.sqrt(T)
    clean_iv_data = {K: iv for K, iv in solved.items() if abs(np.log(K / S)) <= half_width}
    clean_mid_data = {}
    for K in clean_iv_data:
        clean_mid_data[K] = mid_data[K]
    return clean_iv_data, clean_mid_data